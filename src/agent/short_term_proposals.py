"""Generate short-term research proposals from screener candidates."""

from __future__ import annotations

import json
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from src.agent.ollama_client import OllamaClient

DISCLAIMER = (
    "Not financial advice. Short-term trading is high risk. "
    "Use this only as research and define your own position sizing and risk limits."
)


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def _num(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def _market_cap(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    return f"${value:,.0f}"


FACTOR_EXPLANATIONS = {
    "trend": "Price structure: longer-window return, short-vs-medium moving average alignment, close vs SMA20, and recent up-day consistency.",
    "momentum": "Recent price movement across 1D, 5D, 10D, and 20D windows.",
    "relative_strength": "Outperformance or underperformance versus SPY and QQQ across multiple windows.",
    "participation": "Volume and liquidity support: relative volume, persistence of elevated volume, volume z-score, and dollar volume.",
    "extension": "Stretch/risk control: RSI, ATR, gap size, move-vs-ATR, and position above the 20D low. Higher is less stretched.",
}

FACTOR_TARGET_RANGES = [
    (
        "Trend",
        "Good: score >= 0.70 with price above SMA20, positive SMA 5/20, and frequent up days. Mixed: 0.45-0.69. Weak: < 0.45 or price structure below average.",
    ),
    (
        "Momentum",
        "Good: score >= 0.70 with positive 5D/10D/20D returns. Mixed: 0.45-0.69. Weak: < 0.45 or fading/negative recent returns.",
    ),
    (
        "Relative strength",
        "Good: score >= 0.70 with positive SPY/QQQ outperformance, especially 10D/20D. Mixed: 0.45-0.69. Weak: < 0.45 or benchmark underperformance.",
    ),
    (
        "Participation",
        "Good: score >= 0.70 with relative volume > 1.0x, positive volume z-score, persistence, and non-thin liquidity. Mixed: 0.45-0.69. Weak: < 0.45 or thin/fading volume.",
    ),
    (
        "Extension control",
        "Good: score >= 0.70 means less stretched. Mixed: 0.45-0.69. Risky: < 0.45, often from high RSI, high ATR, a large gap, or being far above the 20D low.",
    ),
]

METRIC_EXPLANATIONS = [
    ("score", "Composite rank score used to order candidates."),
    ("opportunity_score", "Weighted average of factor scores before risk adjustment."),
    ("risk_score", "Continuous short-term risk score from extension, volatility, liquidity, trend failure, and event components."),
    ("risk_details", "Component-level breakdown of the risk score, including weights, contributions, and metric scores."),
    ("confidence_score", "Blend of opportunity and risk; it is not a price prediction."),
    ("return_1d/5d/10d/20d", "Recent total return over the named trading window."),
    ("rel_strength_*", "Candidate return minus SPY or QQQ return for the same window."),
    ("sector_relative_strength_*", "Candidate return minus the median return of its sector peers in the screened universe."),
    ("market_regime_score", "Broad SPY/QQQ backdrop score from recent benchmark trend and moving-average position."),
    ("close_location_1d/5d/20d", "Where the close sits inside the day or recent range; 1.0 means near the high."),
    ("volume_ratio_5d/20d", "Latest volume divided by the prior 5D or 20D average."),
    ("volume_trend_5d_20d", "Recent 5D average volume divided by the 20D average volume."),
    ("volume_persistence_5d/10d", "Share of recent days with volume above the 20D average."),
    ("up_volume_ratio_10d", "Volume on up days divided by volume on down days over the last 10 sessions."),
    ("volume_z_score_20d", "How many standard deviations latest volume is from the trailing 20D average."),
    ("liquidity_tier", "Dollar-volume bucket: high, medium, low, or thin."),
    ("dollar_volume", "Latest close multiplied by latest volume."),
    ("sma_5_20_ratio", "5D average price versus 20D average price."),
    ("close_vs_sma_20", "Latest close versus the 20D average price."),
    ("up_day_ratio_5d/10d", "Share of recent sessions that closed higher than the prior session."),
    ("distance_from_5d/20d_high", "How far the latest close is below or above the recent high."),
    ("distance_from_5d/20d_low", "How far the latest close is above the recent low."),
    ("atr_14_pct", "14D average true range as a percent of price; higher means more volatility."),
    ("rsi_14", "14D relative strength index; high values can indicate stretch."),
    ("gap_1d", "Latest open compared with the prior close."),
    ("failed_gap_or_fade", "True when a gap/strong session closes weakly inside the daily range."),
    ("setup_details", "Setup-specific scores used to diagnose which setup style the candidate best fits."),
    ("upcoming_earnings_days", "Days until earnings; negative means the date is already past."),
]


def _metric_guide() -> list[str]:
    return [
        "## How To Read This Report",
        "",
        "Each candidate starts with a quick scorecard and plain-English factor notes. The detailed formula math is included in a collapsible section so the report stays readable while remaining auditable.",
        "",
        "### Score Basics",
        "",
        "- **Factor scores:** 0 to 1 scores for trend, momentum, relative strength, participation, and extension control.",
        "- **Percentile rank (`pct`):** Where the metric sits inside the screened universe. `0.90` means stronger than about 90% of screened names for that metric.",
        "- **Z-score (`z`):** How unusual the raw value is versus the screened universe average. Positive is above average; negative is below average.",
        "- **Weight:** The component's influence inside that factor formula.",
        "- **Regime language:** The setup describes a conditional market regime, not a price forecast.",
        "",
        "### Risk Target Ranges",
        "",
        "- **Low risk:** < 0.25. No major risk bucket is elevated, though normal short-term market risk still applies.",
        "- **Medium risk:** 0.25-0.49. At least one risk bucket is moderately elevated and should be monitored.",
        "- **High risk:** >= 0.50. Extension, volatility, liquidity, trend failure, or event risk is materially elevated.",
        "- **Risk buckets:** extension, volatility, liquidity/participation, trend failure, and earnings/event timing.",
        "",
        "### Factor Target Ranges",
        "",
        "- **General score guide:** >= 0.70 is strong/good, 0.45-0.69 is mixed/watch, and < 0.45 is weak or risky for that bucket.",
        *[
            f"- **{factor}:** {description}"
            for factor, description in FACTOR_TARGET_RANGES
        ],
        "",
        "### Factor Glossary",
        "",
        *[
            f"- **{factor.replace('_', ' ').title()}:** {description}"
            for factor, description in FACTOR_EXPLANATIONS.items()
        ],
        "",
        "### Metric Glossary",
        "",
        *[
            f"- **{metric}:** {description}"
            for metric, description in METRIC_EXPLANATIONS
        ],
        "",
    ]


def _factor_score_line(candidate: dict[str, Any]) -> str:
    scores = candidate.get("factor_scores") or {}
    if not isinstance(scores, dict):
        scores = {}
    return (
        f"trend {_num(scores.get('trend'))}; "
        f"momentum {_num(scores.get('momentum'))}; "
        f"relative strength {_num(scores.get('relative_strength'))}; "
        f"participation {_num(scores.get('participation'))}; "
        f"extension control {_num(scores.get('extension'))}"
    )


def _factor_summary_block(candidate: dict[str, Any]) -> list[str]:
    summaries = candidate.get("factor_summaries") or []
    if not summaries:
        summaries = ["Factor model summary is unavailable for this candidate."]
    return [
        "**Quick scorecard:**",
        f"- **Factor scores:** {_factor_score_line(candidate)}.",
        "- **Read this as:** higher trend/momentum/relative strength/participation is better; higher extension control means less stretched.",
        *[f"- {summary}" for summary in summaries],
    ]


def _factor_detail_value(metric: str, value: float | None) -> str:
    if value is None:
        return "n/a"
    percent_metrics = (
        "return",
        "rel_strength",
        "distance",
        "sma",
        "close_vs",
        "up_day",
        "gap",
        "atr",
        "volume_persistence",
        "sector_relative_strength",
        "close_location",
    )
    multiple_metrics = {
        "volume_ratio_5d",
        "volume_ratio_20d",
        "volume_trend_5d_20d",
        "stretch_vs_atr",
        "up_volume_ratio_10d",
    }
    if metric == "dollar_volume":
        return _market_cap(value)
    if metric in multiple_metrics:
        return f"{value:.2f}x"
    if metric.startswith(percent_metrics):
        return _pct(value)
    return _num(value)


def _factor_details_block(candidate: dict[str, Any]) -> list[str]:
    details = candidate.get("factor_details") or {}
    if not isinstance(details, dict) or not details:
        return ["<details>", "<summary><strong>Formula details</strong></summary>", "", "Formula and component details are unavailable.", "", "</details>"]

    lines = [
        "<details>",
        "<summary><strong>Formula details</strong> - expand for component math</summary>",
        "",
        "Component fields: `raw` is the observed value, `pct` is screened-universe percentile, `z` is standard deviations from average, `weight` is formula influence, and `score` is the component score after direction adjustment.",
        "",
    ]
    for factor in ["trend", "momentum", "relative_strength", "participation", "extension"]:
        payload = details.get(factor)
        if not isinstance(payload, dict):
            continue
        formula = payload.get("formula") or "n/a"
        factor_name = factor.replace("_", " ").title()
        explanation = FACTOR_EXPLANATIONS.get(factor, "")
        lines.append(f"**{factor_name}**")
        if explanation:
            lines.append(f"- Meaning: {explanation}")
        lines.append(f"- Formula: `{formula}`")
        components = payload.get("components") or []
        for component in components:
            if not isinstance(component, dict):
                continue
            metric = str(component.get("metric") or "n/a")
            lines.append(
                f"  - {metric}: raw {_factor_detail_value(metric, component.get('raw'))}; "
                f"pct {_num(component.get('percentile'))}; "
                f"z {_num(component.get('z_score'))}; "
                f"weight {_num(component.get('weight'))}; "
                f"score {_num(component.get('score'))}."
            )
        lines.append("")
    lines.append("</details>")
    return lines


def _risk_details_block(candidate: dict[str, Any]) -> list[str]:
    details = candidate.get("risk_details") or {}
    components = details.get("components") if isinstance(details, dict) else None
    if not isinstance(components, dict) or not components:
        return []

    lines = [
        "<details>",
        "<summary><strong>Risk details</strong> - expand for component math</summary>",
        "",
        "Risk fields: `score` is the bucket risk from 0 to 1, `weight` is bucket influence, and `contribution` is the weighted risk added to the final score.",
        "",
    ]
    for name in ["extension", "volatility", "liquidity", "trend_failure", "event"]:
        component = components.get(name)
        if not isinstance(component, dict):
            continue
        label = str(component.get("label") or name).replace("_", " ").title()
        lines.append(f"**{label}**")
        lines.append(
            f"- Score {_num(component.get('score'))}; weight {_num(component.get('weight'))}; "
            f"contribution {_num(component.get('contribution'))}; severity {component.get('severity') or 'n/a'}."
        )
        if component.get("evidence"):
            lines.append(f"- Evidence: {component.get('evidence')}")
        for metric in component.get("metrics") or []:
            if not isinstance(metric, dict):
                continue
            metric_name = str(metric.get("metric") or "n/a")
            lines.append(
                f"  - {metric_name}: raw {_factor_detail_value(metric_name, metric.get('raw'))}; "
                f"risk score {_num(metric.get('score'))}; range {_num(metric.get('low'))}-{_num(metric.get('high'))}."
            )
        lines.append("")
    lines.append("</details>")
    return lines


def _setup_details_block(candidate: dict[str, Any]) -> list[str]:
    details = candidate.get("setup_details") or {}
    setups = details.get("setups") if isinstance(details, dict) else None
    if not isinstance(setups, dict) or not setups:
        return []
    lines = [
        "**Setup diagnostics:**",
        f"- Best diagnostic setup: {str(details.get('best_setup_score') or 'n/a').replace('_', ' ')} with score {_num(details.get('best_score'))}.",
    ]
    for name, payload in setups.items():
        if isinstance(payload, dict):
            lines.append(f"- {name.replace('_', ' ')}: {_num(payload.get('score'))}.")
    return lines


def _metric_block(candidate: dict[str, Any]) -> list[str]:
    return [
        "**Metrics:**",
        f"- **Snapshot:** {candidate.get('market') or 'n/a'} / {candidate.get('exchange') or 'n/a'}; price {_num(candidate.get('current_price'))}; market cap {_market_cap(candidate.get('market_cap'))}.",
        f"- **Scores:** rank {_num(candidate.get('score'))}; opportunity {_num(candidate.get('opportunity_score'))}; risk {_num(candidate.get('risk_score'))} ({candidate.get('risk_level') or 'n/a'}); confidence {_num(candidate.get('confidence_score'))}.",
        f"- **Regime:** {candidate.get('expected_direction') or 'n/a'} over {candidate.get('expected_window') or 'n/a'}; setup {candidate.get('setup_type') or 'n/a'}.",
        "",
        "**Price action:**",
        f"- Returns: 1D {_pct(candidate.get('return_1d'))}; 5D {_pct(candidate.get('return_5d'))}; 10D {_pct(candidate.get('return_10d'))}; 20D {_pct(candidate.get('return_20d'))}.",
        f"- Trend quality: SMA 5/20 {_pct(candidate.get('sma_5_20_ratio'))}; close vs SMA20 {_pct(candidate.get('close_vs_sma_20'))}; up days 5D {_pct(candidate.get('up_day_ratio_5d'))}; up days 10D {_pct(candidate.get('up_day_ratio_10d'))}.",
        f"- Range and volatility: 5D high {_pct(candidate.get('distance_from_5d_high'))}; 5D low {_pct(candidate.get('distance_from_5d_low'))}; 20D high {_pct(candidate.get('distance_from_20d_high'))}; 20D low {_pct(candidate.get('distance_from_20d_low'))}; close location 1D {_pct(candidate.get('close_location_1d'))}; 5D {_pct(candidate.get('close_location_5d'))}; 20D {_pct(candidate.get('close_location_20d'))}; ATR14 {_pct(candidate.get('atr_14_pct'))}; gap {_pct(candidate.get('gap_1d'))}; RSI14 {_num(candidate.get('rsi_14'))}; fade flag {candidate.get('failed_gap_or_fade')}.",
        "",
        "**Benchmark relative strength:**",
        f"- Versus SPY: 1D {_pct(candidate.get('rel_strength_spy_1d'))}; 5D {_pct(candidate.get('rel_strength_spy_5d'))}; 10D {_pct(candidate.get('rel_strength_spy_10d'))}; 20D {_pct(candidate.get('rel_strength_spy_20d'))}.",
        f"- Versus QQQ: 1D {_pct(candidate.get('rel_strength_qqq_1d'))}; 5D {_pct(candidate.get('rel_strength_qqq_5d'))}; 10D {_pct(candidate.get('rel_strength_qqq_10d'))}; 20D {_pct(candidate.get('rel_strength_qqq_20d'))}.",
        f"- Versus sector peers: 5D {_pct(candidate.get('sector_relative_strength_5d'))}; 10D {_pct(candidate.get('sector_relative_strength_10d'))}; 20D {_pct(candidate.get('sector_relative_strength_20d'))}.",
        f"- Market regime: {_num(candidate.get('market_regime_score'))} ({candidate.get('market_regime_label') or 'n/a'}).",
        "",
        "**Volume and liquidity:**",
        f"- Relative volume: 5D {_num(candidate.get('volume_ratio_5d'))}x; 20D {_num(candidate.get('volume_ratio_20d'))}x; 5D/20D trend {_num(candidate.get('volume_trend_5d_20d'))}x.",
        f"- Participation evidence: volume z-score {_num(candidate.get('volume_z_score_20d'))}; elevated-volume persistence 5D {_pct(candidate.get('volume_persistence_5d'))}; 10D {_pct(candidate.get('volume_persistence_10d'))}; up/down volume 10D {_num(candidate.get('up_volume_ratio_10d'))}x.",
        f"- Liquidity: tier {candidate.get('liquidity_tier') or 'n/a'}; dollar volume {_market_cap(candidate.get('dollar_volume'))}.",
        "",
        "**Other context:**",
        f"- Upcoming earnings days: {_num(candidate.get('upcoming_earnings_days'))}.",
    ]


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def _allowed_observations(candidate: dict[str, Any]) -> list[str]:
    observations: list[str] = []
    return_1d = candidate.get("return_1d")
    return_5d = candidate.get("return_5d")
    return_10d = candidate.get("return_10d")
    volume_ratio = candidate.get("volume_ratio_5d")
    volume_ratio_20d = candidate.get("volume_ratio_20d")
    volume_trend = candidate.get("volume_trend_5d_20d")
    distance_high = candidate.get("distance_from_5d_high")
    distance_high_20d = candidate.get("distance_from_20d_high")
    rsi = candidate.get("rsi_14")
    rel_spy = candidate.get("rel_strength_spy_5d")
    rel_qqq = candidate.get("rel_strength_qqq_5d")
    rel_spy_10d = candidate.get("rel_strength_spy_10d")
    rel_spy_20d = candidate.get("rel_strength_spy_20d")
    rel_qqq_10d = candidate.get("rel_strength_qqq_10d")
    rel_qqq_20d = candidate.get("rel_strength_qqq_20d")
    sector_rs_10d = candidate.get("sector_relative_strength_10d")
    sector_rs_20d = candidate.get("sector_relative_strength_20d")
    volume_persistence_5d = candidate.get("volume_persistence_5d")
    volume_persistence_10d = candidate.get("volume_persistence_10d")
    volume_z_score = candidate.get("volume_z_score_20d")
    up_volume_ratio = candidate.get("up_volume_ratio_10d")
    liquidity_tier = candidate.get("liquidity_tier")
    atr = candidate.get("atr_14_pct")
    sma_ratio = candidate.get("sma_5_20_ratio")
    close_vs_sma = candidate.get("close_vs_sma_20")
    close_location_20d = candidate.get("close_location_20d")
    market_regime_score = candidate.get("market_regime_score")
    market_regime_label = candidate.get("market_regime_label")
    failed_gap_or_fade = candidate.get("failed_gap_or_fade")
    up_day_5d = candidate.get("up_day_ratio_5d")
    if return_1d is not None:
        if return_1d > 0:
            observations.append(f"Latest session was positive at {_pct(return_1d)}.")
        else:
            observations.append(f"Latest session was negative at {_pct(return_1d)}.")
    if return_5d is not None:
        if return_5d > 0:
            observations.append(f"Five-day return is positive at {_pct(return_5d)}.")
        else:
            observations.append(f"Five-day return is negative at {_pct(return_5d)}.")
    if return_10d is not None:
        observations.append(f"Ten-day return is {_pct(return_10d)}.")
    if volume_ratio is not None:
        observations.append(
            f"Latest volume is {_num(volume_ratio)}x the prior 5-day average."
        )
    if volume_ratio_20d is not None:
        observations.append(
            f"Latest volume is {_num(volume_ratio_20d)}x the prior 20-day average."
        )
    if volume_trend is not None:
        observations.append(f"Recent 5-day volume trend is {_num(volume_trend)}x the 20-day average.")
    if volume_z_score is not None:
        observations.append(f"Latest volume z-score versus the trailing 20 days is {_num(volume_z_score)}.")
    if up_volume_ratio is not None:
        observations.append(f"10-day up/down volume ratio is {_num(up_volume_ratio)}x.")
    if volume_persistence_5d is not None:
        observations.append(f"Elevated-volume persistence over 5 days is {_pct(volume_persistence_5d)}.")
    if volume_persistence_10d is not None:
        observations.append(f"Elevated-volume persistence over 10 days is {_pct(volume_persistence_10d)}.")
    if liquidity_tier is not None:
        observations.append(f"Liquidity tier is {liquidity_tier}.")
    if distance_high is not None:
        observations.append(f"Price is {_pct(distance_high)} from the 5-day high.")
    if distance_high_20d is not None:
        observations.append(f"Price is {_pct(distance_high_20d)} from the 20-day high.")
    if close_location_20d is not None:
        observations.append(f"20-day close location is {_pct(close_location_20d)}.")
    if rsi is not None:
        observations.append(f"RSI 14 is {_num(rsi)}.")
    if sma_ratio is not None:
        observations.append(f"SMA 5/20 trend ratio is {_pct(sma_ratio)}.")
    if close_vs_sma is not None:
        observations.append(f"Price is {_pct(close_vs_sma)} versus SMA20.")
    if up_day_5d is not None:
        observations.append(f"Up-day ratio over 5 days is {_pct(up_day_5d)}.")
    if rel_spy is not None:
        observations.append(f"5-day relative strength vs SPY is {_pct(rel_spy)}.")
    if rel_qqq is not None:
        observations.append(f"5-day relative strength vs QQQ is {_pct(rel_qqq)}.")
    if rel_spy_10d is not None:
        observations.append(f"10-day relative strength vs SPY is {_pct(rel_spy_10d)}.")
    if rel_spy_20d is not None:
        observations.append(f"20-day relative strength vs SPY is {_pct(rel_spy_20d)}.")
    if rel_qqq_10d is not None:
        observations.append(f"10-day relative strength vs QQQ is {_pct(rel_qqq_10d)}.")
    if rel_qqq_20d is not None:
        observations.append(f"20-day relative strength vs QQQ is {_pct(rel_qqq_20d)}.")
    if sector_rs_10d is not None:
        observations.append(f"10-day relative strength vs sector peers is {_pct(sector_rs_10d)}.")
    if sector_rs_20d is not None:
        observations.append(f"20-day relative strength vs sector peers is {_pct(sector_rs_20d)}.")
    if market_regime_score is not None:
        observations.append(f"Market regime score is {_num(market_regime_score)} ({market_regime_label or 'n/a'}).")
    if failed_gap_or_fade:
        observations.append("Failed gap or intraday fade risk is flagged.")
    if atr is not None:
        observations.append(f"ATR 14 is {_pct(atr)} of price.")
    observations.extend(candidate.get("reasons") or [])
    return observations


def _proposal_highlights(candidate: dict[str, Any]) -> list[str]:
    factor_summaries = candidate.get("factor_summaries") or []
    if factor_summaries:
        return list(factor_summaries)[:5]

    highlights: list[str] = []
    return_5d = candidate.get("return_5d")
    return_10d = candidate.get("return_10d")
    volume_ratio = candidate.get("volume_ratio_5d")
    volume_ratio_20d = candidate.get("volume_ratio_20d")
    volume_trend = candidate.get("volume_trend_5d_20d")
    volume_z_score = candidate.get("volume_z_score_20d")
    liquidity_tier = candidate.get("liquidity_tier")
    rel_spy = candidate.get("rel_strength_spy_5d")
    rel_qqq = candidate.get("rel_strength_qqq_5d")
    rel_spy_10d = candidate.get("rel_strength_spy_10d")
    rel_qqq_10d = candidate.get("rel_strength_qqq_10d")
    rsi = candidate.get("rsi_14")
    distance_high = candidate.get("distance_from_5d_high")
    sma_ratio = candidate.get("sma_5_20_ratio")
    up_day_5d = candidate.get("up_day_ratio_5d")

    if return_5d is not None:
        highlights.append(f"Five-day return is {_pct(return_5d)}.")
    if return_10d is not None:
        highlights.append(f"Ten-day return is {_pct(return_10d)}.")
    if rel_spy is not None:
        highlights.append(f"5-day relative strength vs SPY is {_pct(rel_spy)}.")
    if rel_qqq is not None:
        highlights.append(f"5-day relative strength vs QQQ is {_pct(rel_qqq)}.")
    if rel_spy_10d is not None:
        highlights.append(f"10-day relative strength vs SPY is {_pct(rel_spy_10d)}.")
    if rel_qqq_10d is not None:
        highlights.append(f"10-day relative strength vs QQQ is {_pct(rel_qqq_10d)}.")
    if volume_ratio is not None:
        highlights.append(f"Latest volume is {_num(volume_ratio)}x the prior 5-day average.")
    if volume_ratio_20d is not None:
        highlights.append(f"Latest volume is {_num(volume_ratio_20d)}x the prior 20-day average.")
    if volume_trend is not None:
        highlights.append(f"5-day volume trend is {_num(volume_trend)}x the 20-day average.")
    if volume_z_score is not None:
        highlights.append(f"Volume z-score versus the trailing 20 days is {_num(volume_z_score)}.")
    if liquidity_tier is not None:
        highlights.append(f"Liquidity tier is {liquidity_tier}.")
    if distance_high is not None:
        highlights.append(f"Price is {_pct(distance_high)} from the 5-day high.")
    if rsi is not None:
        highlights.append(f"RSI 14 is {_num(rsi)}.")
    if sma_ratio is not None:
        highlights.append(f"SMA 5/20 trend ratio is {_pct(sma_ratio)}.")
    if up_day_5d is not None:
        highlights.append(f"Up-day ratio over 5 days is {_pct(up_day_5d)}.")

    return highlights[:5] or ["Short-term composite score ranked highly."]


def _risk_observations(candidate: dict[str, Any]) -> list[str]:
    risks: list[str] = []
    risk_score = candidate.get("risk_score")
    risk_level = candidate.get("risk_level")
    risk_flags = candidate.get("risk_flags") or []

    risks.extend(str(flag) for flag in risk_flags)

    if risk_score is not None:
        risks.append(
            f"Risk score is {_num(risk_score)} ({risk_level or 'n/a'}) on a continuous 0 to 1 scale."
        )
    market_cap = candidate.get("market_cap")
    dollar_volume = candidate.get("dollar_volume")
    if market_cap is not None and market_cap < 1_000_000_000:
        risks.append("smaller market-cap name; liquidity and spreads may matter more")
    if dollar_volume is not None and dollar_volume < 25_000_000:
        risks.append("lower dollar volume; entries and exits may be harder")
    deduped = list(dict.fromkeys(risks))
    if not deduped:
        risks.append("Main invalidation is loss of positive momentum or fading relative volume.")
        return risks
    return deduped


def _deterministic_proposal(candidate: dict[str, Any]) -> str:
    observations = _proposal_highlights(candidate)
    risks = _risk_observations(candidate)
    symbol = candidate.get("symbol")
    name = candidate.get("name")
    setup_type = candidate.get("setup_type") or "short-term"
    article = "an" if setup_type[:1].lower() in {"a", "e", "i", "o", "u"} else "a"

    why = observations[:5] if observations else ["Short-term composite score ranked highly."]
    risk_lines = risks[:4]

    return "\n".join(
        [
            f"### {symbol} - {name}",
            f"**Setup:** {symbol} is {article} {setup_type} candidate based on the current 1-day to 1-week screen. "
            f"The setup is a conditional market regime, not a standalone price forecast.",
            "",
            *_factor_summary_block(candidate),
            "",
            *_factor_details_block(candidate),
            "",
            *_risk_details_block(candidate),
            "",
            *_setup_details_block(candidate),
            "",
            *_metric_block(candidate),
            "",
            "**Why it screens well:**",
            *[f"- {item}" for item in why],
            f"- Opportunity score is {_num(candidate.get('opportunity_score'))}; risk score is {_num(candidate.get('risk_score'))}.",
            f"- Factor reason codes: {', '.join(candidate.get('reason_codes') or ['n/a'])}.",
            "",
            "**1-day to 1-week plan:**",
            "- Watch whether the stock continues to outperform SPY/QQQ over the next session.",
            "- Watch whether relative volume stays supportive; fading volume weakens the setup.",
            "- Treat loss of factor support plus fading relative volume as invalidation.",
            "",
            "**Main risks:**",
            *[f"- {item}" for item in risk_lines],
            "",
            "**Verdict:** This is a watchlist candidate for short-term research only; the setup depends on momentum and volume staying intact. Not financial advice.",
        ]
    )


def _format_ollama_json(candidate: dict[str, Any], payload: dict[str, Any]) -> str:
    sections = [
        f"### {candidate.get('symbol')} - {candidate.get('name')}",
        str(payload["setup"]).strip(),
        "",
        *_factor_summary_block(candidate),
        "",
        *_factor_details_block(candidate),
        "",
        *_risk_details_block(candidate),
        "",
        *_setup_details_block(candidate),
        "",
        *_metric_block(candidate),
        "",
        "**Why it screens well:**",
        *[f"- {item}" for item in payload["why_it_screens_well"]],
        "",
        "**1-day to 1-week plan:**",
        *[f"- {item}" for item in payload["plan"]],
        "",
        "**Main risks:**",
        *[f"- {item}" for item in payload["risks"]],
        "",
        f"**Verdict:** {str(payload['verdict']).strip()} Not financial advice.",
    ]
    return "\n".join(sections)


def _parse_json_response(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _ollama_payload_is_valid(candidate: dict[str, Any], payload: dict[str, Any]) -> bool:
    required_fields = {"setup", "why_it_screens_well", "plan", "risks", "verdict", "metric_refs"}
    if not required_fields.issubset(payload):
        return False

    list_fields = ["why_it_screens_well", "plan", "risks", "metric_refs"]
    if not all(isinstance(payload.get(field), list) for field in list_fields):
        return False
    if not all(isinstance(payload.get(field), str) for field in ["setup", "verdict"]):
        return False

    metric_refs = {str(item) for item in payload["metric_refs"]}
    required_refs = {
        "return_1d",
        "return_5d",
        "return_10d",
        "return_20d",
        "volume_ratio_5d",
        "volume_ratio_20d",
        "volume_trend_5d_20d",
        "volume_persistence_5d",
        "volume_persistence_10d",
        "volume_z_score_20d",
        "up_volume_ratio_10d",
        "liquidity_tier",
        "rel_strength_spy_5d",
        "rel_strength_spy_10d",
        "rel_strength_spy_20d",
        "rel_strength_qqq_5d",
        "rel_strength_qqq_10d",
        "rel_strength_qqq_20d",
        "sector_relative_strength_10d",
        "sector_relative_strength_20d",
        "market_regime_score",
        "close_location_20d",
        "failed_gap_or_fade",
        "sma_5_20_ratio",
        "close_vs_sma_20",
        "up_day_ratio_5d",
        "rsi_14",
        "atr_14_pct",
        "risk_score",
        "confidence_score",
    }
    if not required_refs.issubset(metric_refs):
        return False

    combined = json.dumps(payload).lower()
    forbidden_forecasts = ["guaranteed", "will rise", "will go up", "prediction: up"]
    return not any(term in combined for term in forbidden_forecasts)


def build_short_term_prompt(candidate: dict[str, Any], rank: int) -> str:
    reasons = ", ".join(candidate.get("reasons") or [])
    allowed_observations = "\n".join(f"- {item}" for item in _allowed_observations(candidate))
    risk_observations = "\n".join(f"- {item}" for item in _risk_observations(candidate))
    factor_observations = "\n".join(
        f"- {item}"
        for item in [*_factor_summary_block(candidate)[1:], *_factor_details_block(candidate)[1:]]
    )
    return f"""
You are a cautious market research assistant. Return ONLY valid JSON using
the schema below. Use ONLY the facts below.

Rules:
- Do not invent news, catalysts, earnings dates, support/resistance levels, or prices.
- Do not mention moving averages, analyst ratings, macro news, or precise stop prices.
- Do not create new RSI thresholds; only use the current RSI fact or the provided risk notes.
- Do not say "buy" or "guaranteed"; use "candidate", "setup", and "watch".
- Do not present expected direction as a price prediction; describe only the conditional regime.
- Keep it practical for a short holding window, not long-term investing.
- Mention risk clearly using only the allowed risk notes.
- Include a simple invalidation idea: losing momentum or fading relative volume.
- Reference every required metric in metric_refs.

Candidate facts:
- Rank: {rank}
- Symbol: {candidate.get("symbol")}
- Name: {candidate.get("name")}
- Market: {candidate.get("market")}
- Exchange: {candidate.get("exchange")}
- Screener score: {candidate.get("score")}
- Current price: {_num(candidate.get("current_price"))}
- Market cap: {_market_cap(candidate.get("market_cap"))}
- 1-day return: {_pct(candidate.get("return_1d"))}
- 5-day return: {_pct(candidate.get("return_5d"))}
- 10-day return: {_pct(candidate.get("return_10d"))}
- 20-day return: {_pct(candidate.get("return_20d"))}
- Latest volume vs prior 5-day average: {_num(candidate.get("volume_ratio_5d"))}x
- Latest volume vs prior 20-day average: {_num(candidate.get("volume_ratio_20d"))}x
- 5-day volume trend vs 20-day average: {_num(candidate.get("volume_trend_5d_20d"))}x
- Elevated-volume persistence 5D: {_pct(candidate.get("volume_persistence_5d"))}
- Elevated-volume persistence 10D: {_pct(candidate.get("volume_persistence_10d"))}
- Latest volume z-score vs trailing 20 days: {_num(candidate.get("volume_z_score_20d"))}
- Liquidity tier: {candidate.get("liquidity_tier") or "n/a"}
- Dollar volume: {_market_cap(candidate.get("dollar_volume"))}
- Distance from 5-day high: {_pct(candidate.get("distance_from_5d_high"))}
- Distance from 5-day low: {_pct(candidate.get("distance_from_5d_low"))}
- Distance from 20-day high: {_pct(candidate.get("distance_from_20d_high"))}
- Distance from 20-day low: {_pct(candidate.get("distance_from_20d_low"))}
- SMA 5/20 trend ratio: {_pct(candidate.get("sma_5_20_ratio"))}
- Close vs SMA20: {_pct(candidate.get("close_vs_sma_20"))}
- Up-day ratio 5D: {_pct(candidate.get("up_day_ratio_5d"))}
- Up-day ratio 10D: {_pct(candidate.get("up_day_ratio_10d"))}
- Gap from previous close to latest open: {_pct(candidate.get("gap_1d"))}
- ATR 14 as pct of price: {_pct(candidate.get("atr_14_pct"))}
- RSI 14: {_num(candidate.get("rsi_14"))}
- 5-day relative strength vs SPY: {_pct(candidate.get("rel_strength_spy_5d"))}
- 5-day relative strength vs QQQ: {_pct(candidate.get("rel_strength_qqq_5d"))}
- 10-day relative strength vs SPY: {_pct(candidate.get("rel_strength_spy_10d"))}
- 10-day relative strength vs QQQ: {_pct(candidate.get("rel_strength_qqq_10d"))}
- 20-day relative strength vs SPY: {_pct(candidate.get("rel_strength_spy_20d"))}
- 20-day relative strength vs QQQ: {_pct(candidate.get("rel_strength_qqq_20d"))}
- 10-day relative strength vs sector peers: {_pct(candidate.get("sector_relative_strength_10d"))}
- 20-day relative strength vs sector peers: {_pct(candidate.get("sector_relative_strength_20d"))}
- Market regime: {_num(candidate.get("market_regime_score"))} ({candidate.get("market_regime_label") or "n/a"})
- Close location 1D/5D/20D: {_pct(candidate.get("close_location_1d"))} / {_pct(candidate.get("close_location_5d"))} / {_pct(candidate.get("close_location_20d"))}
- 10-day up/down volume ratio: {_num(candidate.get("up_volume_ratio_10d"))}x
- Failed gap or fade flag: {candidate.get("failed_gap_or_fade")}
- Setup type: {candidate.get("setup_type")}
- Opportunity score: {_num(candidate.get("opportunity_score"))}
- Risk score: {_num(candidate.get("risk_score"))}
- Risk level: {candidate.get("risk_level")}
- Confidence score: {_num(candidate.get("confidence_score"))}
- Regime label: {candidate.get("expected_direction")}
- Expected window: {candidate.get("expected_window")}
- Reason codes: {", ".join(candidate.get("reason_codes") or [])}
- Risk flags: {", ".join(candidate.get("risk_flags") or [])}
- Upcoming earnings days: {_num(candidate.get("upcoming_earnings_days"))}
- Valuation context: trailing P/E {_num(candidate.get("trailing_pe"))}, P/B {_num(candidate.get("price_to_book"))}
- Screener signals: {reasons}

Allowed observations to use:
{allowed_observations}

Factor model summary:
{factor_observations}

Allowed risk notes to use:
{risk_observations}

Required JSON schema:
{{
  "setup": "1-2 cautious sentences",
  "why_it_screens_well": ["2-4 fact-based bullets"],
  "plan": ["2-4 bullets focused on what to watch"],
  "risks": ["2-4 bullets using only allowed risk notes"],
  "verdict": "one cautious sentence",
  "metric_refs": ["return_1d", "return_5d", "return_10d", "return_20d", "volume_ratio_5d", "volume_ratio_20d", "volume_trend_5d_20d", "volume_persistence_5d", "volume_persistence_10d", "volume_z_score_20d", "up_volume_ratio_10d", "liquidity_tier", "rel_strength_spy_5d", "rel_strength_spy_10d", "rel_strength_spy_20d", "rel_strength_qqq_5d", "rel_strength_qqq_10d", "rel_strength_qqq_20d", "sector_relative_strength_10d", "sector_relative_strength_20d", "market_regime_score", "close_location_20d", "failed_gap_or_fade", "sma_5_20_ratio", "close_vs_sma_20", "up_day_ratio_5d", "rsi_14", "atr_14_pct", "risk_score", "confidence_score"]
}}
""".strip()


def generate_short_term_proposals(
    *,
    input_path: Path,
    output_markdown_path: Path,
    output_json_path: Path,
    output_summary_path: Path,
    model: str,
    top: int,
    use_ollama: bool = False,
) -> list[dict[str, Any]]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    candidates = payload.get("candidates", [])[:top]
    if not candidates:
        raise ValueError(f"No candidates found in {input_path}")

    client = OllamaClient(model=model) if use_ollama else None
    if client is not None and not client.is_available():
        print(
            f"Ollama model '{model}' is not available; using fact-only proposals. "
            f"Run 'ollama pull {model}' to enable it."
        )
        client = None

    proposals: list[dict[str, Any]] = []
    markdown_parts = [
        "# Short-Term Research Proposals",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"Model: `{model}`",
        f"Source: `{_display_path(input_path)}`",
        "",
        DISCLAIMER,
        "",
        *_metric_guide(),
    ]

    for rank, candidate in enumerate(candidates, start=1):
        print(f"Generating proposal {rank}/{len(candidates)}: {candidate.get('symbol')}")
        proposal = _deterministic_proposal(candidate)
        used_ollama = False
        if client is not None:
            prompt = build_short_term_prompt(candidate, rank)
            try:
                generated = client.generate(prompt)
            except requests.RequestException:
                generated = ""
            payload = _parse_json_response(generated) if generated else None
            if payload is not None and _ollama_payload_is_valid(candidate, payload):
                proposal = _format_ollama_json(candidate, payload)
                used_ollama = True
            else:
                print(
                    f"Using fact-only fallback for {candidate.get('symbol')} "
                    "because the local model output was unsafe or too broad."
                )
        proposals.append(
            {
                "rank": rank,
                "symbol": candidate.get("symbol"),
                "name": candidate.get("name"),
                "used_ollama": used_ollama,
                "proposal": proposal,
                "source_metrics": candidate,
            }
        )
        markdown_parts.append(proposal)
        markdown_parts.append("")
        markdown_parts.append("---")
        markdown_parts.append("")

    output_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_summary_path.parent.mkdir(parents=True, exist_ok=True)
    output_markdown_path.write_text("\n".join(markdown_parts).strip() + "\n", encoding="utf-8")
    output_json_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "model": model,
                "input": _display_path(input_path),
                "disclaimer": DISCLAIMER,
                "proposals": proposals,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_metrics_summary(candidates, output_summary_path)
    return proposals


SUMMARY_COLUMNS = [
    "rank",
    "symbol",
    "name",
    "market",
    "exchange",
    "score",
    "opportunity_score",
    "risk_score",
    "risk_level",
    "confidence_score",
    "expected_direction",
    "expected_window",
    "setup_type",
    "market_cap",
    "current_price",
    "return_1d",
    "return_5d",
    "return_10d",
    "return_20d",
    "rel_strength_spy_1d",
    "rel_strength_spy_5d",
    "rel_strength_spy_10d",
    "rel_strength_spy_20d",
    "rel_strength_qqq_1d",
    "rel_strength_qqq_5d",
    "rel_strength_qqq_10d",
    "rel_strength_qqq_20d",
    "sector_relative_strength_5d",
    "sector_relative_strength_10d",
    "sector_relative_strength_20d",
    "volume_ratio_5d",
    "volume_ratio_20d",
    "volume_trend_5d_20d",
    "volume_persistence_5d",
    "volume_persistence_10d",
    "volume_z_score_20d",
    "up_volume_ratio_10d",
    "liquidity_tier",
    "distance_from_5d_high",
    "distance_from_5d_low",
    "distance_from_20d_high",
    "distance_from_20d_low",
    "close_location_1d",
    "close_location_5d",
    "close_location_20d",
    "gap_1d",
    "failed_gap_or_fade",
    "sma_5_20_ratio",
    "close_vs_sma_20",
    "up_day_ratio_5d",
    "up_day_ratio_10d",
    "dollar_volume",
    "atr_14_pct",
    "rsi_14",
    "market_regime_score",
    "market_regime_label",
    "upcoming_earnings_days",
    "risk_flags",
    "risk_details",
    "reason_codes",
    "factor_scores",
    "factor_summaries",
    "factor_details",
    "setup_details",
]


def write_metrics_summary(candidates: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        for rank, candidate in enumerate(candidates, start=1):
            row = {column: candidate.get(column) for column in SUMMARY_COLUMNS}
            row["rank"] = rank
            row["risk_flags"] = "; ".join(candidate.get("risk_flags") or [])
            row["risk_details"] = json.dumps(candidate.get("risk_details") or {}, sort_keys=True)
            row["reason_codes"] = "; ".join(candidate.get("reason_codes") or [])
            row["factor_scores"] = json.dumps(candidate.get("factor_scores") or {}, sort_keys=True)
            row["factor_summaries"] = "; ".join(candidate.get("factor_summaries") or [])
            row["factor_details"] = json.dumps(candidate.get("factor_details") or {}, sort_keys=True)
            row["setup_details"] = json.dumps(candidate.get("setup_details") or {}, sort_keys=True)
            writer.writerow(row)
