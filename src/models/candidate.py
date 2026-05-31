from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class StockMetrics:
    symbol: str
    name: str
    sector: str
    industry: str
    market_cap: float | None
    trailing_pe: float | None
    forward_pe: float | None
    price_to_book: float | None
    peg_ratio: float | None
    revenue_growth: float | None
    debt_to_equity: float | None
    free_cashflow: float | None
    current_price: float | None
    market: str = "US / S&P 500"
    exchange: str = "NYSE/Nasdaq"
    upcoming_earnings_days: float | None = None
    return_1d: float | None = None
    return_5d: float | None = None
    return_10d: float | None = None
    return_20d: float | None = None
    gap_1d: float | None = None
    volume_ratio_5d: float | None = None
    volume_ratio_20d: float | None = None
    volume_trend_5d_20d: float | None = None
    distance_from_5d_high: float | None = None
    distance_from_5d_low: float | None = None
    distance_from_20d_high: float | None = None
    distance_from_20d_low: float | None = None
    sma_5_20_ratio: float | None = None
    close_vs_sma_20: float | None = None
    up_day_ratio_5d: float | None = None
    up_day_ratio_10d: float | None = None
    dollar_volume: float | None = None
    atr_14_pct: float | None = None
    rsi_14: float | None = None
    rel_strength_spy_1d: float | None = None
    rel_strength_spy_5d: float | None = None
    rel_strength_spy_10d: float | None = None
    rel_strength_spy_20d: float | None = None
    rel_strength_qqq_1d: float | None = None
    rel_strength_qqq_5d: float | None = None
    rel_strength_qqq_10d: float | None = None
    rel_strength_qqq_20d: float | None = None
    sector_relative_strength_5d: float | None = None
    sector_relative_strength_10d: float | None = None
    sector_relative_strength_20d: float | None = None
    volume_persistence_5d: float | None = None
    volume_persistence_10d: float | None = None
    volume_z_score_20d: float | None = None
    up_volume_ratio_10d: float | None = None
    liquidity_tier: str | None = None
    close_location_1d: float | None = None
    close_location_5d: float | None = None
    close_location_20d: float | None = None
    market_regime_score: float | None = None
    market_regime_label: str | None = None
    failed_gap_or_fade: bool | None = None
    expected_direction: str | None = None
    expected_window: str | None = None
    confidence_score: float | None = None
    reason_codes: list[str] | None = None
    factor_scores: dict[str, float] | None = None
    factor_summaries: list[str] | None = None
    factor_details: dict[str, Any] | None = None
    risk_details: dict[str, Any] | None = None
    setup_details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScoredCandidate:
    symbol: str
    name: str
    sector: str
    market: str
    exchange: str
    score: float
    trailing_pe: float | None
    price_to_book: float | None
    peg_ratio: float | None
    market_cap: float | None
    current_price: float | None
    graham_match: bool
    reasons: list[str]
    opportunity_score: float | None = None
    risk_score: float | None = None
    risk_level: str | None = None
    setup_type: str | None = None
    risk_flags: list[str] | None = None
    upcoming_earnings_days: float | None = None
    return_1d: float | None = None
    return_5d: float | None = None
    return_10d: float | None = None
    return_20d: float | None = None
    gap_1d: float | None = None
    volume_ratio_5d: float | None = None
    volume_ratio_20d: float | None = None
    volume_trend_5d_20d: float | None = None
    distance_from_5d_high: float | None = None
    distance_from_5d_low: float | None = None
    distance_from_20d_high: float | None = None
    distance_from_20d_low: float | None = None
    sma_5_20_ratio: float | None = None
    close_vs_sma_20: float | None = None
    up_day_ratio_5d: float | None = None
    up_day_ratio_10d: float | None = None
    dollar_volume: float | None = None
    atr_14_pct: float | None = None
    rsi_14: float | None = None
    rel_strength_spy_1d: float | None = None
    rel_strength_spy_5d: float | None = None
    rel_strength_spy_10d: float | None = None
    rel_strength_spy_20d: float | None = None
    rel_strength_qqq_1d: float | None = None
    rel_strength_qqq_5d: float | None = None
    rel_strength_qqq_10d: float | None = None
    rel_strength_qqq_20d: float | None = None
    sector_relative_strength_5d: float | None = None
    sector_relative_strength_10d: float | None = None
    sector_relative_strength_20d: float | None = None
    volume_persistence_5d: float | None = None
    volume_persistence_10d: float | None = None
    volume_z_score_20d: float | None = None
    up_volume_ratio_10d: float | None = None
    liquidity_tier: str | None = None
    close_location_1d: float | None = None
    close_location_5d: float | None = None
    close_location_20d: float | None = None
    market_regime_score: float | None = None
    market_regime_label: str | None = None
    failed_gap_or_fade: bool | None = None
    expected_direction: str | None = None
    expected_window: str | None = None
    confidence_score: float | None = None
    reason_codes: list[str] | None = None
    factor_scores: dict[str, float] | None = None
    factor_summaries: list[str] | None = None
    factor_details: dict[str, Any] | None = None
    risk_details: dict[str, Any] | None = None
    setup_details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
