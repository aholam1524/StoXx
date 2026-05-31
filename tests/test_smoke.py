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
from scripts.evaluate_runs import (
    _validate_config_on_run,
    bucket_risk,
    build_calibration_suggestions,
    summarize_group,
)


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
                "setup_details": {
                    "best_setup_score": "trend_confirmation",
                    "best_score": 0.82,
                    "setups": {"trend_confirmation": {"score": 0.82}},
                },
                "expected_direction": "bullish regime if conditions persist",
                "expected_window": "1d-5d",
                "sector_relative_strength_10d": 0.03,
                "sector_relative_strength_20d": 0.04,
                "market_regime_score": 0.70,
                "market_regime_label": "supportive",
                "close_location_1d": 0.75,
                "close_location_5d": 0.82,
                "close_location_20d": 0.88,
                "up_volume_ratio_10d": 1.6,
                "failed_gap_or_fade": False,
                "risk_flags": ["controlled volatility: ATR/gap/1D move are not elevated"],
                "risk_details": {
                    "components": {
                        "extension": {
                            "label": "extension risk",
                            "score": 0.10,
                            "weight": 0.33,
                            "contribution": 0.03,
                            "severity": "low",
                            "evidence": "RSI 55.00",
                            "metrics": [
                                {
                                    "metric": "rsi_14",
                                    "raw": 55.0,
                                    "low": 60.0,
                                    "high": 80.0,
                                    "score": 0.0,
                                }
                            ],
                        }
                    }
                },
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
        self.assertIn("<summary><strong>Risk details</strong>", proposal)
        self.assertIn("**Setup diagnostics:**", proposal)
        self.assertIn("Market regime: 0.70 (supportive)", proposal)
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
            up_volume_ratio_10d=1.7,
            liquidity_tier="medium",
            close_location_1d=0.80,
            close_location_5d=0.90,
            close_location_20d=0.85,
            market_regime_score=0.65,
            market_regime_label="supportive",
            failed_gap_or_fade=False,
            atr_14_pct=0.03,
            rsi_14=61.0,
            rel_strength_spy_5d=0.03,
            rel_strength_qqq_5d=0.02,
            rel_strength_spy_10d=0.04,
            rel_strength_qqq_10d=0.03,
            rel_strength_spy_20d=0.05,
            rel_strength_qqq_20d=0.04,
            sector_relative_strength_5d=0.02,
            sector_relative_strength_10d=0.03,
            sector_relative_strength_20d=0.04,
        )

        [candidate] = score_short_term_candidates(
            [row],
            scoring={"factor_weights": {"trend": 0.25, "momentum": 0.25, "relative_strength": 0.20, "participation": 0.20, "extension": 0.10}},
            filters={},
        )

        self.assertIsNotNone(candidate.factor_scores)
        self.assertIsNotNone(candidate.factor_details)
        self.assertIsNotNone(candidate.risk_details)
        self.assertIsNotNone(candidate.setup_details)
        assert candidate.factor_scores is not None
        assert candidate.factor_details is not None
        assert candidate.risk_details is not None
        assert candidate.setup_details is not None
        for score in candidate.factor_scores.values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

        self.assertIn("formula", candidate.factor_details["trend"])
        self.assertIn("components", candidate.factor_details["trend"])
        self.assertIn("components", candidate.risk_details)
        self.assertIn("extension", candidate.risk_details["components"])
        self.assertIn("sector_relative_strength_10d", [item["metric"] for item in candidate.factor_details["relative_strength"]["components"]])
        self.assertIn("up_volume_ratio_10d", [item["metric"] for item in candidate.factor_details["participation"]["components"]])
        self.assertEqual(candidate.setup_details["best_setup_score"], "trend_confirmation")
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

    def test_evaluate_run_risk_buckets_match_report_ranges(self) -> None:
        self.assertEqual(bucket_risk(0.24), "low")
        self.assertEqual(bucket_risk(0.25), "medium")
        self.assertEqual(bucket_risk(0.49), "medium")
        self.assertEqual(bucket_risk(0.50), "high")

    def test_evaluation_summary_tracks_relative_and_downside_stats(self) -> None:
        summary = summarize_group(
            [
                {
                    "forward_return_1d": 0.01,
                    "forward_return_5d": 0.03,
                    "relative_spy_forward_1d": 0.005,
                    "relative_spy_forward_5d": 0.02,
                    "relative_qqq_forward_1d": 0.002,
                    "relative_qqq_forward_5d": 0.01,
                },
                {
                    "forward_return_1d": -0.01,
                    "forward_return_5d": -0.03,
                    "relative_spy_forward_1d": -0.005,
                    "relative_spy_forward_5d": -0.02,
                    "relative_qqq_forward_1d": -0.002,
                    "relative_qqq_forward_5d": -0.01,
                },
            ]
        )

        self.assertEqual(summary["hit_rate_vs_spy_5d"], 0.5)
        self.assertEqual(summary["downside_rate_5d"], 0.5)
        self.assertAlmostEqual(summary["median_forward_return_5d"], 0.0)

    def test_calibration_suggestions_require_sample_size(self) -> None:
        evaluations = [
            {
                "rank": index + 1,
                "setup_type": "trend confirmation",
                "risk_score": 0.1,
                "reason_codes": ["TREND_CONSTRUCTIVE"],
                "risk_flags": [],
                "factor_scores": {"trend": 0.8},
                "risk_details": {},
                "forward_return_1d": 0.01,
                "forward_return_5d": 0.02,
                "relative_spy_forward_1d": 0.01,
                "relative_spy_forward_5d": 0.02,
                "relative_qqq_forward_1d": 0.01,
                "relative_qqq_forward_5d": 0.02,
            }
            for index in range(5)
        ]

        suggestions = build_calibration_suggestions(evaluations, min_samples=5)

        self.assertTrue(suggestions["suggested_adjustments"])
        self.assertEqual(suggestions["suggested_adjustments"][0]["sample_size"], 5)

    def test_validate_config_compares_rescored_run_candidates(self) -> None:
        source_candidates = [
            {
                "symbol": "STRONG",
                "name": "Strong",
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
                "return_1d": 0.02,
                "return_5d": 0.08,
                "return_10d": 0.10,
                "return_20d": 0.12,
                "rel_strength_spy_10d": 0.08,
                "rel_strength_qqq_10d": 0.08,
                "rel_strength_spy_20d": 0.10,
                "rel_strength_qqq_20d": 0.10,
            },
            {
                "symbol": "WEAK",
                "name": "Weak",
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
                "return_5d": 0.01,
                "return_10d": 0.01,
                "return_20d": 0.01,
                "rel_strength_spy_10d": -0.02,
                "rel_strength_qqq_10d": -0.02,
                "rel_strength_spy_20d": -0.02,
                "rel_strength_qqq_20d": -0.02,
            },
        ]
        evaluations = [
            {
                "symbol": "WEAK",
                "forward_return_1d": 0.0,
                "forward_return_5d": -0.01,
                "relative_spy_forward_1d": 0.0,
                "relative_spy_forward_5d": -0.02,
                "relative_qqq_forward_1d": 0.0,
                "relative_qqq_forward_5d": -0.02,
            },
            {
                "symbol": "STRONG",
                "forward_return_1d": 0.0,
                "forward_return_5d": 0.03,
                "relative_spy_forward_1d": 0.0,
                "relative_spy_forward_5d": 0.02,
                "relative_qqq_forward_1d": 0.0,
                "relative_qqq_forward_5d": 0.02,
            },
        ]

        validation = _validate_config_on_run(
            source_candidates=source_candidates,
            evaluations=evaluations,
            config={"short_term_scoring": {"factor_weights": {}}},
        )

        self.assertEqual(validation["status"], "ok")
        self.assertEqual(validation["rescored_symbols"][0], "STRONG")

    def test_configured_risk_weights_affect_candidate_risk_details(self) -> None:
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
            return_1d=0.01,
            return_5d=0.14,
            return_10d=0.20,
            return_20d=0.18,
            distance_from_20d_low=0.24,
            distance_from_20d_high=-0.01,
            atr_14_pct=0.02,
            rsi_14=68.0,
            dollar_volume=250_000_000,
            liquidity_tier="high",
            volume_persistence_10d=0.8,
            close_vs_sma_20=0.04,
            sma_5_20_ratio=0.03,
            up_day_ratio_10d=0.7,
        )

        [candidate] = score_short_term_candidates(
            [row],
            scoring={
                "factor_weights": {},
                "risk_weights": {
                    "extension": 1.0,
                    "volatility": 0.0,
                    "liquidity": 0.0,
                    "trend_failure": 0.0,
                    "event": 0.0,
                },
            },
            filters={},
        )

        assert candidate.risk_details is not None
        self.assertEqual(candidate.risk_details["weights"]["extension"], 1.0)
        self.assertGreater(candidate.risk_score or 0.0, 0.30)

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
