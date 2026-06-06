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


def _factor_weights(scoring: dict[str, Any], regime: str | None = None) -> dict[str, float]:
    factor_weights = scoring.get("factor_weights")
    if isinstance(factor_weights, dict):
        weights = {
            "trend": float(factor_weights.get("trend", 0.25)),
            "momentum": float(factor_weights.get("momentum", 0.15)),
            "relative_strength": float(factor_weights.get("relative_strength", 0.25)),
            "participation": float(factor_weights.get("participation", 0.20)),
            "extension": float(factor_weights.get("extension", 0.15)),
        }
    else:
        # Backward-compatible defaults for older flat signal configs.
        weights = {
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

    if regime:
        regime_lower = regime.lower()
        if "supportive" in regime_lower:
            weights["momentum"] *= 1.3
            weights["relative_strength"] *= 1.2
            weights["extension"] *= 0.8
        elif "weak" in regime_lower:
            weights["extension"] *= 1.5
            weights["trend"] *= 1.2
            weights["momentum"] *= 0.6
        elif "mixed" in regime_lower:
            weights["trend"] *= 1.1
            weights["participation"] *= 1.1

    # Normalize weights
    weight_sum = sum(weights.values())
    if weight_sum > 0:
        weights = {k: v / weight_sum for k, v in weights.items()}

    return weights


FACTOR_COMPONENT_DEFAULTS: dict[str, dict[str, float]] = {
    "trend": {
        "sma_5_20_ratio": 0.35,
        "close_vs_sma_20": 0.25,
        "up_day_ratio_10d": 0.15,
        "close_location_20d": 0.15,
        "market_regime_score": 0.10,
    },
    "momentum": {
        "momentum_acceleration_5d_10d": 0.35,
        "return_1d": 0.15,
        "close_location_5d": 0.20,
        "rs_momentum_5d_20d": 0.15,
        "price_volume_efficiency_5d": 0.15,
    },
    "relative_strength": {
        "rs_momentum_5d_20d": 0.25,
        "rel_strength_spy_10d": 0.20,
        "rel_strength_qqq_10d": 0.15,
        "sector_relative_strength_5d": 0.15,
        "sector_relative_strength_10d": 0.15,
        "sector_relative_strength_20d": 0.10,
    },
    "participation": {
        "volume_acceleration_5d_20d": 0.15,
        "volume_ratio_5d": 0.15,
        "volume_trend_5d_20d": 0.10,
        "volume_persistence_5d": 0.15,
        "volume_persistence_10d": 0.15,
        "volume_z_score_20d": 0.10,
        "up_volume_ratio_10d": 0.10,
        "price_volume_efficiency_5d": 0.10,
        "dollar_volume": 0.05,
    },
    "extension": {
        "rsi_control": 0.25,
        "atr_14_pct": 0.25,
        "stretch_vs_atr": 0.20,
        "distance_from_20d_low": 0.15,
        "abs_gap_1d": 0.10,
        "failed_gap_or_fade": 0.05,
        "distribution_pressure": 0.05,
    },
}

RISK_WEIGHT_DEFAULTS = {
    "extension": 0.33,
    "volatility": 0.20,
    "liquidity": 0.20,
    "trend_failure": 0.15,
    "event": 0.12,
}

RISK_LEVEL_DEFAULTS = {
    "low_max": 0.25,
    "medium_max": 0.50,
}

RISK_THRESHOLD_DEFAULTS = {
    "extension": {
        "rsi_14": (60.0, 80.0),
        "return_5d": (0.04, 0.16),
        "return_10d": (0.08, 0.24),
        "return_20d": (0.10, 0.30),
        "distance_from_20d_low": (0.08, 0.28),
        "distance_from_20d_high": (-0.08, 0.02),
        "stretch_vs_atr": (1.0, 3.5),
    },
    "volatility": {
        "atr_14_pct": (0.02, 0.07),
        "abs_gap_1d": (0.01, 0.06),
        "abs_return_1d": (0.02, 0.08),
    },
    "liquidity": {
        "dollar_volume": (5_000_000.0, 100_000_000.0),
        "volume_ratio_5d": (1.5, 4.0),
        "volume_persistence_10d": (0.2, 0.8),
    },
    "trend_failure": {
        "close_vs_sma_20": (0.0, 0.08),
        "sma_5_20_ratio": (0.0, 0.06),
        "up_day_ratio_10d": (0.3, 0.7),
    },
}

ENTRY_QUALITY_DEFAULTS = {
    "close_location_1d_min": 0.55,
    "close_location_5d_min": 0.50,
    "max_return_1d": 0.08,
    "max_gap_1d": 0.05,
    "max_rsi_14": 78.0,
    "max_stretch_vs_atr": 3.0,
    "min_dollar_volume": 10_000_000.0,
}

RISK_ADJUSTED_RANKING_DEFAULTS = {
    "risk_penalty_weight": 0.35,
    "entry_penalty_weight": 0.20,
}

INVERTED_COMPONENTS = {
    "atr_14_pct",
    "stretch_vs_atr",
    "distance_from_20d_low",
    "abs_gap_1d",
    "failed_gap_or_fade",
    "effort_vs_result_5d",
    "distribution_day_count_10d",
    "distribution_pressure",
    "rs_decoupling",
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
    if metric in {"failed_gap_or_fade", "distribution_pressure", "rs_decoupling"}:
        return 1.0 if getattr(row, metric, None) else 0.0
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
            f"Trend {score:.2f}: SMA 5/20 {_fmt_pct(row.sma_5_20_ratio)}, "
            f"close vs SMA20 {_fmt_pct(row.close_vs_sma_20)}, "
            f"20D close location {_fmt_pct(row.close_location_20d)}, market regime {row.market_regime_label or 'n/a'}."
        )
    if factor == "momentum":
        return (
            f"Momentum {score:.2f}: acceleration {_fmt_pct(row.momentum_acceleration_5d_10d)}, "
            f"1D {_fmt_pct(row.return_1d)}, 5D close location {_fmt_pct(row.close_location_5d)}, "
            f"price/volume efficiency {_fmt_pct(row.price_volume_efficiency_5d)}."
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
            f"RS momentum {_fmt_pct(row.rs_momentum_5d_20d)}, 10D sector {_fmt_pct(row.sector_relative_strength_10d)}."
        )
    if factor == "participation":
        persistence = _top_component(components, "volume_persistence_10d") or {}
        return (
            f"Participation {score:.2f}: volume z-score {_fmt_num(row.volume_z_score_20d)}, "
            f"5D persistence {_fmt_pct(row.volume_persistence_5d)}, "
            f"10D persistence {_fmt_pct(row.volume_persistence_10d)} "
            f"(pct {_fmt_num(persistence.get('percentile'))}), "
            f"volume acceleration {_fmt_num(row.volume_acceleration_5d_20d)}, "
            f"up/down volume {_fmt_num(row.up_volume_ratio_10d)}x, "
            f"efficiency {_fmt_pct(row.price_volume_efficiency_5d)}, "
            f"liquidity tier {row.liquidity_tier or 'n/a'} ({_fmt_money(row.dollar_volume)})."
        )
    return (
        f"Extension control {score:.2f}: RSI {_fmt_num(row.rsi_14)}, "
        f"ATR14 {_fmt_pct(row.atr_14_pct)}, gap {_fmt_pct(row.gap_1d)}, "
        f"20D low distance {_fmt_pct(row.distance_from_20d_low)}, "
        f"fade/distribution flags {row.failed_gap_or_fade}/{row.distribution_pressure}."
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
    opportunity_score = _weighted_score(raw_scores, _factor_weights(scoring, row.market_regime_label))
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
    if row.distribution_pressure:
        reason_codes.append("DISTRIBUTION_PRESSURE")
    if row.rs_decoupling:
        reason_codes.append("RS_DECOUPLING")
    if row.failed_gap_or_fade:
        reason_codes.append("FAILED_GAP_OR_FADE")

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
        risk_score, risk_flags, risk_details = _short_term_risk_model(row, scoring)
        risk_level = _risk_level(risk_score, scoring)
        risk_details["level"] = risk_level
        lifecycle_details = _lifecycle_details(row, factor_scores, risk_score)
        confidence_score, expected_direction = _short_term_prediction(
            row,
            opportunity_score,
            risk_score,
        )
        reason_codes = _factor_reasons(factor_scores, risk_score, row)
        entry_quality_score, entry_quality_flags, entry_quality_details = _entry_quality_model(
            row,
            scoring,
        )
        score = _final_rank_score(
            opportunity_score,
            risk_score,
            entry_quality_score,
            scoring,
        )
        setup_type = _setup_type(row, risk_score)
        setup_details = _setup_details(row, factor_scores, risk_score, lifecycle_details)

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
                sector_relative_strength_5d=row.sector_relative_strength_5d,
                sector_relative_strength_10d=row.sector_relative_strength_10d,
                sector_relative_strength_20d=row.sector_relative_strength_20d,
                volume_persistence_5d=row.volume_persistence_5d,
                volume_persistence_10d=row.volume_persistence_10d,
                volume_z_score_20d=row.volume_z_score_20d,
                up_volume_ratio_10d=row.up_volume_ratio_10d,
                volume_acceleration_5d_20d=row.volume_acceleration_5d_20d,
                price_volume_efficiency_5d=row.price_volume_efficiency_5d,
                effort_vs_result_5d=row.effort_vs_result_5d,
                distribution_day_count_10d=row.distribution_day_count_10d,
                liquidity_tier=row.liquidity_tier,
                close_location_1d=row.close_location_1d,
                close_location_5d=row.close_location_5d,
                close_location_20d=row.close_location_20d,
                market_regime_score=row.market_regime_score,
                market_regime_label=row.market_regime_label,
                momentum_acceleration_5d_10d=row.momentum_acceleration_5d_10d,
                rs_momentum_5d_20d=row.rs_momentum_5d_20d,
                failed_gap_or_fade=row.failed_gap_or_fade,
                rs_decoupling=row.rs_decoupling,
                distribution_pressure=row.distribution_pressure,
                expected_direction=expected_direction,
                expected_window="1d-5d",
                confidence_score=round(confidence_score, 4),
                final_rank_score=round(score, 4),
                entry_quality_score=entry_quality_score,
                entry_quality_flags=entry_quality_flags,
                entry_quality_details=entry_quality_details,
                reason_codes=reason_codes,
                factor_scores=factor_scores,
                factor_summaries=factor_summaries,
                factor_details=factor_details,
                risk_details=risk_details,
                setup_details=setup_details,
                lifecycle_details=lifecycle_details,
            )
        )

    results.sort(key=lambda c: c.score, reverse=True)
    return results


def _risk_mean(values: list[float | None]) -> float:
    present = [value for value in values if value is not None]
    return _mean_score(present)


def _configured_risk_weights(scoring: dict[str, Any] | None) -> dict[str, float]:
    configured = (scoring or {}).get("risk_weights")
    weights = RISK_WEIGHT_DEFAULTS.copy()
    if isinstance(configured, dict):
        for name in weights:
            if name in configured:
                weights[name] = float(configured[name])
    return weights


def _configured_risk_levels(scoring: dict[str, Any] | None) -> dict[str, float]:
    configured = (scoring or {}).get("risk_levels")
    levels = RISK_LEVEL_DEFAULTS.copy()
    if isinstance(configured, dict):
        for name in levels:
            if name in configured:
                levels[name] = float(configured[name])
    return levels


def _configured_risk_thresholds(scoring: dict[str, Any] | None) -> dict[str, dict[str, tuple[float, float]]]:
    thresholds = {
        bucket: values.copy()
        for bucket, values in RISK_THRESHOLD_DEFAULTS.items()
    }
    configured = (scoring or {}).get("risk_thresholds")
    if isinstance(configured, dict):
        for bucket, values in configured.items():
            if not isinstance(values, dict):
                continue
            thresholds.setdefault(str(bucket), {})
            for metric, raw_range in values.items():
                if (
                    isinstance(raw_range, list | tuple)
                    and len(raw_range) == 2
                ):
                    thresholds[str(bucket)][str(metric)] = (
                        float(raw_range[0]),
                        float(raw_range[1]),
                    )
    return thresholds


def _configured_entry_quality(scoring: dict[str, Any] | None) -> dict[str, float]:
    thresholds = ENTRY_QUALITY_DEFAULTS.copy()
    configured = (scoring or {}).get("entry_quality")
    if isinstance(configured, dict):
        for name in thresholds:
            if name in configured:
                thresholds[name] = float(configured[name])
    return thresholds


def _configured_risk_adjusted_ranking(scoring: dict[str, Any] | None) -> dict[str, float]:
    weights = RISK_ADJUSTED_RANKING_DEFAULTS.copy()
    configured = (scoring or {}).get("risk_adjusted_ranking")
    if isinstance(configured, dict):
        for name in weights:
            if name in configured:
                weights[name] = float(configured[name])
    return weights


def _risk_range(
    thresholds: dict[str, dict[str, tuple[float, float]]],
    bucket: str,
    metric: str,
) -> tuple[float, float]:
    return thresholds[bucket][metric]


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


def _entry_check(name: str, passed: bool, evidence: str, weight: float) -> dict[str, Any]:
    return {
        "name": name,
        "passed": passed,
        "evidence": evidence,
        "weight": weight,
        "contribution": weight if passed else 0.0,
    }


def _entry_quality_model(
    row: StockMetrics,
    scoring: dict[str, Any] | None = None,
) -> tuple[float, list[str], dict[str, Any]]:
    thresholds = _configured_entry_quality(scoring)
    stretch_vs_atr = _stretch_vs_atr(row)

    not_intraday_extended = not (
        (row.return_1d is not None and row.return_1d > thresholds["max_return_1d"])
        or (row.gap_1d is not None and row.gap_1d > thresholds["max_gap_1d"])
        or (row.rsi_14 is not None and row.rsi_14 > thresholds["max_rsi_14"])
        or (stretch_vs_atr is not None and stretch_vs_atr > thresholds["max_stretch_vs_atr"])
    )
    constructive_close = (
        row.close_location_1d is not None
        and row.close_location_1d >= thresholds["close_location_1d_min"]
        and (
            row.close_location_5d is None
            or row.close_location_5d >= thresholds["close_location_5d_min"]
        )
    )
    no_gap_exhaustion = not (
        row.failed_gap_or_fade
        or (
            row.gap_1d is not None
            and row.gap_1d > thresholds["max_gap_1d"] * 0.80
            and row.close_location_1d is not None
            and row.close_location_1d < thresholds["close_location_1d_min"]
        )
    )
    no_distribution = not bool(row.distribution_pressure)
    adequate_liquidity = (
        row.dollar_volume is not None
        and row.dollar_volume >= thresholds["min_dollar_volume"]
        and str(row.liquidity_tier or "").lower() != "thin"
    )

    checks = [
        _entry_check(
            "not_intraday_extended",
            not_intraday_extended,
            (
                f"1D {_fmt_pct(row.return_1d)}, gap {_fmt_pct(row.gap_1d)}, "
                f"RSI {_fmt_num(row.rsi_14)}, stretch/ATR {_fmt_num(stretch_vs_atr)}"
            ),
            0.25,
        ),
        _entry_check(
            "constructive_close_location",
            constructive_close,
            (
                f"1D close location {_fmt_pct(row.close_location_1d)}, "
                f"5D close location {_fmt_pct(row.close_location_5d)}"
            ),
            0.20,
        ),
        _entry_check(
            "no_gap_exhaustion_or_fade",
            no_gap_exhaustion,
            f"failed gap/fade {row.failed_gap_or_fade}, gap {_fmt_pct(row.gap_1d)}",
            0.20,
        ),
        _entry_check(
            "no_distribution_pressure",
            no_distribution,
            f"distribution pressure {row.distribution_pressure}",
            0.20,
        ),
        _entry_check(
            "adequate_liquidity",
            adequate_liquidity,
            f"tier {row.liquidity_tier or 'n/a'}, dollar volume {_fmt_money(row.dollar_volume)}",
            0.15,
        ),
    ]
    weight_sum = sum(check["weight"] for check in checks) or 1.0
    score = _clamp(sum(check["contribution"] for check in checks) / weight_sum, 0.0, 1.0)
    flags = [
        f"entry check failed: {check['name']} ({check['evidence']})"
        for check in checks
        if not check["passed"]
    ]
    if not flags:
        flags = ["entry quality acceptable: extension, close location, distribution, and liquidity checks passed"]
    return round(score, 4), flags, {
        "score": round(score, 4),
        "thresholds": {name: round(value, 4) for name, value in thresholds.items()},
        "checks": checks,
    }


def _final_rank_score(
    opportunity_score: float,
    risk_score: float,
    entry_quality_score: float,
    scoring: dict[str, Any] | None = None,
) -> float:
    weights = _configured_risk_adjusted_ranking(scoring)
    score = (
        opportunity_score
        - weights["risk_penalty_weight"] * risk_score
        - weights["entry_penalty_weight"] * (1 - entry_quality_score)
    )
    return _clamp(score, 0.0, 1.0)


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


def _risk_metric(
    *,
    metric: str,
    raw: float | None,
    low: float | None = None,
    high: float | None = None,
    direction: str = "higher_is_riskier",
    score: float | None = None,
) -> dict[str, Any]:
    if score is None:
        if low is None or high is None:
            component_score = None
        elif direction == "lower_is_riskier":
            component_score = _inverse_risk_component(raw, low, high)
        elif direction == "negative_is_riskier":
            component_score = _negative_risk_component(raw, low, high)
        else:
            component_score = _risk_component(raw, low, high)
    else:
        component_score = score
    return {
        "metric": metric,
        "raw": raw,
        "low": low,
        "high": high,
        "direction": direction,
        "score": round(component_score, 4) if component_score is not None else None,
    }


def _bucket_detail(name: str, weight: float, metrics: list[dict[str, Any]], evidence: str) -> dict[str, Any]:
    score = _risk_mean([metric.get("score") for metric in metrics])
    return {
        "score": round(score, 4),
        "weight": round(weight, 4),
        "contribution": round(weight * score, 4),
        "evidence": evidence,
        "metrics": metrics,
        "severity": "high" if score >= 0.65 else "moderate" if score >= 0.30 else "low",
        "label": name,
    }


def _short_term_risk_model(
    row: StockMetrics,
    scoring: dict[str, Any] | None = None,
) -> tuple[float, list[str], dict[str, Any]]:
    raw_weights = _configured_risk_weights(scoring)
    weight_sum = sum(raw_weights.values()) or 1.0
    weights = {name: weight / weight_sum for name, weight in raw_weights.items()}
    thresholds = _configured_risk_thresholds(scoring)
    stretch_vs_atr = _stretch_vs_atr(row)

    extension_metrics = [
        _risk_metric(metric="rsi_14", raw=row.rsi_14, low=_risk_range(thresholds, "extension", "rsi_14")[0], high=_risk_range(thresholds, "extension", "rsi_14")[1]),
        _risk_metric(metric="return_5d", raw=row.return_5d, low=_risk_range(thresholds, "extension", "return_5d")[0], high=_risk_range(thresholds, "extension", "return_5d")[1]),
        _risk_metric(metric="return_10d", raw=row.return_10d, low=_risk_range(thresholds, "extension", "return_10d")[0], high=_risk_range(thresholds, "extension", "return_10d")[1]),
        _risk_metric(metric="return_20d", raw=row.return_20d, low=_risk_range(thresholds, "extension", "return_20d")[0], high=_risk_range(thresholds, "extension", "return_20d")[1]),
        _risk_metric(metric="distance_from_20d_low", raw=row.distance_from_20d_low, low=_risk_range(thresholds, "extension", "distance_from_20d_low")[0], high=_risk_range(thresholds, "extension", "distance_from_20d_low")[1]),
        _risk_metric(metric="distance_from_20d_high", raw=row.distance_from_20d_high, low=_risk_range(thresholds, "extension", "distance_from_20d_high")[0], high=_risk_range(thresholds, "extension", "distance_from_20d_high")[1]),
        _risk_metric(metric="stretch_vs_atr", raw=stretch_vs_atr, low=_risk_range(thresholds, "extension", "stretch_vs_atr")[0], high=_risk_range(thresholds, "extension", "stretch_vs_atr")[1]),
    ]
    volatility_metrics = [
        _risk_metric(metric="atr_14_pct", raw=row.atr_14_pct, low=_risk_range(thresholds, "volatility", "atr_14_pct")[0], high=_risk_range(thresholds, "volatility", "atr_14_pct")[1]),
        _risk_metric(metric="abs_gap_1d", raw=abs(row.gap_1d) if row.gap_1d is not None else None, low=_risk_range(thresholds, "volatility", "abs_gap_1d")[0], high=_risk_range(thresholds, "volatility", "abs_gap_1d")[1]),
        _risk_metric(metric="abs_return_1d", raw=abs(row.return_1d) if row.return_1d is not None else None, low=_risk_range(thresholds, "volatility", "abs_return_1d")[0], high=_risk_range(thresholds, "volatility", "abs_return_1d")[1]),
        _risk_metric(metric="failed_gap_or_fade", raw=1.0 if row.failed_gap_or_fade else None, direction="event", score=1.0 if row.failed_gap_or_fade else None),
        _risk_metric(metric="distribution_pressure", raw=1.0 if row.distribution_pressure else None, direction="event", score=1.0 if row.distribution_pressure else None),
    ]
    liquidity_metrics = [
        _risk_metric(metric="liquidity_tier", raw=None, direction="tier", score=_liquidity_tier_risk(row.liquidity_tier)),
        _risk_metric(metric="dollar_volume", raw=row.dollar_volume, low=_risk_range(thresholds, "liquidity", "dollar_volume")[0], high=_risk_range(thresholds, "liquidity", "dollar_volume")[1], direction="lower_is_riskier"),
        _risk_metric(metric="volume_ratio_5d", raw=row.volume_ratio_5d, low=_risk_range(thresholds, "liquidity", "volume_ratio_5d")[0], high=_risk_range(thresholds, "liquidity", "volume_ratio_5d")[1]),
        _risk_metric(metric="volume_persistence_10d", raw=row.volume_persistence_10d, low=_risk_range(thresholds, "liquidity", "volume_persistence_10d")[0], high=_risk_range(thresholds, "liquidity", "volume_persistence_10d")[1], direction="lower_is_riskier"),
    ]
    trend_failure_metrics = [
        _risk_metric(metric="close_vs_sma_20", raw=row.close_vs_sma_20, low=_risk_range(thresholds, "trend_failure", "close_vs_sma_20")[0], high=_risk_range(thresholds, "trend_failure", "close_vs_sma_20")[1], direction="negative_is_riskier"),
        _risk_metric(metric="sma_5_20_ratio", raw=row.sma_5_20_ratio, low=_risk_range(thresholds, "trend_failure", "sma_5_20_ratio")[0], high=_risk_range(thresholds, "trend_failure", "sma_5_20_ratio")[1], direction="negative_is_riskier"),
        _risk_metric(metric="up_day_ratio_10d", raw=row.up_day_ratio_10d, low=_risk_range(thresholds, "trend_failure", "up_day_ratio_10d")[0], high=_risk_range(thresholds, "trend_failure", "up_day_ratio_10d")[1], direction="lower_is_riskier"),
        _risk_metric(metric="rs_decoupling", raw=1.0 if row.rs_decoupling else None, direction="event", score=1.0 if row.rs_decoupling else None),
    ]
    event_metrics = [
        _risk_metric(metric="upcoming_earnings_days", raw=row.upcoming_earnings_days, direction="nearer_is_riskier", score=_event_risk(row.upcoming_earnings_days)),
    ]

    components = {
        "extension": _bucket_detail(
            "extension risk",
            weights["extension"],
            extension_metrics,
            (
                f"RSI {_fmt_num(row.rsi_14)}, 5D return {_fmt_pct(row.return_5d)}, "
                f"10D return {_fmt_pct(row.return_10d)}, 20D low distance {_fmt_pct(row.distance_from_20d_low)}"
            ),
        ),
        "volatility": _bucket_detail(
            "volatility risk",
            weights["volatility"],
            volatility_metrics,
            f"ATR14 {_fmt_pct(row.atr_14_pct)}, gap {_fmt_pct(row.gap_1d)}, 1D return {_fmt_pct(row.return_1d)}, fade/distribution {row.failed_gap_or_fade}/{row.distribution_pressure}",
        ),
        "liquidity": _bucket_detail(
            "liquidity/participation risk",
            weights["liquidity"],
            liquidity_metrics,
            (
                f"tier {row.liquidity_tier or 'n/a'}, dollar volume {_fmt_money(row.dollar_volume)}, "
                f"5D volume {_fmt_num(row.volume_ratio_5d)}x"
            ),
        ),
        "trend_failure": _bucket_detail(
            "trend failure risk",
            weights["trend_failure"],
            trend_failure_metrics,
            (
                f"close vs SMA20 {_fmt_pct(row.close_vs_sma_20)}, "
                f"SMA 5/20 {_fmt_pct(row.sma_5_20_ratio)}, up-day ratio 10D {_fmt_pct(row.up_day_ratio_10d)}, "
                f"RS decoupling {row.rs_decoupling}"
            ),
        ),
        "event": _bucket_detail(
            "event risk",
            weights["event"],
            event_metrics,
            f"earnings in {_fmt_num(row.upcoming_earnings_days)} days",
        ),
    }

    risk = sum(component["contribution"] for component in components.values())

    flags = [
        flag
        for component in components.values()
        if (
            flag := _risk_detail(
                component["label"],
                component["score"],
                component["evidence"],
            )
        ) is not None
    ]

    if not flags:
        flags = [
            "controlled volatility: ATR/gap/1D move are not elevated",
            "no near-term earnings flag",
            f"liquidity adequate: tier {row.liquidity_tier or 'n/a'}, dollar volume {_fmt_money(row.dollar_volume)}",
        ]

    score = _clamp(max(risk, MIN_SHORT_TERM_RISK), 0.0, 1.0)
    details = {
        "score": round(score, 4),
        "weights": {name: round(weight, 4) for name, weight in weights.items()},
        "components": components,
        "flags": flags,
    }
    return score, flags, details


def _short_term_risk(row: StockMetrics) -> tuple[float, list[str]]:
    risk_score, risk_flags, _ = _short_term_risk_model(row)
    return risk_score, risk_flags


def _risk_level(risk_score: float, scoring: dict[str, Any] | None = None) -> str:
    levels = _configured_risk_levels(scoring)
    if risk_score < levels["low_max"]:
        return "low"
    if risk_score < levels["medium_max"]:
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


def _lifecycle_details(
    row: StockMetrics,
    factor_scores: dict[str, float],
    risk_score: float,
) -> dict[str, Any]:
    trend = factor_scores.get("trend", 0.0)
    momentum = factor_scores.get("momentum", 0.0)
    participation = factor_scores.get("participation", 0.0)
    extension = factor_scores.get("extension", 0.0)
    acceleration = _scale(row.momentum_acceleration_5d_10d, -0.03, 0.05) if row.momentum_acceleration_5d_10d is not None else 0.5
    volume_acceleration = _scale(row.volume_acceleration_5d_20d, -0.5, 1.5) if row.volume_acceleration_5d_20d is not None else 0.5
    efficiency = _scale(row.price_volume_efficiency_5d, -0.02, 0.04) if row.price_volume_efficiency_5d is not None else 0.5
    poor_efficiency = 1 - efficiency
    distribution = 1.0 if row.distribution_pressure else (_scale(row.distribution_day_count_10d, 0, 4) if row.distribution_day_count_10d is not None else 0.0)
    fade = 1.0 if row.failed_gap_or_fade else 0.0
    rs_decoupling = 1.0 if row.rs_decoupling else 0.0

    phases = {
        "ignition": _clamp(0.30 * acceleration + 0.30 * volume_acceleration + 0.20 * participation + 0.20 * trend, 0.0, 1.0),
        "expansion": _clamp(0.30 * trend + 0.25 * momentum + 0.20 * participation + 0.15 * extension + 0.10 * (1 - risk_score), 0.0, 1.0),
        "euphoria": _clamp(0.35 * (1 - extension) + 0.25 * momentum + 0.20 * volume_acceleration + 0.20 * risk_score, 0.0, 1.0),
        "exhaustion": _clamp(0.30 * poor_efficiency + 0.25 * distribution + 0.20 * fade + 0.15 * rs_decoupling + 0.10 * (1 - extension), 0.0, 1.0),
        "reversal": _clamp(0.30 * risk_score + 0.25 * distribution + 0.20 * rs_decoupling + 0.15 * fade + 0.10 * (1 - trend), 0.0, 1.0),
    }
    regime_probabilities = {
        "continuation": round(_clamp(0.45 * phases["expansion"] + 0.30 * phases["ignition"] + 0.15 * participation + 0.10 * (1 - risk_score), 0.0, 1.0), 4),
        "mean_reversion": round(_clamp(0.45 * phases["exhaustion"] + 0.30 * phases["euphoria"] + 0.25 * phases["reversal"], 0.0, 1.0), 4),
        "volatility_expansion": round(_clamp(0.35 * risk_score + 0.25 * (row.atr_14_pct or 0.0) / 0.08 + 0.20 * volume_acceleration + 0.20 * phases["euphoria"], 0.0, 1.0), 4),
    }
    best_phase = max(phases.items(), key=lambda item: item[1])[0]
    return {
        "phase": best_phase,
        "phase_scores": {name: round(score, 4) for name, score in phases.items()},
        "regime_probabilities": regime_probabilities,
        "signals": {
            "poor_price_volume_efficiency": round(poor_efficiency, 4),
            "distribution_pressure": row.distribution_pressure,
            "failed_gap_or_fade": row.failed_gap_or_fade,
            "rs_decoupling": row.rs_decoupling,
        },
        "note": "Heuristic regime probabilities; not yet calibrated to historical forward outcomes.",
    }


def _setup_details(
    row: StockMetrics,
    factor_scores: dict[str, float],
    risk_score: float,
    lifecycle_details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    trend = factor_scores.get("trend", 0.0)
    momentum = factor_scores.get("momentum", 0.0)
    relative_strength = factor_scores.get("relative_strength", 0.0)
    participation = factor_scores.get("participation", 0.0)
    extension = factor_scores.get("extension", 0.0)
    risk_control = 1 - risk_score

    diagnostics = {
        "trend_confirmation": {
            "score": round(_clamp(0.35 * trend + 0.20 * momentum + 0.20 * relative_strength + 0.15 * participation + 0.10 * risk_control, 0.0, 1.0), 4),
            "formula": "0.35*trend + 0.20*momentum + 0.20*relative_strength + 0.15*participation + 0.10*risk_control",
        },
        "momentum_continuation": {
            "score": round(_clamp(0.30 * momentum + 0.25 * relative_strength + 0.15 * participation + 0.15 * extension + 0.15 * risk_control, 0.0, 1.0), 4),
            "formula": "0.30*momentum + 0.25*relative_strength + 0.15*participation + 0.15*extension + 0.15*risk_control",
        },
        "breakout_watch": {
            "score": round(_clamp(0.25 * trend + 0.25 * participation + 0.20 * relative_strength + 0.15 * momentum + 0.15 * (row.close_location_20d or 0.0), 0.0, 1.0), 4),
            "formula": "0.25*trend + 0.25*participation + 0.20*relative_strength + 0.15*momentum + 0.15*close_location_20d",
        },
        "pullback_risk": {
            "score": round(_clamp(0.30 * (1 - trend) + 0.25 * (1 - momentum) + 0.25 * risk_score + 0.20 * (1 - extension), 0.0, 1.0), 4),
            "formula": "0.30*(1-trend) + 0.25*(1-momentum) + 0.25*risk + 0.20*(1-extension)",
        },
    }
    best_setup, best_payload = max(
        diagnostics.items(),
        key=lambda item: item[1]["score"],
    )
    return {
        "best_setup_score": best_setup,
        "best_score": best_payload["score"],
        "setups": diagnostics,
        "lifecycle_phase": (lifecycle_details or {}).get("phase"),
        "regime_probabilities": (lifecycle_details or {}).get("regime_probabilities", {}),
    }


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

