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
    upcoming_earnings_days: float | None = None
    return_1d: float | None = None
    return_5d: float | None = None
    return_20d: float | None = None
    gap_1d: float | None = None
    volume_ratio_5d: float | None = None
    volume_ratio_20d: float | None = None
    distance_from_5d_high: float | None = None
    distance_from_5d_low: float | None = None
    atr_14_pct: float | None = None
    rsi_14: float | None = None
    rel_strength_spy_1d: float | None = None
    rel_strength_spy_5d: float | None = None
    rel_strength_qqq_1d: float | None = None
    rel_strength_qqq_5d: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScoredCandidate:
    symbol: str
    name: str
    sector: str
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
    setup_type: str | None = None
    risk_flags: list[str] | None = None
    upcoming_earnings_days: float | None = None
    return_1d: float | None = None
    return_5d: float | None = None
    return_20d: float | None = None
    gap_1d: float | None = None
    volume_ratio_5d: float | None = None
    volume_ratio_20d: float | None = None
    distance_from_5d_high: float | None = None
    distance_from_5d_low: float | None = None
    atr_14_pct: float | None = None
    rsi_14: float | None = None
    rel_strength_spy_1d: float | None = None
    rel_strength_spy_5d: float | None = None
    rel_strength_qqq_1d: float | None = None
    rel_strength_qqq_5d: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
