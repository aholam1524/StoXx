"""Short-term price and volume indicators for 1-day to 1-week screens."""

from __future__ import annotations

import math

import pandas as pd

from src.data.network import configure_ssl
from src.models.candidate import StockMetrics

configure_ssl()

import yfinance as yf  # noqa: E402

BENCHMARKS = ("SPY", "QQQ")


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


def _up_day_ratio(closes: pd.Series, window: int) -> float | None:
    changes = closes.diff().dropna().tail(window)
    if len(changes) < window:
        return None
    return _safe_float((changes > 0).sum() / window)


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
            benchmark_returns[benchmark] = {"1d": None, "5d": None}
            continue
        closes = frame.dropna(subset=["Close"])["Close"].astype(float)
        benchmark_returns[benchmark] = {
            "1d": _return(closes, 1),
            "5d": _return(closes, 5),
        }

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
            avg_volume_20 = _safe_float(volumes.iloc[-21:-1].mean())
            if latest_volume is not None and avg_volume_20 is not None and avg_volume_20 > 0:
                row.volume_ratio_20d = latest_volume / avg_volume_20
            if avg_volume_5 is not None and avg_volume_20 is not None and avg_volume_20 > 0:
                row.volume_trend_5d_20d = avg_volume_5 / avg_volume_20
        if latest_close is not None and latest_volume is not None:
            row.dollar_volume = latest_close * latest_volume

        last_5 = frame.tail(5)
        high_5d = _safe_float(last_5["High"].max()) if "High" in last_5 else None
        low_5d = _safe_float(last_5["Low"].min()) if "Low" in last_5 else None
        if latest_close is not None and high_5d is not None and high_5d > 0:
            row.distance_from_5d_high = latest_close / high_5d - 1
        if latest_close is not None and low_5d is not None and low_5d > 0:
            row.distance_from_5d_low = latest_close / low_5d - 1

        last_20 = frame.tail(20)
        high_20d = _safe_float(last_20["High"].max()) if "High" in last_20 else None
        low_20d = _safe_float(last_20["Low"].min()) if "Low" in last_20 else None
        if latest_close is not None and high_20d is not None and high_20d > 0:
            row.distance_from_20d_high = latest_close / high_20d - 1
        if latest_close is not None and low_20d is not None and low_20d > 0:
            row.distance_from_20d_low = latest_close / low_20d - 1

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
        row.current_price = latest_close

    return rows
