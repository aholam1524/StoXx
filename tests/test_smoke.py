from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent.short_term_proposals import _deterministic_proposal
from src.models.candidate import StockMetrics
from src.screen.scorer import _percentile_rank, _short_term_risk, score_short_term_candidates


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
        self.assertIn("controlled volatility: ATR/gap/1D move are not elevated", risk_flags)
        self.assertIn("no near-term earnings flag", risk_flags)

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
                "expected_direction": "bullish regime if conditions persist",
                "expected_window": "1d-5d",
                "risk_flags": ["controlled volatility: ATR/gap/1D move are not elevated"],
                "reason_codes": ["TREND_CONSTRUCTIVE"],
                "factor_scores": {
                    "trend": 0.75,
                    "momentum": 0.70,
                    "relative_strength": 0.65,
                    "participation": 0.60,
                    "extension": 0.80,
                },
                "factor_summaries": ["Trend factor is constructive."],
                "factor_details": {
                    "trend": {
                        "formula": "1.00 * pct_rank(return_20d)",
                        "components": [
                            {
                                "metric": "return_20d",
                                "raw": 0.12,
                                "percentile": 0.8,
                                "z_score": 1.1,
                                "weight": 1.0,
                                "score": 0.8,
                            }
                        ],
                    }
                },
            }
        )

        self.assertIn("### TEST - Test Company", proposal)
        self.assertIn("Risk score is 0.10 (low)", proposal)
        self.assertIn("**Snapshot:** US / S&P 500", proposal)
        self.assertIn("<summary><strong>Formula details</strong>", proposal)
        self.assertIn("pct_rank(return_20d)", proposal)
        self.assertIn("**Regime:** bullish regime if conditions persist", proposal)
        self.assertNotIn("**Prediction:** up", proposal)

    def test_percentile_rank_is_bounded_and_monotonic(self) -> None:
        values = [0.01, 0.03, 0.05, 0.08]
        ranks = [_percentile_rank(value, values) for value in values]

        for rank in ranks:
            self.assertGreaterEqual(rank, 0.0)
            self.assertLessEqual(rank, 1.0)
        self.assertEqual(ranks, sorted(ranks))
        self.assertGreater(ranks[-1], ranks[0])

    def test_short_term_scoring_uses_grouped_factor_codes(self) -> None:
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
            return_1d=0.02,
            return_5d=0.06,
            return_10d=0.09,
            return_20d=0.10,
            volume_ratio_5d=1.8,
            volume_ratio_20d=1.6,
            volume_trend_5d_20d=1.2,
            distance_from_5d_high=-0.01,
            distance_from_20d_high=-0.02,
            distance_from_20d_low=0.12,
            sma_5_20_ratio=0.03,
            close_vs_sma_20=0.05,
            up_day_ratio_5d=0.8,
            up_day_ratio_10d=0.7,
            dollar_volume=50_000_000,
            volume_persistence_5d=0.8,
            volume_persistence_10d=0.7,
            volume_z_score_20d=1.4,
            liquidity_tier="medium",
            atr_14_pct=0.03,
            rsi_14=61.0,
            rel_strength_spy_5d=0.03,
            rel_strength_qqq_5d=0.02,
            rel_strength_spy_10d=0.04,
            rel_strength_qqq_10d=0.03,
            rel_strength_spy_20d=0.05,
            rel_strength_qqq_20d=0.04,
        )

        [candidate] = score_short_term_candidates(
            [row],
            scoring={"factor_weights": {"trend": 0.25, "momentum": 0.25, "relative_strength": 0.20, "participation": 0.20, "extension": 0.10}},
            filters={},
        )

        self.assertIsNotNone(candidate.factor_scores)
        self.assertIsNotNone(candidate.factor_details)
        assert candidate.factor_scores is not None
        assert candidate.factor_details is not None
        for score in candidate.factor_scores.values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

        self.assertIn("formula", candidate.factor_details["trend"])
        self.assertIn("components", candidate.factor_details["trend"])
        self.assertTrue(any("volume z-score" in item for item in candidate.factor_summaries or []))
        self.assertTrue(any("liquidity tier medium" in item for item in candidate.factor_summaries or []))
        self.assertIn("TREND_CONSTRUCTIVE", candidate.reason_codes)
        self.assertIn("MOMENTUM_POSITIVE", candidate.reason_codes)
        self.assertNotIn("MOMENTUM_5D_POSITIVE", candidate.reason_codes)
        self.assertLessEqual(len(candidate.reason_codes or []), 6)

    def test_near_threshold_extension_gets_above_floor_risk(self) -> None:
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
            return_1d=0.03,
            return_5d=0.14,
            return_10d=0.21,
            return_20d=0.15,
            distance_from_20d_high=-0.01,
            distance_from_20d_low=0.24,
            atr_14_pct=0.04,
            rsi_14=66.0,
            dollar_volume=200_000_000,
            liquidity_tier="high",
            volume_persistence_10d=0.8,
            close_vs_sma_20=0.04,
            sma_5_20_ratio=0.03,
            up_day_ratio_10d=0.7,
        )

        risk_score, risk_flags = _short_term_risk(row)

        self.assertGreater(risk_score, 0.25)
        self.assertTrue(any("extension risk" in flag for flag in risk_flags))

    def test_thin_liquidity_increases_risk(self) -> None:
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
            dollar_volume=1_000_000,
            liquidity_tier="thin",
            volume_persistence_10d=0.1,
        )

        risk_score, risk_flags = _short_term_risk(row)

        self.assertGreater(risk_score, 0.10)
        self.assertTrue(any("liquidity/participation risk" in flag for flag in risk_flags))

    def test_earnings_today_increases_event_risk(self) -> None:
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
            upcoming_earnings_days=0.0,
        )

        risk_score, risk_flags = _short_term_risk(row)

        self.assertGreater(risk_score, 0.10)
        self.assertTrue(any("event risk" in flag for flag in risk_flags))

    def test_calm_liquid_candidate_stays_lower_risk_with_evidence(self) -> None:
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
            return_1d=0.005,
            return_5d=0.02,
            return_10d=0.03,
            return_20d=0.04,
            gap_1d=0.001,
            atr_14_pct=0.02,
            rsi_14=55.0,
            dollar_volume=250_000_000,
            liquidity_tier="high",
            volume_persistence_10d=0.7,
            close_vs_sma_20=0.02,
            sma_5_20_ratio=0.01,
            up_day_ratio_10d=0.6,
        )

        risk_score, risk_flags = _short_term_risk(row)

        self.assertLess(risk_score, 0.25)
        self.assertIn("controlled volatility: ATR/gap/1D move are not elevated", risk_flags)

    def test_relative_strength_rewards_10d_20d_outperformance(self) -> None:
        base = {
            "sector": "Technology",
            "industry": "Software",
            "market_cap": 500_000_000,
            "trailing_pe": 20.0,
            "forward_pe": None,
            "price_to_book": 3.0,
            "peg_ratio": None,
            "revenue_growth": None,
            "debt_to_equity": None,
            "free_cashflow": None,
            "current_price": 10.0,
            "return_1d": 0.01,
            "return_5d": 0.03,
            "return_10d": 0.06,
            "return_20d": 0.08,
            "rel_strength_spy_5d": 0.00,
            "rel_strength_qqq_5d": 0.00,
        }
        strong = StockMetrics(
            symbol="STRONG",
            name="Strong RS",
            rel_strength_spy_10d=0.08,
            rel_strength_qqq_10d=0.07,
            rel_strength_spy_20d=0.10,
            rel_strength_qqq_20d=0.09,
            **base,
        )
        weak = StockMetrics(
            symbol="WEAK",
            name="Weak RS",
            rel_strength_spy_10d=-0.02,
            rel_strength_qqq_10d=-0.03,
            rel_strength_spy_20d=-0.01,
            rel_strength_qqq_20d=-0.02,
            **base,
        )

        candidates = score_short_term_candidates([strong, weak], scoring={"factor_weights": {}}, filters={})
        by_symbol = {candidate.symbol: candidate for candidate in candidates}

        assert by_symbol["STRONG"].factor_scores is not None
        assert by_symbol["WEAK"].factor_scores is not None
        self.assertGreater(
            by_symbol["STRONG"].factor_scores["relative_strength"],
            by_symbol["WEAK"].factor_scores["relative_strength"],
        )

    def test_rsi_above_70_adds_extension_risk(self) -> None:
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
            rsi_14=72.0,
        )

        risk_score, risk_flags = _short_term_risk(row)

        self.assertGreater(risk_score, 0.10)
        self.assertTrue(any("extension risk" in flag for flag in risk_flags))


if __name__ == "__main__":
    unittest.main()
