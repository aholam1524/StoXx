"""Fetch and summarize report-only news context for proposal candidates."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from src.data.network import configure_ssl

configure_ssl()

import yfinance as yf  # noqa: E402

try:  # noqa: SIM105 - optional dependency with graceful fallback.
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore
except Exception:  # pragma: no cover - depends on optional local install state.
    SentimentIntensityAnalyzer = None  # type: ignore

POSITIVE_KEYWORDS = {
    "analyst_upgrade": ("upgrade", "upgraded", "raises rating", "buy rating"),
    "earnings_positive": ("beats estimates", "earnings beat", "tops estimates", "better-than-expected"),
    "guidance_positive": ("raises guidance", "boosts guidance", "raises forecast", "lifts guidance"),
    "deal_or_partnership": ("contract win", "wins contract", "partnership", "collaboration", "deal"),
    "capital_return": ("buyback", "share repurchase", "dividend increase", "raises dividend"),
}

NEGATIVE_KEYWORDS = {
    "analyst_downgrade": ("downgrade", "downgraded", "cuts rating", "sell rating"),
    "earnings_negative": ("misses estimates", "earnings miss", "missed estimates", "disappoints"),
    "guidance_negative": ("cuts guidance", "lowers guidance", "cuts forecast", "warning"),
    "legal_risk": ("lawsuit", "investigation", "probe", "sec charges", "fraud"),
    "offering_or_dilution": ("stock offering", "share offering", "secondary offering", "dilution"),
    "job_cuts": ("layoffs", "job cuts", "restructuring"),
}

_ANALYZER = SentimentIntensityAnalyzer() if SentimentIntensityAnalyzer is not None else None


def _parse_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (OSError, OverflowError, ValueError):
            return None
    if isinstance(value, str):
        for raw in (value, value.replace("Z", "+00:00")):
            try:
                parsed = datetime.fromisoformat(raw)
            except ValueError:
                continue
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
    return None


def _first_url(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        url = value.get("url")
        return str(url) if url else None
    if isinstance(value, list):
        for item in value:
            if url := _first_url(item):
                return url
    return None


def _keyword_flags(text: str) -> tuple[list[str], int, int]:
    lowered = text.lower()
    flags: list[str] = []
    positive_hits = 0
    negative_hits = 0
    for flag, patterns in POSITIVE_KEYWORDS.items():
        if any(pattern in lowered for pattern in patterns):
            flags.append(flag)
            positive_hits += 1
    for flag, patterns in NEGATIVE_KEYWORDS.items():
        if any(pattern in lowered for pattern in patterns):
            flags.append(flag)
            negative_hits += 1
    return flags, positive_hits, negative_hits


def classify_sentiment(text: str) -> dict[str, Any]:
    """Classify headline sentiment with VADER plus finance keyword overrides."""
    flags, positive_hits, negative_hits = _keyword_flags(text)
    compound = 0.0
    if _ANALYZER is not None:
        compound = float(_ANALYZER.polarity_scores(text).get("compound", 0.0))

    if positive_hits and negative_hits:
        sentiment = "mixed"
    elif negative_hits or compound <= -0.20:
        sentiment = "negative"
    elif positive_hits or compound >= 0.20:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "compound": round(compound, 4),
        "flags": flags,
        "positive_keyword_hits": positive_hits,
        "negative_keyword_hits": negative_hits,
        "method": "vader+keywords" if _ANALYZER is not None else "keywords",
    }


def _normalize_news_item(item: dict[str, Any]) -> dict[str, Any] | None:
    content = item.get("content") if isinstance(item.get("content"), dict) else item
    title = str(content.get("title") or "").strip()
    if not title:
        return None

    publisher = (
        content.get("publisher")
        or content.get("provider")
        or content.get("providerDisplayName")
        or content.get("source")
        or item.get("publisher")
        or item.get("provider")
    )
    published_at = _parse_timestamp(
        content.get("providerPublishTime")
        or content.get("pubDate")
        or content.get("displayTime")
        or item.get("providerPublishTime")
    )
    link = (
        _first_url(content.get("clickThroughUrl"))
        or _first_url(content.get("canonicalUrl"))
        or _first_url(content.get("link"))
        or _first_url(item.get("link"))
    )
    sentiment = classify_sentiment(title)
    return {
        "title": title,
        "publisher": str(publisher or "Unknown"),
        "published_at": published_at.isoformat() if published_at else None,
        "link": link,
        "sentiment": sentiment["sentiment"],
        "sentiment_score": sentiment["compound"],
        "flags": sentiment["flags"],
        "sentiment_method": sentiment["method"],
    }


def _summarize_news(symbol: str, headlines: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {
        "positive": sum(1 for item in headlines if item["sentiment"] == "positive"),
        "negative": sum(1 for item in headlines if item["sentiment"] == "negative"),
        "neutral": sum(1 for item in headlines if item["sentiment"] == "neutral"),
        "mixed": sum(1 for item in headlines if item["sentiment"] == "mixed"),
    }
    flags = sorted({flag for item in headlines for flag in item.get("flags", [])})
    if counts["positive"] > counts["negative"] and counts["positive"] >= counts["mixed"]:
        overall = "positive"
    elif counts["negative"] > counts["positive"] and counts["negative"] >= counts["mixed"]:
        overall = "negative"
    elif counts["positive"] or counts["negative"] or counts["mixed"]:
        overall = "mixed"
    else:
        overall = "neutral"
    return {
        "symbol": symbol,
        "status": "ok" if headlines else "unavailable",
        "overall_sentiment": overall if headlines else "unavailable",
        "counts": counts,
        "flags": flags,
        "headlines": headlines,
        "note": "Headline sentiment/context only; not used for ranking or scoring.",
    }


def fetch_symbol_news(
    symbol: str,
    *,
    limit: int = 5,
    days: int | None = 7,
) -> dict[str, Any]:
    """Fetch recent Yahoo Finance news and summarize headline sentiment."""
    try:
        raw_items = yf.Ticker(symbol).news or []
    except Exception as exc:
        return {
            "symbol": symbol,
            "status": "unavailable",
            "overall_sentiment": "unavailable",
            "counts": {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0},
            "flags": [],
            "headlines": [],
            "error": str(exc),
            "note": "News fetch failed; ranking and scoring are unchanged.",
        }

    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=days)
        if days is not None and days > 0
        else None
    )
    headlines: list[dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        normalized = _normalize_news_item(item)
        if normalized is None:
            continue
        if cutoff is not None and normalized.get("published_at"):
            published = _parse_timestamp(normalized["published_at"])
            if published is not None and published < cutoff:
                continue
        headlines.append(normalized)
        if len(headlines) >= limit:
            break

    return _summarize_news(symbol, headlines)
