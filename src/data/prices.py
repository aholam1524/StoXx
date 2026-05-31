"""Short-term price and volume indicators for 1-day to 1-week screens."""

from __future__ import annotations

import math

import pandas as pd

from src.data.network import configure_ssl
from src.models.candidate import StockMetrics

configure_ssl()

import yfinance as yf  # noqa: E402

BENCHMARKS = ("SPY", "QQQ")


def _liquidity_tier(dollar_volume: float | None) -> str | None:
    if dollar_volume is None:
        return None
    if dollar_volume >= 200_000_000:
        return "high"
    if dollar_volume >= 50_000_000:
        return "medium"
    if dollar_volume >= 10_000_000:
        return "low"
    return "thin"


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result):
        return None
    return result


def _rsi(closes: pd.Series, window: int = 14) -> float | None:
    changes = closes.diff().dropna()
    if len(changes) < window:
        return None

    gains = changes.clip(lower=0).tail(window).mean()
    losses = -changes.clip(upper=0).tail(window).mean()
    if losses == 0:
        return 100.0 if gains > 0 else None

    rs = gains / losses
    return _safe_float(100 - (100 / (1 + rs)))


def _return(closes: pd.Series, periods: int) -> float | None:
    if len(closes) <= periods:
        return None
    latest = _safe_float(closes.iloc[-1])
    previous = _safe_float(closes.iloc[-periods - 1])
    if latest is None or previous is None or previous <= 0:
        return None
    return latest / previous - 1


def _close_location(close: float | None, low: float | None, high: float | None) -> float | None:
    if close is None or low is None or high is None or high <= low:
        return None
    return _safe_float((close - low) / (high - low))


def _up_day_ratio(closes: pd.Series, window: int) -> float | None:
    changes = closes.diff().dropna().tail(window)
    if len(changes) < window:
        return None
    return _safe_float((changes > 0).sum() / window)


def _up_volume_ratio(closes: pd.Series, volumes: pd.Series, window: int = 10) -> float | None:
    if len(closes) < window + 1 or len(volumes) < window + 1:
        return None
    recent_closes = closes.tail(window + 1)
    recent_volumes = volumes.reindex(recent_closes.index).tail(window)
    changes = recent_closes.diff().dropna().tail(window)
    up_volume = recent_volumes[changes > 0].sum()
    down_volume = recent_volumes[changes <= 0].sum()
    if down_volume <= 0:
        return _safe_float(5.0 if up_volume > 0 else None)
    return _safe_float(up_volume / down_volume)


def _atr_pct(frame: pd.DataFrame, window: int = 14) -> float | None:
    if len(frame) < window + 1 or not {"High", "Low", "Close"}.issubset(frame.columns):
        return None
    highs = frame["High"].astype(float)
    lows = frame["Low"].astype(float)
    closes = frame["Close"].astype(float)
    previous_close = closes.shift(1)
    true_range = pd.concat(
        [
            highs - lows,
            (highs - previous_close).abs(),
            (lows - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = _safe_float(true_range.tail(window).mean())
    latest_close = _safe_float(closes.iloc[-1])
    if atr is None or latest_close is None or latest_close <= 0:
        return None
    return atr / latest_close


def _symbol_frame(history: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if isinstance(history.columns, pd.MultiIndex):
        if symbol not in history.columns.get_level_values(1):
            return pd.DataFrame()
        return history.xs(symbol, axis=1, level=1).dropna(how="all")
    return history.dropna(how="all")


def _scale(value: float | None, low: float, high: float) -> float | None:
    if value is None or high <= low:
        return None
    return max(0.0, min(1.0, (value - low) / (high - low)))


def _market_regime_score(benchmark_returns: dict[str, dict[str, float | None]], history: pd.DataFrame) -> tuple[float | None, str | None]:
    scores: list[float] = []
    for benchmark in BENCHMARKS:
        returns = benchmark_returns.get(benchmark, {})
        score_5d = _scale(returns.get("5d"), -0.02, 0.03)
        score_20d = _scale(returns.get("20d"), -0.05, 0.06)
        if score_5d is not None:
            scores.append(score_5d)
        if score_20d is not None:
            scores.append(score_20d)

        frame = _symbol_frame(history, benchmark)
        if not frame.empty and "Close" in frame and len(frame) >= 20:
            closes = frame["Close"].dropna().astype(float)
            latest = _safe_float(closes.iloc[-1])
            sma_20 = _safe_float(closes.tail(20).mean())
            if latest is not None and sma_20 is not None and sma_20 > 0:
                close_vs_sma = latest / sma_20 - 1
                sma_score = _scale(close_vs_sma, -0.03, 0.04)
                if sma_score is not None:
                    scores.append(sma_score)

    if not scores:
        return None, None
    score = _safe_float(sum(scores) / len(scores))
    if score is None:
        return None, None
    if score >= 0.65:
        return score, "supportive"
    if score >= 0.40:
        return score, "mixed"
    return score, "weak"


def enrich_short_term_metrics(
    rows: list[StockMetrics],
    *,
    period: str = "3mo",
) -> list[StockMetrics]:
    """Attach recent return, volume, range, and RSI metrics to fetched rows."""
    if not rows:
        return rows

    symbols = [row.symbol for row in rows]
    download_symbols = sorted(set(symbols + list(BENCHMARKS)))
    history = yf.download(
        download_symbols,
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    if history.empty:
        return rows

    benchmark_returns: dict[str, dict[str, float | None]] = {}
    for benchmark in BENCHMARKS:
        frame = _symbol_frame(history, benchmark)
        if frame.empty or "Close" not in frame:
            benchmark_returns[benchmark] = {
                "1d": None,
                "5d": None,
                "10d": None,
                "20d": None,
            }
            continue
        closes = frame.dropna(subset=["Close"])["Close"].astype(float)
        benchmark_returns[benchmark] = {
            "1d": _return(closes, 1),
            "5d": _return(closes, 5),
            "10d": _return(closes, 10),
            "20d": _return(closes, 20),
        }

    market_regime_score, market_regime_label = _market_regime_score(benchmark_returns, history)

    by_symbol = {row.symbol: row for row in rows}
    for symbol, row in by_symbol.items():
        frame = _symbol_frame(history, symbol)
        if frame.empty or "Close" not in frame or "Volume" not in frame:
            continue

        frame = frame.dropna(subset=["Close"])
        if len(frame) < 6:
            continue

        closes = frame["Close"].astype(float)
        volumes = frame["Volume"].dropna().astype(float)
        latest_close = _safe_float(closes.iloc[-1])
        previous_close = _safe_float(closes.iloc[-2])
        latest_open = _safe_float(frame["Open"].iloc[-1]) if "Open" in frame else None
        latest_high = _safe_float(frame["High"].iloc[-1]) if "High" in frame else None
        latest_low = _safe_float(frame["Low"].iloc[-1]) if "Low" in frame else None
        close_5d_ago = _safe_float(closes.iloc[-6])
        close_10d_ago = _safe_float(closes.iloc[-11]) if len(closes) >= 11 else None
        close_20d_ago = _safe_float(closes.iloc[-21]) if len(closes) >= 21 else None

        if latest_close is not None and previous_close is not None and previous_close > 0:
            row.return_1d = latest_close / previous_close - 1
        if latest_open is not None and previous_close is not None and previous_close > 0:
            row.gap_1d = latest_open / previous_close - 1
        if latest_close is not None and close_5d_ago is not None and close_5d_ago > 0:
            row.return_5d = latest_close / close_5d_ago - 1
        if latest_close is not None and close_10d_ago is not None and close_10d_ago > 0:
            row.return_10d = latest_close / close_10d_ago - 1
        if latest_close is not None and close_20d_ago is not None and close_20d_ago > 0:
            row.return_20d = latest_close / close_20d_ago - 1

        latest_volume = _safe_float(volumes.iloc[-1]) if len(volumes) else None
        avg_volume_5 = None
        avg_volume_20 = None
        if len(volumes) >= 6:
            avg_volume_5 = _safe_float(volumes.iloc[-6:-1].mean())
            if latest_volume is not None and avg_volume_5 is not None and avg_volume_5 > 0:
                row.volume_ratio_5d = latest_volume / avg_volume_5
        if len(volumes) >= 21:
            trailing_20 = volumes.iloc[-21:-1]
            avg_volume_20 = _safe_float(trailing_20.mean())
            if latest_volume is not None and avg_volume_20 is not None and avg_volume_20 > 0:
                row.volume_ratio_20d = latest_volume / avg_volume_20
                volume_std_20 = _safe_float(trailing_20.std())
                if volume_std_20 is not None and volume_std_20 > 0:
                    row.volume_z_score_20d = (latest_volume - avg_volume_20) / volume_std_20
            if avg_volume_5 is not None and avg_volume_20 is not None and avg_volume_20 > 0:
                row.volume_trend_5d_20d = avg_volume_5 / avg_volume_20
            if avg_volume_20 is not None and avg_volume_20 > 0:
                recent_5 = volumes.tail(5)
                recent_10 = volumes.tail(10)
                if len(recent_5) == 5:
                    row.volume_persistence_5d = _safe_float((recent_5 > avg_volume_20).sum() / 5)
                if len(recent_10) == 10:
                    row.volume_persistence_10d = _safe_float((recent_10 > avg_volume_20).sum() / 10)
        row.up_volume_ratio_10d = _up_volume_ratio(closes, volumes, 10)
        if latest_close is not None and latest_volume is not None:
            row.dollar_volume = latest_close * latest_volume
            row.liquidity_tier = _liquidity_tier(row.dollar_volume)

        row.close_location_1d = _close_location(latest_close, latest_low, latest_high)
        last_5 = frame.tail(5)
        high_5d = _safe_float(last_5["High"].max()) if "High" in last_5 else None
        low_5d = _safe_float(last_5["Low"].min()) if "Low" in last_5 else None
        if latest_close is not None and high_5d is not None and high_5d > 0:
            row.distance_from_5d_high = latest_close / high_5d - 1
        if latest_close is not None and low_5d is not None and low_5d > 0:
            row.distance_from_5d_low = latest_close / low_5d - 1
        row.close_location_5d = _close_location(latest_close, low_5d, high_5d)

        last_20 = frame.tail(20)
        high_20d = _safe_float(last_20["High"].max()) if "High" in last_20 else None
        low_20d = _safe_float(last_20["Low"].min()) if "Low" in last_20 else None
        if latest_close is not None and high_20d is not None and high_20d > 0:
            row.distance_from_20d_high = latest_close / high_20d - 1
        if latest_close is not None and low_20d is not None and low_20d > 0:
            row.distance_from_20d_low = latest_close / low_20d - 1
        row.close_location_20d = _close_location(latest_close, low_20d, high_20d)

        if len(closes) >= 20:
            sma_5 = _safe_float(closes.tail(5).mean())
            sma_20 = _safe_float(closes.tail(20).mean())
            if sma_5 is not None and sma_20 is not None and sma_20 > 0:
                row.sma_5_20_ratio = sma_5 / sma_20 - 1
            if latest_close is not None and sma_20 is not None and sma_20 > 0:
                row.close_vs_sma_20 = latest_close / sma_20 - 1
        row.up_day_ratio_5d = _up_day_ratio(closes, 5)
        row.up_day_ratio_10d = _up_day_ratio(closes, 10)

        row.rsi_14 = _rsi(closes)
        row.atr_14_pct = _atr_pct(frame)
        row.market_regime_score = market_regime_score
        row.market_regime_label = market_regime_label
        row.failed_gap_or_fade = bool(
            (
                row.gap_1d is not None
                and row.gap_1d >= 0.015
                and row.close_location_1d is not None
                and row.close_location_1d <= 0.40
            )
            or (
                row.return_1d is not None
                and row.return_1d >= 0.025
                and row.close_location_1d is not None
                and row.close_location_1d <= 0.35
            )
        )
        if row.return_1d is not None:
            spy_1d = benchmark_returns.get("SPY", {}).get("1d")
            qqq_1d = benchmark_returns.get("QQQ", {}).get("1d")
            if spy_1d is not None:
                row.rel_strength_spy_1d = row.return_1d - spy_1d
            if qqq_1d is not None:
                row.rel_strength_qqq_1d = row.return_1d - qqq_1d
        if row.return_5d is not None:
            spy_5d = benchmark_returns.get("SPY", {}).get("5d")
            qqq_5d = benchmark_returns.get("QQQ", {}).get("5d")
            if spy_5d is not None:
                row.rel_strength_spy_5d = row.return_5d - spy_5d
            if qqq_5d is not None:
                row.rel_strength_qqq_5d = row.return_5d - qqq_5d
        if row.return_10d is not None:
            spy_10d = benchmark_returns.get("SPY", {}).get("10d")
            qqq_10d = benchmark_returns.get("QQQ", {}).get("10d")
            if spy_10d is not None:
                row.rel_strength_spy_10d = row.return_10d - spy_10d
            if qqq_10d is not None:
                row.rel_strength_qqq_10d = row.return_10d - qqq_10d
        if row.return_20d is not None:
            spy_20d = benchmark_returns.get("SPY", {}).get("20d")
            qqq_20d = benchmark_returns.get("QQQ", {}).get("20d")
            if spy_20d is not None:
                row.rel_strength_spy_20d = row.return_20d - spy_20d
            if qqq_20d is not None:
                row.rel_strength_qqq_20d = row.return_20d - qqq_20d
        row.current_price = latest_close

    sector_returns: dict[str, dict[str, list[float]]] = {}
    for row in rows:
        sector_bucket = sector_returns.setdefault(row.sector, {"5d": [], "10d": [], "20d": []})
        if row.return_5d is not None:
            sector_bucket["5d"].append(row.return_5d)
        if row.return_10d is not None:
            sector_bucket["10d"].append(row.return_10d)
        if row.return_20d is not None:
            sector_bucket["20d"].append(row.return_20d)

    for row in rows:
        sector_bucket = sector_returns.get(row.sector, {})
        if row.return_5d is not None and sector_bucket.get("5d"):
            sector_median = _safe_float(pd.Series(sector_bucket["5d"]).median())
            if sector_median is not None:
                row.sector_relative_strength_5d = row.return_5d - sector_median
        if row.return_10d is not None and sector_bucket.get("10d"):
            sector_median = _safe_float(pd.Series(sector_bucket["10d"]).median())
            if sector_median is not None:
                row.sector_relative_strength_10d = row.return_10d - sector_median
        if row.return_20d is not None and sector_bucket.get("20d"):
            sector_median = _safe_float(pd.Series(sector_bucket["20d"]).median())
            if sector_median is not None:
                row.sector_relative_strength_20d = row.return_20d - sector_median

    return rows
