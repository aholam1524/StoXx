"""Rank stocks by relative cheapness vs sector peers."""

from __future__ import annotations

import statistics
from typing import Any

from src.models.candidate import ScoredCandidate, StockMetrics

MIN_SHORT_TERM_RISK = 0.10


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


def _mean_score(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def _weighted_score(scores: dict[str, float], weights: dict[str, float]) -> float:
    weight_sum = sum(weights.values())
    if weight_sum <= 0:
        return 0.0
    return sum(weights[name] * scores.get(name, 0.0) for name in weights) / weight_sum


def _fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def _fmt_num(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def _fmt_money(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value:,.0f}"


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
                market=row.market,
                exchange=row.exchange,
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


def _factor_weights(scoring: dict[str, Any]) -> dict[str, float]:
    factor_weights = scoring.get("factor_weights")
    if isinstance(factor_weights, dict):
        return {
            "trend": float(factor_weights.get("trend", 0.25)),
            "momentum": float(factor_weights.get("momentum", 0.15)),
            "relative_strength": float(factor_weights.get("relative_strength", 0.25)),
            "participation": float(factor_weights.get("participation", 0.20)),
            "extension": float(factor_weights.get("extension", 0.15)),
        }

    # Backward-compatible defaults for older flat signal configs.
    return {
        "trend": (
            float(scoring.get("return_20d", 0.05))
            + float(scoring.get("sma_5_20_ratio", 0.08))
            + float(scoring.get("close_vs_sma_20", 0.06))
            + float(scoring.get("up_day_ratio_5d", 0.07))
            + float(scoring.get("up_day_ratio_10d", 0.05))
            + float(scoring.get("near_5d_high", 0.08))
            + float(scoring.get("near_20d_high", 0.05))
        ),
        "momentum": (
            float(scoring.get("return_1d", 0.20))
            + float(scoring.get("return_5d", 0.25))
            + float(scoring.get("return_10d", 0.10))
        ),
        "relative_strength": (
            float(scoring.get("relative_spy_5d", 0.14))
            + float(scoring.get("relative_qqq_5d", 0.10))
        ),
        "participation": (
            float(scoring.get("volume_ratio_5d", 0.18))
            + float(scoring.get("volume_ratio_20d", 0.10))
            + float(scoring.get("volume_trend_5d_20d", 0.06))
            + float(scoring.get("dollar_volume", 0.04))
        ),
        "extension": float(scoring.get("rsi_14", 0.10)),
    }


FACTOR_COMPONENT_DEFAULTS: dict[str, dict[str, float]] = {
    "trend": {
        "sma_5_20_ratio": 0.30,
        "close_vs_sma_20": 0.25,
        "return_20d": 0.25,
        "up_day_ratio_10d": 0.20,
    },
    "momentum": {
        "return_1d": 0.15,
        "return_5d": 0.30,
        "return_10d": 0.30,
        "return_20d": 0.25,
    },
    "relative_strength": {
        "rel_strength_spy_1d": 0.03,
        "rel_strength_qqq_1d": 0.02,
        "rel_strength_spy_5d": 0.20,
        "rel_strength_qqq_5d": 0.15,
        "rel_strength_spy_10d": 0.25,
        "rel_strength_qqq_10d": 0.15,
        "rel_strength_spy_20d": 0.15,
        "rel_strength_qqq_20d": 0.10,
    },
    "participation": {
        "volume_ratio_5d": 0.20,
        "volume_ratio_20d": 0.20,
        "volume_trend_5d_20d": 0.15,
        "volume_persistence_5d": 0.15,
        "volume_persistence_10d": 0.15,
        "volume_z_score_20d": 0.10,
        "dollar_volume": 0.05,
    },
    "extension": {
        "rsi_control": 0.30,
        "atr_14_pct": 0.25,
        "stretch_vs_atr": 0.20,
        "distance_from_20d_low": 0.15,
        "abs_gap_1d": 0.10,
    },
}

INVERTED_COMPONENTS = {
    "atr_14_pct",
    "stretch_vs_atr",
    "distance_from_20d_low",
    "abs_gap_1d",
}


def _factor_components(scoring: dict[str, Any]) -> dict[str, dict[str, float]]:
    components = {factor: values.copy() for factor, values in FACTOR_COMPONENT_DEFAULTS.items()}
    configured = scoring.get("factor_components")
    if isinstance(configured, dict):
        for factor, values in configured.items():
            if isinstance(values, dict):
                components[str(factor)] = {
                    str(metric): float(weight)
                    for metric, weight in values.items()
                }
    return components


def _component_raw_value(row: StockMetrics, metric: str) -> float | None:
    if metric == "rsi_control":
        return _ideal_rsi_score(row.rsi_14)
    if metric == "stretch_vs_atr":
        if row.atr_14_pct is None or row.atr_14_pct <= 0 or row.return_5d is None:
            return None
        return row.return_5d / row.atr_14_pct
    if metric == "abs_gap_1d":
        return abs(row.gap_1d) if row.gap_1d is not None else None
    value = getattr(row, metric, None)
    return float(value) if isinstance(value, int | float) else None


def _metric_distribution(rows: list[StockMetrics], metric: str) -> dict[str, Any]:
    values = [
        value
        for row in rows
        if (value := _component_raw_value(row, metric)) is not None
    ]
    if not values:
        return {"values": [], "mean": None, "std": None}
    mean = statistics.fmean(values)
    std = statistics.pstdev(values) if len(values) > 1 else 0.0
    return {"values": sorted(values), "mean": mean, "std": std}


def _build_normalization_context(
    rows: list[StockMetrics],
    components: dict[str, dict[str, float]],
) -> dict[str, dict[str, Any]]:
    metrics = sorted({metric for values in components.values() for metric in values})
    return {metric: _metric_distribution(rows, metric) for metric in metrics}


def _percentile_rank(value: float | None, values: list[float]) -> float:
    if value is None or not values:
        return 0.0
    if len(values) == 1:
        return 1.0
    if values[0] == values[-1]:
        return 0.5
    less = sum(1 for item in values if item < value)
    equal = sum(1 for item in values if item == value)
    return _clamp((less + (equal - 1) / 2) / (len(values) - 1), 0.0, 1.0)


def _z_score(value: float | None, distribution: dict[str, Any]) -> float | None:
    std = distribution.get("std")
    mean = distribution.get("mean")
    if value is None or mean is None or std is None or std <= 0:
        return None
    return (value - mean) / std


def _component_details(
    row: StockMetrics,
    factor: str,
    weights: dict[str, float],
    context: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    weight_sum = sum(weights.values()) or 1.0
    details: list[dict[str, Any]] = []
    for metric, weight in weights.items():
        raw_value = _component_raw_value(row, metric)
        distribution = context.get(metric, {"values": [], "mean": None, "std": None})
        percentile = _percentile_rank(raw_value, distribution["values"])
        component_score = 1 - percentile if metric in INVERTED_COMPONENTS else percentile
        normalized_weight = weight / weight_sum
        details.append(
            {
                "factor": factor,
                "metric": metric,
                "weight": round(normalized_weight, 4),
                "raw": raw_value,
                "percentile": round(percentile, 4),
                "z_score": (
                    round(z, 4)
                    if (z := _z_score(raw_value, distribution)) is not None
                    else None
                ),
                "score": round(component_score, 4),
                "contribution": round(normalized_weight * component_score, 4),
                "direction": "lower_is_better" if metric in INVERTED_COMPONENTS else "higher_is_better",
            }
        )
    return details


def _formula_text(details: list[dict[str, Any]]) -> str:
    parts = [
        f"{detail['weight']:.2f} * pct_rank({detail['metric']})"
        for detail in details
        if detail["direction"] == "higher_is_better"
    ]
    parts.extend(
        f"{detail['weight']:.2f} * (1 - pct_rank({detail['metric']}))"
        for detail in details
        if detail["direction"] == "lower_is_better"
    )
    return " + ".join(parts)


def _factor_formula_details(
    row: StockMetrics,
    scoring: dict[str, Any],
    context: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    factor_details: dict[str, dict[str, Any]] = {}
    for factor, weights in _factor_components(scoring).items():
        details = _component_details(row, factor, weights, context)
        score = sum(detail["contribution"] for detail in details)
        factor_details[factor] = {
            "score": round(_clamp(score, 0.0, 1.0), 4),
            "formula": _formula_text(details),
            "components": details,
        }
    return factor_details


def _top_component(details: list[dict[str, Any]], metric: str) -> dict[str, Any] | None:
    return next((detail for detail in details if detail["metric"] == metric), None)


def _factor_summary(factor: str, row: StockMetrics, details: dict[str, Any]) -> str:
    score = details["score"]
    components = details["components"]
    if factor == "trend":
        return (
            f"Trend {score:.2f}: 20D return {_fmt_pct(row.return_20d)} "
            f"(pct {_fmt_num((_top_component(components, 'return_20d') or {}).get('percentile'))}), "
            f"SMA 5/20 {_fmt_pct(row.sma_5_20_ratio)}, close vs SMA20 {_fmt_pct(row.close_vs_sma_20)}."
        )
    if factor == "momentum":
        return (
            f"Momentum {score:.2f}: 1D {_fmt_pct(row.return_1d)}, 5D {_fmt_pct(row.return_5d)}, "
            f"10D {_fmt_pct(row.return_10d)}, 20D {_fmt_pct(row.return_20d)}."
        )
    if factor == "relative_strength":
        windows = [
            ("10D vs SPY", row.rel_strength_spy_10d, "rel_strength_spy_10d"),
            ("20D vs SPY", row.rel_strength_spy_20d, "rel_strength_spy_20d"),
            ("10D vs QQQ", row.rel_strength_qqq_10d, "rel_strength_qqq_10d"),
            ("20D vs QQQ", row.rel_strength_qqq_20d, "rel_strength_qqq_20d"),
            ("5D vs SPY", row.rel_strength_spy_5d, "rel_strength_spy_5d"),
            ("5D vs QQQ", row.rel_strength_qqq_5d, "rel_strength_qqq_5d"),
        ]
        label, value, metric = max(
            (item for item in windows if item[1] is not None),
            key=lambda item: item[1],
            default=("benchmark window", None, ""),
        )
        percentile = (_top_component(components, metric) or {}).get("percentile")
        return (
            f"Relative strength {score:.2f}: strongest window {label} {_fmt_pct(value)} "
            f"(pct {_fmt_num(percentile)}); 5D SPY {_fmt_pct(row.rel_strength_spy_5d)}, "
            f"10D SPY {_fmt_pct(row.rel_strength_spy_10d)}, 20D SPY {_fmt_pct(row.rel_strength_spy_20d)}."
        )
    if factor == "participation":
        persistence = _top_component(components, "volume_persistence_10d") or {}
        return (
            f"Participation {score:.2f}: volume z-score {_fmt_num(row.volume_z_score_20d)}, "
            f"5D persistence {_fmt_pct(row.volume_persistence_5d)}, "
            f"10D persistence {_fmt_pct(row.volume_persistence_10d)} "
            f"(pct {_fmt_num(persistence.get('percentile'))}), "
            f"liquidity tier {row.liquidity_tier or 'n/a'} ({_fmt_money(row.dollar_volume)})."
        )
    return (
        f"Extension control {score:.2f}: RSI {_fmt_num(row.rsi_14)}, "
        f"ATR14 {_fmt_pct(row.atr_14_pct)}, gap {_fmt_pct(row.gap_1d)}, "
        f"20D low distance {_fmt_pct(row.distance_from_20d_low)}."
    )


def _factor_model(
    row: StockMetrics,
    scoring: dict[str, Any],
    context: dict[str, dict[str, Any]],
) -> tuple[float, dict[str, float], list[str], dict[str, Any]]:
    factor_details = _factor_formula_details(row, scoring, context)
    raw_scores = {
        name: details["score"]
        for name, details in factor_details.items()
    }
    factor_scores = {
        name: round(score, 4)
        for name, score in raw_scores.items()
    }
    summaries = [
        _factor_summary(name, row, details)
        for name, details in factor_details.items()
    ]
    opportunity_score = _weighted_score(raw_scores, _factor_weights(scoring))
    return opportunity_score, factor_scores, summaries, factor_details


def _factor_reasons(factor_scores: dict[str, float], risk_score: float, row: StockMetrics) -> list[str]:
    reason_codes: list[str] = []
    if factor_scores.get("trend", 0.0) >= 0.60:
        reason_codes.append("TREND_CONSTRUCTIVE")
    if factor_scores.get("momentum", 0.0) >= 0.60:
        reason_codes.append("MOMENTUM_POSITIVE")
    if factor_scores.get("relative_strength", 0.0) >= 0.60:
        reason_codes.append("RELATIVE_STRENGTH_SUPPORTIVE")
    if factor_scores.get("participation", 0.0) >= 0.60:
        reason_codes.append("PARTICIPATION_EXPANDING")
    if factor_scores.get("extension", 1.0) < 0.50 or risk_score >= 0.45:
        reason_codes.append("EXTENSION_ELEVATED")
    if row.rsi_14 is not None and 45 <= row.rsi_14 <= 65:
        reason_codes.append("RSI_CONSTRUCTIVE")
    elif row.rsi_14 is not None and row.rsi_14 > 70:
        reason_codes.append("RSI_STRETCHED")

    if not reason_codes:
        reason_codes.append("FACTOR_MODEL_MIXED")
    return reason_codes


def _factor_reason_text(factor_scores: dict[str, float]) -> list[str]:
    labels = {
        "trend": "trend factor",
        "momentum": "momentum factor",
        "relative_strength": "relative strength factor",
        "participation": "participation factor",
        "extension": "extension control factor",
    }
    reasons = [
        f"{labels[name]} score {score:.2f}"
        for name, score in factor_scores.items()
        if score >= 0.60
    ]
    return reasons or ["factor model score is mixed"]


def score_short_term_candidates(
    rows: list[StockMetrics],
    *,
    scoring: dict[str, Any],
    filters: dict[str, Any],
) -> list[ScoredCandidate]:
    """Rank names for a 1-day to 1-week window using price/volume behavior."""
    filtered = [r for r in rows if passes_filters(r, filters)]
    components = _factor_components(scoring)
    normalization_context = _build_normalization_context(filtered, components)

    results: list[ScoredCandidate] = []
    for row in filtered:
        if row.return_1d is None or row.return_5d is None:
            continue

        opportunity_score, factor_scores, factor_summaries, factor_details = _factor_model(
            row,
            scoring,
            normalization_context,
        )
        risk_score, risk_flags = _short_term_risk(row)
        risk_level = _risk_level(risk_score)
        confidence_score, expected_direction = _short_term_prediction(
            row,
            opportunity_score,
            risk_score,
        )
        reason_codes = _factor_reasons(factor_scores, risk_score, row)
        score = 0.75 * opportunity_score + 0.25 * (1 - risk_score)
        setup_type = _setup_type(row, risk_score)

        results.append(
            ScoredCandidate(
                symbol=row.symbol,
                name=row.name,
                sector=row.sector,
                market=row.market,
                exchange=row.exchange,
                score=round(score, 4),
                trailing_pe=row.trailing_pe,
                price_to_book=row.price_to_book,
                peg_ratio=row.peg_ratio,
                market_cap=row.market_cap,
                current_price=row.current_price,
                graham_match=_graham_match(row.trailing_pe, row.price_to_book),
                reasons=_factor_reason_text(factor_scores),
                opportunity_score=round(opportunity_score, 4),
                risk_score=round(risk_score, 4),
                risk_level=risk_level,
                setup_type=setup_type,
                risk_flags=risk_flags,
                upcoming_earnings_days=row.upcoming_earnings_days,
                return_1d=row.return_1d,
                return_5d=row.return_5d,
                return_10d=row.return_10d,
                return_20d=row.return_20d,
                gap_1d=row.gap_1d,
                volume_ratio_5d=row.volume_ratio_5d,
                volume_ratio_20d=row.volume_ratio_20d,
                volume_trend_5d_20d=row.volume_trend_5d_20d,
                distance_from_5d_high=row.distance_from_5d_high,
                distance_from_5d_low=row.distance_from_5d_low,
                distance_from_20d_high=row.distance_from_20d_high,
                distance_from_20d_low=row.distance_from_20d_low,
                sma_5_20_ratio=row.sma_5_20_ratio,
                close_vs_sma_20=row.close_vs_sma_20,
                up_day_ratio_5d=row.up_day_ratio_5d,
                up_day_ratio_10d=row.up_day_ratio_10d,
                dollar_volume=row.dollar_volume,
                atr_14_pct=row.atr_14_pct,
                rsi_14=row.rsi_14,
                rel_strength_spy_1d=row.rel_strength_spy_1d,
                rel_strength_spy_5d=row.rel_strength_spy_5d,
                rel_strength_spy_10d=row.rel_strength_spy_10d,
                rel_strength_spy_20d=row.rel_strength_spy_20d,
                rel_strength_qqq_1d=row.rel_strength_qqq_1d,
                rel_strength_qqq_5d=row.rel_strength_qqq_5d,
                rel_strength_qqq_10d=row.rel_strength_qqq_10d,
                rel_strength_qqq_20d=row.rel_strength_qqq_20d,
                volume_persistence_5d=row.volume_persistence_5d,
                volume_persistence_10d=row.volume_persistence_10d,
                volume_z_score_20d=row.volume_z_score_20d,
                liquidity_tier=row.liquidity_tier,
                expected_direction=expected_direction,
                expected_window="1d-5d",
                confidence_score=round(confidence_score, 4),
                reason_codes=reason_codes,
                factor_scores=factor_scores,
                factor_summaries=factor_summaries,
                factor_details=factor_details,
            )
        )

    results.sort(key=lambda c: c.score, reverse=True)
    return results


def _risk_mean(values: list[float | None]) -> float:
    present = [value for value in values if value is not None]
    return _mean_score(present)


def _risk_component(value: float | None, low: float, high: float) -> float | None:
    if value is None:
        return None
    return _scale(value, low, high)


def _inverse_risk_component(value: float | None, low: float, high: float) -> float | None:
    if value is None:
        return None
    return 1 - _scale(value, low, high)


def _negative_risk_component(value: float | None, low: float, high: float) -> float | None:
    if value is None:
        return None
    return _scale(-value, low, high)


def _liquidity_tier_risk(tier: str | None) -> float | None:
    if tier is None:
        return None
    return {
        "high": 0.0,
        "medium": 0.25,
        "low": 0.55,
        "thin": 0.85,
    }.get(str(tier).lower())


def _stretch_vs_atr(row: StockMetrics) -> float | None:
    if row.atr_14_pct is None or row.atr_14_pct <= 0 or row.return_5d is None:
        return None
    return row.return_5d / row.atr_14_pct


def _risk_detail(name: str, score: float, evidence: str) -> str | None:
    if score >= 0.65:
        return f"high {name}: {evidence}"
    if score >= 0.30:
        return f"moderate {name}: {evidence}"
    return None


def _event_risk(days: float | None) -> float:
    if days is None or days < 0 or days > 7:
        return 0.0
    return _clamp(1 - days / 7, 0.25, 1.0)


def _short_term_risk(row: StockMetrics) -> tuple[float, list[str]]:
    stretch_vs_atr = _stretch_vs_atr(row)
    extension_score = _risk_mean(
        [
            _risk_component(row.rsi_14, 60, 80),
            _risk_component(row.return_5d, 0.04, 0.16),
            _risk_component(row.return_10d, 0.08, 0.24),
            _risk_component(row.return_20d, 0.10, 0.30),
            _risk_component(row.distance_from_20d_low, 0.08, 0.28),
            _risk_component(row.distance_from_20d_high, -0.08, 0.02),
            _risk_component(stretch_vs_atr, 1.0, 3.5),
        ]
    )
    volatility_score = _risk_mean(
        [
            _risk_component(row.atr_14_pct, 0.02, 0.07),
            _risk_component(abs(row.gap_1d) if row.gap_1d is not None else None, 0.01, 0.06),
            _risk_component(abs(row.return_1d) if row.return_1d is not None else None, 0.02, 0.08),
        ]
    )
    liquidity_score = _risk_mean(
        [
            _liquidity_tier_risk(row.liquidity_tier),
            _inverse_risk_component(row.dollar_volume, 5_000_000, 100_000_000),
            _risk_component(row.volume_ratio_5d, 1.5, 4.0),
            _inverse_risk_component(row.volume_persistence_10d, 0.2, 0.8),
        ]
    )
    trend_failure_score = _risk_mean(
        [
            _negative_risk_component(row.close_vs_sma_20, 0.0, 0.08),
            _negative_risk_component(row.sma_5_20_ratio, 0.0, 0.06),
            _inverse_risk_component(row.up_day_ratio_10d, 0.3, 0.7),
        ]
    )
    event_score = _event_risk(row.upcoming_earnings_days)

    risk = (
        0.33 * extension_score
        + 0.20 * volatility_score
        + 0.20 * liquidity_score
        + 0.15 * trend_failure_score
        + 0.12 * event_score
    )

    flags = [
        flag
        for flag in [
            _risk_detail(
                "extension risk",
                extension_score,
                (
                    f"RSI {_fmt_num(row.rsi_14)}, 5D return {_fmt_pct(row.return_5d)}, "
                    f"10D return {_fmt_pct(row.return_10d)}, 20D low distance {_fmt_pct(row.distance_from_20d_low)}"
                ),
            ),
            _risk_detail(
                "volatility risk",
                volatility_score,
                f"ATR14 {_fmt_pct(row.atr_14_pct)}, gap {_fmt_pct(row.gap_1d)}, 1D return {_fmt_pct(row.return_1d)}",
            ),
            _risk_detail(
                "liquidity/participation risk",
                liquidity_score,
                (
                    f"tier {row.liquidity_tier or 'n/a'}, dollar volume {_fmt_money(row.dollar_volume)}, "
                    f"5D volume {_fmt_num(row.volume_ratio_5d)}x"
                ),
            ),
            _risk_detail(
                "trend failure risk",
                trend_failure_score,
                (
                    f"close vs SMA20 {_fmt_pct(row.close_vs_sma_20)}, "
                    f"SMA 5/20 {_fmt_pct(row.sma_5_20_ratio)}, up-day ratio 10D {_fmt_pct(row.up_day_ratio_10d)}"
                ),
            ),
            _risk_detail(
                "event risk",
                event_score,
                f"earnings in {_fmt_num(row.upcoming_earnings_days)} days",
            ),
        ]
        if flag is not None
    ]

    if not flags:
        flags = [
            "controlled volatility: ATR/gap/1D move are not elevated",
            "no near-term earnings flag",
            f"liquidity adequate: tier {row.liquidity_tier or 'n/a'}, dollar volume {_fmt_money(row.dollar_volume)}",
        ]

    return _clamp(max(risk, MIN_SHORT_TERM_RISK), 0.0, 1.0), flags


def _risk_level(risk_score: float) -> str:
    if risk_score < 0.25:
        return "low"
    if risk_score < 0.50:
        return "medium"
    return "high"


def _setup_type(row: StockMetrics, risk_score: float) -> str:
    if (
        row.upcoming_earnings_days is not None
        and 0 <= row.upcoming_earnings_days <= 7
    ):
        return "earnings risk"
    if risk_score >= 0.45:
        return "overextended"
    if (
        row.sma_5_20_ratio is not None
        and row.sma_5_20_ratio > 0
        and row.close_vs_sma_20 is not None
        and row.close_vs_sma_20 > 0
        and row.up_day_ratio_5d is not None
        and row.up_day_ratio_5d >= 0.6
        and risk_score < 0.35
    ):
        return "trend confirmation"
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
) -> tuple[float, str]:
    confidence = _clamp(0.60 * opportunity_score + 0.40 * (1 - risk_score), 0.0, 1.0)
    if confidence >= 0.70 and opportunity_score >= 0.65 and risk_score < 0.45:
        expected_direction = "bullish regime if conditions persist"
    elif risk_score >= 0.45:
        expected_direction = "extended/high-risk regime"
    else:
        expected_direction = "neutral/watch"

    return confidence, expected_direction
