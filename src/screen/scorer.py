"""Rank stocks by relative cheapness vs sector peers."""

from __future__ import annotations

import statistics
from typing import Any

from src.models.candidate import ScoredCandidate, StockMetrics


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return statistics.median(values)


def _relative_cheapness(value: float | None, sector_median: float | None) -> float:
    """Higher = cheaper vs sector (value below median is better for PE/PB/PEG)."""
    if value is None or value <= 0.05 or sector_median is None or sector_median <= 0:
        return 0.0
    return min(sector_median / value, 5.0)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _scale(value: float | None, low: float, high: float) -> float:
    if value is None or high <= low:
        return 0.0
    return _clamp((value - low) / (high - low), 0.0, 1.0)


def _ideal_rsi_score(value: float | None) -> float:
    """Prefer constructive RSI, but avoid extremely overbought readings."""
    if value is None:
        return 0.0
    if 45 <= value <= 65:
        return 1.0
    if 35 <= value < 45:
        return 0.7
    if 65 < value <= 75:
        return 0.6
    return 0.2


def _graham_match(pe: float | None, pb: float | None) -> bool:
    return (
        pe is not None
        and pb is not None
        and 0 < pe < 15
        and 0 < pb < 1.5
    )


def _build_sector_medians(rows: list[StockMetrics]) -> dict[str, dict[str, float | None]]:
    by_sector: dict[str, list[StockMetrics]] = {}
    for row in rows:
        by_sector.setdefault(row.sector, []).append(row)

    medians: dict[str, dict[str, float | None]] = {}
    for sector, sector_rows in by_sector.items():
        pes = [r.trailing_pe for r in sector_rows if r.trailing_pe and r.trailing_pe > 0]
        pbs = [
            r.price_to_book
            for r in sector_rows
            if r.price_to_book and r.price_to_book > 0
        ]
        pegs = [r.peg_ratio for r in sector_rows if r.peg_ratio and r.peg_ratio > 0]
        medians[sector] = {
            "trailing_pe": _median(pes),
            "price_to_book": _median(pbs),
            "peg_ratio": _median(pegs),
        }
    return medians


def passes_filters(row: StockMetrics, filters: dict[str, Any]) -> bool:
    min_cap = filters.get("min_market_cap")
    if min_cap and (row.market_cap is None or row.market_cap < min_cap):
        return False

    max_cap = filters.get("max_market_cap")
    if max_cap and row.market_cap is not None and row.market_cap > max_cap:
        return False

    if filters.get("require_positive_trailing_pe") and (
        row.trailing_pe is None or row.trailing_pe <= 0
    ):
        return False

    max_pe = filters.get("max_trailing_pe")
    if max_pe is not None and row.trailing_pe is not None and row.trailing_pe > max_pe:
        return False

    max_pb = filters.get("max_price_to_book")
    if max_pb is not None and row.price_to_book is not None and row.price_to_book > max_pb:
        return False

    if filters.get("require_positive_revenue_growth") and (
        row.revenue_growth is None or row.revenue_growth <= 0
    ):
        return False

    return True


def score_candidates(
    rows: list[StockMetrics],
    *,
    scoring: dict[str, Any],
    filters: dict[str, Any],
) -> list[ScoredCandidate]:
    filtered = [r for r in rows if passes_filters(r, filters)]
    sector_medians = _build_sector_medians(filtered)

    w_pe = float(scoring.get("trailing_pe", 0.45))
    w_pb = float(scoring.get("price_to_book", 0.35))
    w_peg = float(scoring.get("peg_ratio", 0.20))
    graham_bonus = float(scoring.get("graham_bonus", 0.15))

    weight_sum = w_pe + w_pb + w_peg
    if weight_sum <= 0:
        weight_sum = 1.0

    results: list[ScoredCandidate] = []
    for row in filtered:
        med = sector_medians.get(row.sector, {})
        pe_score = _relative_cheapness(row.trailing_pe, med.get("trailing_pe"))
        pb_score = _relative_cheapness(row.price_to_book, med.get("price_to_book"))
        peg_score = _relative_cheapness(row.peg_ratio, med.get("peg_ratio"))

        base = (w_pe * pe_score + w_pb * pb_score + w_peg * peg_score) / weight_sum
        graham = _graham_match(row.trailing_pe, row.price_to_book)
        score = base + (graham_bonus if graham else 0.0)

        reasons: list[str] = []
        if pe_score > 1.05:
            reasons.append("trailing P/E below sector median")
        if pb_score > 1.05:
            reasons.append("P/B below sector median")
        if peg_score > 1.05 and row.peg_ratio is not None:
            reasons.append("PEG below sector median")
        if graham:
            reasons.append("meets classic Graham thresholds (P/E<15, P/B<1.5)")
        if not reasons:
            reasons.append("composite relative-value score")

        results.append(
            ScoredCandidate(
                symbol=row.symbol,
                name=row.name,
                sector=row.sector,
                score=round(score, 4),
                trailing_pe=row.trailing_pe,
                price_to_book=row.price_to_book,
                peg_ratio=row.peg_ratio,
                market_cap=row.market_cap,
                current_price=row.current_price,
                graham_match=graham,
                reasons=reasons,
                return_1d=row.return_1d,
                return_5d=row.return_5d,
                volume_ratio_5d=row.volume_ratio_5d,
                distance_from_5d_high=row.distance_from_5d_high,
                distance_from_5d_low=row.distance_from_5d_low,
                rsi_14=row.rsi_14,
            )
        )

    results.sort(key=lambda c: c.score, reverse=True)
    return results


def score_short_term_candidates(
    rows: list[StockMetrics],
    *,
    scoring: dict[str, Any],
    filters: dict[str, Any],
) -> list[ScoredCandidate]:
    """Rank names for a 1-day to 1-week window using price/volume behavior."""
    filtered = [r for r in rows if passes_filters(r, filters)]

    w_1d = float(scoring.get("return_1d", 0.20))
    w_5d = float(scoring.get("return_5d", 0.25))
    w_volume = float(scoring.get("volume_ratio_5d", 0.18))
    w_volume_20 = float(scoring.get("volume_ratio_20d", 0.10))
    w_high = float(scoring.get("near_5d_high", 0.08))
    w_rsi = float(scoring.get("rsi_14", 0.10))
    w_spy = float(scoring.get("relative_spy_5d", 0.14))
    w_qqq = float(scoring.get("relative_qqq_5d", 0.10))
    w_trend = float(scoring.get("return_20d", 0.05))
    weight_sum = w_1d + w_5d + w_volume + w_volume_20 + w_high + w_rsi + w_spy + w_qqq + w_trend
    if weight_sum <= 0:
        weight_sum = 1.0

    results: list[ScoredCandidate] = []
    for row in filtered:
        if row.return_1d is None or row.return_5d is None:
            continue

        # These ranges favor positive short-term momentum without rewarding
        # extreme one-day spikes too heavily.
        one_day = _scale(row.return_1d, -0.03, 0.04)
        five_day = _scale(row.return_5d, -0.05, 0.10)
        volume = _scale(row.volume_ratio_5d, 0.75, 2.50)
        volume_20 = _scale(row.volume_ratio_20d, 0.80, 2.75)
        near_high = _scale(row.distance_from_5d_high, -0.08, 0.0)
        rsi = _ideal_rsi_score(row.rsi_14)
        relative_spy = _scale(row.rel_strength_spy_5d, -0.03, 0.08)
        relative_qqq = _scale(row.rel_strength_qqq_5d, -0.03, 0.08)
        trend_20d = _scale(row.return_20d, -0.08, 0.18)

        opportunity_score = (
            w_1d * one_day
            + w_5d * five_day
            + w_volume * volume
            + w_volume_20 * volume_20
            + w_high * near_high
            + w_rsi * rsi
            + w_spy * relative_spy
            + w_qqq * relative_qqq
            + w_trend * trend_20d
        ) / weight_sum
        risk_score, risk_flags = _short_term_risk(row)
        confidence_score, expected_direction, reason_codes = _short_term_prediction(
            row,
            opportunity_score,
            risk_score,
        )
        score = 0.75 * opportunity_score + 0.25 * (1 - risk_score)
        setup_type = _setup_type(row, risk_score)

        reasons: list[str] = []
        if row.return_5d is not None and row.return_5d > 0.02:
            reasons.append("positive 5-day momentum")
        if row.return_1d is not None and row.return_1d > 0:
            reasons.append("positive latest session")
        if row.volume_ratio_5d is not None and row.volume_ratio_5d > 1.25:
            reasons.append("volume above recent average")
        if row.volume_ratio_20d is not None and row.volume_ratio_20d > 1.25:
            reasons.append("volume above 20-day average")
        if row.distance_from_5d_high is not None and row.distance_from_5d_high > -0.02:
            reasons.append("trading near 5-day high")
        if row.rsi_14 is not None and 45 <= row.rsi_14 <= 65:
            reasons.append("RSI in constructive range")
        if row.rel_strength_spy_5d is not None and row.rel_strength_spy_5d > 0:
            reasons.append("outperforming SPY over 5 days")
        if row.rel_strength_qqq_5d is not None and row.rel_strength_qqq_5d > 0:
            reasons.append("outperforming QQQ over 5 days")
        if not reasons:
            reasons.append("short-term composite score")

        results.append(
            ScoredCandidate(
                symbol=row.symbol,
                name=row.name,
                sector=row.sector,
                score=round(score, 4),
                trailing_pe=row.trailing_pe,
                price_to_book=row.price_to_book,
                peg_ratio=row.peg_ratio,
                market_cap=row.market_cap,
                current_price=row.current_price,
                graham_match=_graham_match(row.trailing_pe, row.price_to_book),
                reasons=reasons,
                opportunity_score=round(opportunity_score, 4),
                risk_score=round(risk_score, 4),
                setup_type=setup_type,
                risk_flags=risk_flags,
                upcoming_earnings_days=row.upcoming_earnings_days,
                return_1d=row.return_1d,
                return_5d=row.return_5d,
                return_20d=row.return_20d,
                gap_1d=row.gap_1d,
                volume_ratio_5d=row.volume_ratio_5d,
                volume_ratio_20d=row.volume_ratio_20d,
                distance_from_5d_high=row.distance_from_5d_high,
                distance_from_5d_low=row.distance_from_5d_low,
                atr_14_pct=row.atr_14_pct,
                rsi_14=row.rsi_14,
                rel_strength_spy_1d=row.rel_strength_spy_1d,
                rel_strength_spy_5d=row.rel_strength_spy_5d,
                rel_strength_qqq_1d=row.rel_strength_qqq_1d,
                rel_strength_qqq_5d=row.rel_strength_qqq_5d,
                expected_direction=expected_direction,
                expected_window="1d-5d",
                confidence_score=round(confidence_score, 4),
                reason_codes=reason_codes,
            )
        )

    results.sort(key=lambda c: c.score, reverse=True)
    return results


def _short_term_risk(row: StockMetrics) -> tuple[float, list[str]]:
    flags: list[str] = []
    risk = 0.0

    if row.return_1d is not None and row.return_1d > 0.08:
        flags.append("large 1-day move")
        risk += 0.18
    if row.return_5d is not None and row.return_5d > 0.15:
        flags.append("large 5-day move")
        risk += 0.22
    if row.rsi_14 is not None and row.rsi_14 > 70:
        flags.append("RSI above 70")
        risk += 0.18
    if row.volume_ratio_5d is not None and row.volume_ratio_5d > 3.0:
        flags.append("very high 5-day relative volume")
        risk += 0.12
    if row.atr_14_pct is not None and row.atr_14_pct > 0.06:
        flags.append("high ATR volatility")
        risk += 0.12
    if row.gap_1d is not None and abs(row.gap_1d) > 0.05:
        flags.append("large opening gap")
        risk += 0.10
    if (
        row.upcoming_earnings_days is not None
        and 0 <= row.upcoming_earnings_days <= 7
    ):
        flags.append("earnings within 7 days")
        risk += 0.25

    if not flags:
        flags.append("no major short-term risk flags")

    return _clamp(risk, 0.0, 1.0), flags


def _setup_type(row: StockMetrics, risk_score: float) -> str:
    if (
        row.upcoming_earnings_days is not None
        and 0 <= row.upcoming_earnings_days <= 7
    ):
        return "earnings risk"
    if risk_score >= 0.45:
        return "overextended"
    if (
        row.return_5d is not None
        and row.return_5d > 0.02
        and row.rel_strength_spy_5d is not None
        and row.rel_strength_spy_5d > 0
    ):
        if row.distance_from_5d_high is not None and row.distance_from_5d_high > -0.02:
            return "momentum continuation"
        return "relative strength"
    if (
        row.volume_ratio_20d is not None
        and row.volume_ratio_20d > 1.5
        and row.distance_from_5d_high is not None
        and row.distance_from_5d_high > -0.02
    ):
        return "breakout watch"
    return "pullback risk"


def _short_term_prediction(
    row: StockMetrics,
    opportunity_score: float,
    risk_score: float,
) -> tuple[float, str, list[str]]:
    reason_codes: list[str] = []
    if row.return_5d is not None and row.return_5d > 0.02:
        reason_codes.append("MOMENTUM_5D_POSITIVE")
    if row.return_1d is not None and row.return_1d > 0:
        reason_codes.append("LATEST_SESSION_POSITIVE")
    if row.rel_strength_spy_5d is not None and row.rel_strength_spy_5d > 0:
        reason_codes.append("OUTPERFORMS_SPY_5D")
    if row.rel_strength_qqq_5d is not None and row.rel_strength_qqq_5d > 0:
        reason_codes.append("OUTPERFORMS_QQQ_5D")
    if row.volume_ratio_5d is not None and row.volume_ratio_5d > 1.25:
        reason_codes.append("VOLUME_5D_ABOVE_AVERAGE")
    if row.volume_ratio_20d is not None and row.volume_ratio_20d > 1.25:
        reason_codes.append("VOLUME_20D_ABOVE_AVERAGE")
    if row.distance_from_5d_high is not None and row.distance_from_5d_high > -0.02:
        reason_codes.append("NEAR_5D_HIGH")
    if row.rsi_14 is not None and 45 <= row.rsi_14 <= 65:
        reason_codes.append("RSI_CONSTRUCTIVE")

    confidence = _clamp(0.60 * opportunity_score + 0.40 * (1 - risk_score), 0.0, 1.0)
    if confidence >= 0.70 and opportunity_score >= 0.65 and risk_score < 0.45:
        expected_direction = "up"
    elif risk_score >= 0.45:
        expected_direction = "mixed/high-risk"
    else:
        expected_direction = "neutral/watch"

    if not reason_codes:
        reason_codes.append("COMPOSITE_SCORE")

    return confidence, expected_direction, reason_codes
