from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent.short_term_proposals import _deterministic_proposal
from src.models.candidate import StockMetrics
from src.screen.scorer import _short_term_risk


class SmokeTests(unittest.TestCase):
    def test_short_term_risk_has_nonzero_floor(self) -> None:
        row = StockMetrics(
            symbol="TEST",
            name="Test Company",
            sector="Technology",
            industry="Software",
            market_cap=500_000_000,
            trailing_pe=20.0,
            forward_pe=None,
            price_to_book=3.0,
            peg_ratio=None,
            revenue_growth=None,
            debt_to_equity=None,
            free_cashflow=None,
            current_price=10.0,
        )

        risk_score, risk_flags = _short_term_risk(row)

        self.assertGreaterEqual(risk_score, 0.10)
        self.assertIn("low visible short-term risk flags", risk_flags)

    def test_deterministic_proposal_does_not_need_ollama(self) -> None:
        proposal = _deterministic_proposal(
            {
                "symbol": "TEST",
                "name": "Test Company",
                "market": "US / S&P 500",
                "exchange": "NYSE/Nasdaq",
                "score": 0.75,
                "opportunity_score": 0.80,
                "risk_score": 0.10,
                "risk_level": "low",
                "confidence_score": 0.84,
                "setup_type": "trend confirmation",
                "expected_direction": "up",
                "expected_window": "1d-5d",
                "risk_flags": ["low visible short-term risk flags"],
                "reason_codes": ["COMPOSITE_SCORE"],
            }
        )

        self.assertIn("### TEST - Test Company", proposal)
        self.assertIn("Risk score is 0.10 (low)", proposal)
        self.assertIn("Market: US / S&P 500", proposal)


if __name__ == "__main__":
    unittest.main()
