"""Fetch fundamentals for US tickers via Yahoo Finance (free)."""

from __future__ import annotations

from datetime import datetime, timezone
import time
from typing import Callable, Iterable

import requests

from src.data.network import configure_ssl
from src.models.candidate import StockMetrics

# Configure SSL / Yahoo backend before yfinance is imported.
configure_ssl()

import yfinance as yf  # noqa: E402
from yfinance.data import YfData  # noqa: E402

BATCH_SIZE = 80
MAX_RETRIES = 5


def init_yfinance_session(*, insecure_ssl: bool = False) -> YfData:
    configure_ssl(insecure=insecure_ssl)
    return YfData()


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result:  # NaN
        return None
    return result


def _earnings_days(value: object) -> float | None:
    timestamp = _safe_float(value)
    if timestamp is None:
        return None
    now = datetime.now(timezone.utc).timestamp()
    return (timestamp - now) / 86_400


def load_demo_metrics(path) -> list[StockMetrics]:
    import json
    from pathlib import Path

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        StockMetrics(
            symbol=row["symbol"],
            name=row["name"],
            sector=row["sector"],
            industry=row.get("industry", "Unknown"),
            market_cap=row.get("market_cap"),
            trailing_pe=row.get("trailing_pe"),
            forward_pe=row.get("forward_pe"),
            price_to_book=row.get("price_to_book"),
            peg_ratio=row.get("peg_ratio"),
            revenue_growth=row.get("revenue_growth"),
            debt_to_equity=row.get("debt_to_equity"),
            free_cashflow=row.get("free_cashflow"),
            current_price=row.get("current_price"),
            upcoming_earnings_days=row.get("upcoming_earnings_days"),
        )
        for row in payload
    ]


def _quote_item_to_metrics(item: dict) -> StockMetrics | None:
    symbol = item.get("symbol")
    if not symbol:
        return None

    quote_type = item.get("quoteType")
    if quote_type not in (None, "EQUITY"):
        return None

    name = str(item.get("longName") or item.get("shortName") or symbol)
    sector = str(item.get("sector") or "Unknown")
    industry = str(item.get("industry") or "Unknown")

    price = _safe_float(item.get("regularMarketPrice"))
    book_value = _safe_float(item.get("bookValue"))
    price_to_book = _safe_float(item.get("priceToBook"))
    if price_to_book is None and price and book_value and book_value > 0:
        price_to_book = price / book_value

    return StockMetrics(
        symbol=str(symbol),
        name=name,
        sector=sector,
        industry=industry,
        market_cap=_safe_float(item.get("marketCap")),
        trailing_pe=_safe_float(item.get("trailingPE")),
        forward_pe=_safe_float(item.get("forwardPE")),
        price_to_book=price_to_book,
        peg_ratio=_safe_float(item.get("pegRatio")),
        revenue_growth=_safe_float(item.get("revenueGrowth")),
        debt_to_equity=_safe_float(item.get("debtToEquity")),
        free_cashflow=None,
        current_price=price,
        upcoming_earnings_days=_earnings_days(
            item.get("earningsTimestamp") or item.get("earningsTimestampStart")
        ),
    )


def _fetch_quote_batch(symbols: list[str]) -> list[StockMetrics]:
    data = YfData()
    params = {"symbols": ",".join(symbols), "formatted": "false"}

    for attempt in range(MAX_RETRIES):
        try:
            payload = data.get_raw_json(
                "https://query1.finance.yahoo.com/v7/finance/quote?",
                params=params,
            )
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 429:
                time.sleep(min(90, 8 * (2**attempt)))
                continue
            return []
        except Exception:
            return []

        results = payload.get("quoteResponse", {}).get("result") or []
        rows: list[StockMetrics] = []
        for item in results:
            metrics = _quote_item_to_metrics(item)
            if metrics is not None:
                rows.append(metrics)
        return rows

    return []


def fetch_metrics(symbol: str) -> StockMetrics | None:
    """Single-symbol fallback (uses quoteSummary; slower)."""
    rows = _fetch_quote_batch([symbol])
    if rows:
        return rows[0]

    try:
        info = yf.Ticker(symbol).info or {}
    except Exception:
        return None

    if not info:
        return None
    quote_type = info.get("quoteType")
    if quote_type not in (None, "EQUITY"):
        return None

    name = str(info.get("longName") or info.get("shortName") or symbol)
    sector = str(info.get("sector") or "Unknown")
    industry = str(info.get("industry") or "Unknown")

    return StockMetrics(
        symbol=symbol,
        name=name,
        sector=sector,
        industry=industry,
        market_cap=_safe_float(info.get("marketCap")),
        trailing_pe=_safe_float(info.get("trailingPE")),
        forward_pe=_safe_float(info.get("forwardPE")),
        price_to_book=_safe_float(info.get("priceToBook")),
        peg_ratio=_safe_float(info.get("pegRatio")),
        revenue_growth=_safe_float(info.get("revenueGrowth")),
        debt_to_equity=_safe_float(info.get("debtToEquity")),
        free_cashflow=_safe_float(info.get("freeCashflow")),
        current_price=_safe_float(
            info.get("currentPrice") or info.get("regularMarketPrice")
        ),
        upcoming_earnings_days=_earnings_days(
            info.get("earningsTimestamp") or info.get("earningsTimestampStart")
        ),
    )


def fetch_many(
    symbols: Iterable[str],
    *,
    delay_seconds: float = 1.0,
    on_progress: Callable[[int, int, str, bool], None] | None = None,
) -> list[StockMetrics]:
    symbol_list = list(symbols)
    total = len(symbol_list)
    rows: list[StockMetrics] = []
    done = 0

    init_yfinance_session()

    for start in range(0, total, BATCH_SIZE):
        batch = symbol_list[start : start + BATCH_SIZE]
        batch_rows = _fetch_quote_batch(batch)
        found = {row.symbol for row in batch_rows}
        rows.extend(batch_rows)

        for symbol in batch:
            done += 1
            if on_progress is not None:
                on_progress(done, total, symbol, symbol in found)

        if delay_seconds > 0 and start + BATCH_SIZE < total:
            time.sleep(delay_seconds)

    return rows
