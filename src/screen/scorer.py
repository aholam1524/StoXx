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
    if value is None or value <= 0 or sector_median is None or sector_median <= 0:
        return 0.0
    return sector_median / value


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
            )
        )

    results.sort(key=lambda c: c.score, reverse=True)
    return results
