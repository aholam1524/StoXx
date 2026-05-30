"""Short-term price and volume indicators for 1-day to 1-week screens."""

from __future__ import annotations

import math

import pandas as pd

from src.data.network import configure_ssl
from src.models.candidate import StockMetrics

configure_ssl()

import yfinance as yf  # noqa: E402


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


def _symbol_frame(history: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if isinstance(history.columns, pd.MultiIndex):
        if symbol not in history.columns.get_level_values(1):
            return pd.DataFrame()
        return history.xs(symbol, axis=1, level=1).dropna(how="all")
    return history.dropna(how="all")


def enrich_short_term_metrics(
    rows: list[StockMetrics],
    *,
    period: str = "1mo",
) -> list[StockMetrics]:
    """Attach recent return, volume, range, and RSI metrics to fetched rows."""
    if not rows:
        return rows

    symbols = [row.symbol for row in rows]
    history = yf.download(
        symbols,
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    if history.empty:
        return rows

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
        close_5d_ago = _safe_float(closes.iloc[-6])

        if latest_close and previous_close and previous_close > 0:
            row.return_1d = latest_close / previous_close - 1
        if latest_close and close_5d_ago and close_5d_ago > 0:
            row.return_5d = latest_close / close_5d_ago - 1

        if len(volumes) >= 6:
            latest_volume = _safe_float(volumes.iloc[-1])
            avg_volume = _safe_float(volumes.iloc[-6:-1].mean())
            if latest_volume and avg_volume and avg_volume > 0:
                row.volume_ratio_5d = latest_volume / avg_volume

        last_5 = frame.tail(5)
        high_5d = _safe_float(last_5["High"].max()) if "High" in last_5 else None
        low_5d = _safe_float(last_5["Low"].min()) if "Low" in last_5 else None
        if latest_close and high_5d and high_5d > 0:
            row.distance_from_5d_high = latest_close / high_5d - 1
        if latest_close and low_5d and low_5d > 0:
            row.distance_from_5d_low = latest_close / low_5d - 1

        row.rsi_14 = _rsi(closes)
        row.current_price = latest_close

    return rows
