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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
