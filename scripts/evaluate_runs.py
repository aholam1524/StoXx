#!/usr/bin/env python3
"""Evaluate historical proposal runs against 1-day and 5-day forward returns."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from dataclasses import fields
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.network import configure_ssl  # noqa: E402
from src.models.candidate import StockMetrics  # noqa: E402
from src.screen.scorer import score_short_term_candidates  # noqa: E402

configure_ssl()

import pandas as pd  # noqa: E402
import yfinance as yf  # noqa: E402

BENCHMARKS = ("SPY", "QQQ")
MIN_CALIBRATION_SAMPLES = 5
STOCK_METRIC_FIELDS = {field.name for field in fields(StockMetrics)}


def parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def safe_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result:
        return None
    return result


def symbol_frame(history: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if isinstance(history.columns, pd.MultiIndex):
        if symbol not in history.columns.get_level_values(1):
            return pd.DataFrame()
        return history.xs(symbol, axis=1, level=1).dropna(how="all")
    return history.dropna(how="all")


def forward_close(closes: pd.Series, as_of: datetime, trading_days: int) -> float | None:
    future = closes[closes.index.date > as_of.date()]
    if len(future) < trading_days:
        return None
    return safe_float(future.iloc[trading_days - 1])


def last_close_on_or_before(closes: pd.Series, as_of: datetime) -> float | None:
    prior = closes[closes.index.date <= as_of.date()]
    if prior.empty:
        return None
    return safe_float(prior.iloc[-1])


def pct_return(entry: float | None, exit_price: float | None) -> float | None:
    if entry is None or exit_price is None or entry <= 0:
        return None
    return exit_price / entry - 1


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def hit_rate(values: list[float]) -> float | None:
    return sum(1 for value in values if value > 0) / len(values) if values else None


def downside_rate(values: list[float], threshold: float = -0.02) -> float | None:
    return sum(1 for value in values if value <= threshold) / len(values) if values else None


def bucket_risk(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value < 0.25:
        return "low"
    if value < 0.50:
        return "medium"
    return "high"


def summarize_group(items: list[dict[str, Any]]) -> dict[str, Any]:
    forward_1d = [item["forward_return_1d"] for item in items if item["forward_return_1d"] is not None]
    forward_5d = [item["forward_return_5d"] for item in items if item["forward_return_5d"] is not None]
    rel_spy_1d = [item["relative_spy_forward_1d"] for item in items if item["relative_spy_forward_1d"] is not None]
    rel_spy_5d = [item["relative_spy_forward_5d"] for item in items if item["relative_spy_forward_5d"] is not None]
    rel_qqq_1d = [item["relative_qqq_forward_1d"] for item in items if item["relative_qqq_forward_1d"] is not None]
    rel_qqq_5d = [item["relative_qqq_forward_5d"] for item in items if item["relative_qqq_forward_5d"] is not None]
    return {
        "count": len(items),
        "hit_rate_1d": hit_rate(forward_1d),
        "hit_rate_5d": hit_rate(forward_5d),
        "hit_rate_vs_spy_1d": hit_rate(rel_spy_1d),
        "hit_rate_vs_spy_5d": hit_rate(rel_spy_5d),
        "hit_rate_vs_qqq_1d": hit_rate(rel_qqq_1d),
        "hit_rate_vs_qqq_5d": hit_rate(rel_qqq_5d),
        "avg_forward_return_1d": mean(forward_1d),
        "avg_forward_return_5d": mean(forward_5d),
        "median_forward_return_1d": median(forward_1d),
        "median_forward_return_5d": median(forward_5d),
        "downside_rate_5d": downside_rate(forward_5d),
        "avg_relative_spy_forward_1d": mean(rel_spy_1d),
        "avg_relative_spy_forward_5d": mean(rel_spy_5d),
        "median_relative_spy_forward_5d": median(rel_spy_5d),
        "avg_relative_qqq_forward_1d": mean(rel_qqq_1d),
        "avg_relative_qqq_forward_5d": mean(rel_qqq_5d),
    }


def _rank_bucket(rank: int | None) -> str:
    if rank is None:
        return "unknown"
    if rank <= 3:
        return "top_1_3"
    if rank <= 5:
        return "top_4_5"
    return "top_6_plus"


def _factor_bucket(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score >= 0.70:
        return "strong"
    if score >= 0.45:
        return "mixed"
    return "weak"


def _candidate_groups(item: dict[str, Any]) -> list[str]:
    groups = [
        f"setup_type:{item.get('setup_type') or 'unknown'}",
        f"risk_bucket:{bucket_risk(item.get('risk_score'))}",
        f"rank_bucket:{_rank_bucket(item.get('rank'))}",
    ]
    for code in item.get("reason_codes") or []:
        groups.append(f"reason_code:{code}")
    for flag in item.get("risk_flags") or []:
        groups.append(f"risk_flag:{flag}")

    factor_scores = item.get("factor_scores") or {}
    if isinstance(factor_scores, dict):
        for name, score in factor_scores.items():
            groups.append(f"factor:{name}:{_factor_bucket(safe_float(score))}")

    setup_details = item.get("setup_details") or {}
    if isinstance(setup_details, dict):
        for name, payload in setup_details.items():
            if isinstance(payload, dict):
                groups.append(f"setup_score:{name}:{_factor_bucket(safe_float(payload.get('score')))}")

    risk_components = (item.get("risk_details") or {}).get("components") or {}
    if isinstance(risk_components, dict):
        for name, component in risk_components.items():
            if isinstance(component, dict):
                severity = component.get("severity")
                if severity in {"moderate", "high"}:
                    groups.append(f"risk_component:{name}:{severity}")
    return groups


def build_calibration_suggestions(
    evaluations: list[dict[str, Any]],
    *,
    min_samples: int = MIN_CALIBRATION_SAMPLES,
) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in evaluations:
        for group in _candidate_groups(item):
            groups[group].append(item)

    group_stats = {
        group: summarize_group(items)
        for group, items in groups.items()
        if len(items) >= min_samples
    }

    suggested_adjustments: list[dict[str, Any]] = []
    for group, stats in group_stats.items():
        avg_rel = stats.get("avg_relative_spy_forward_5d")
        hit_rel = stats.get("hit_rate_vs_spy_5d")
        if avg_rel is None:
            continue
        if avg_rel > 0.01:
            suggested_adjustments.append(
                {
                    "signal": group,
                    "suggestion": "increase weight or reduce penalty",
                    "reason": "positive average 5-day forward return vs SPY",
                    "sample_size": stats["count"],
                    "avg_relative_spy_forward_5d": avg_rel,
                    "hit_rate_vs_spy_5d": hit_rel,
                }
            )
        elif avg_rel < -0.01:
            suggested_adjustments.append(
                {
                    "signal": group,
                    "suggestion": "decrease weight or increase penalty",
                    "reason": "negative average 5-day forward return vs SPY",
                    "sample_size": stats["count"],
                    "avg_relative_spy_forward_5d": avg_rel,
                    "hit_rate_vs_spy_5d": hit_rel,
                }
            )

    return {
        "group_stats": group_stats,
        "suggested_adjustments": sorted(
            suggested_adjustments,
            key=lambda item: abs(item["avg_relative_spy_forward_5d"]),
            reverse=True,
        ),
        "min_samples": min_samples,
        "note": "Use these suggestions to manually tune config.yaml after enough completed runs exist.",
    }


def _stock_metrics_from_candidate(candidate: dict[str, Any]) -> StockMetrics:
    values = {
        name: candidate.get(name)
        for name in STOCK_METRIC_FIELDS
        if name in candidate
    }
    values.setdefault("symbol", candidate.get("symbol"))
    values.setdefault("name", candidate.get("name") or candidate.get("symbol") or "Unknown")
    values.setdefault("sector", candidate.get("sector") or "Unknown")
    values.setdefault("industry", candidate.get("industry") or "Unknown")
    values.setdefault("market_cap", candidate.get("market_cap"))
    values.setdefault("trailing_pe", candidate.get("trailing_pe"))
    values.setdefault("forward_pe", candidate.get("forward_pe"))
    values.setdefault("price_to_book", candidate.get("price_to_book"))
    values.setdefault("peg_ratio", candidate.get("peg_ratio"))
    values.setdefault("revenue_growth", candidate.get("revenue_growth"))
    values.setdefault("debt_to_equity", candidate.get("debt_to_equity"))
    values.setdefault("free_cashflow", candidate.get("free_cashflow"))
    values.setdefault("current_price", candidate.get("current_price"))
    return StockMetrics(**values)


def _validate_config_on_run(
    *,
    source_candidates: list[dict[str, Any]],
    evaluations: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    if not source_candidates:
        return {"status": "skipped", "reason": "no source candidates"}

    rows = [_stock_metrics_from_candidate(candidate) for candidate in source_candidates]
    rescored = score_short_term_candidates(
        rows,
        scoring=config.get("short_term_scoring", {}),
        filters={
            **config.get("filters", {}),
            "min_market_cap": config.get("min_market_cap"),
            "max_market_cap": config.get("max_market_cap"),
        },
    )
    by_symbol = {item["symbol"]: item for item in evaluations}
    original_symbols = [item["symbol"] for item in evaluations]
    rescored_symbols = [candidate.symbol for candidate in rescored[:len(original_symbols)]]

    original_items = [by_symbol[symbol] for symbol in original_symbols if symbol in by_symbol]
    rescored_items = [by_symbol[symbol] for symbol in rescored_symbols if symbol in by_symbol]
    original_summary = summarize_group(original_items)
    rescored_summary = summarize_group(rescored_items)
    original_avg = original_summary.get("avg_relative_spy_forward_5d")
    rescored_avg = rescored_summary.get("avg_relative_spy_forward_5d")
    return {
        "status": "ok",
        "original_symbols": original_symbols,
        "rescored_symbols": rescored_symbols,
        "original_summary": original_summary,
        "rescored_summary": rescored_summary,
        "delta_avg_relative_spy_forward_5d": (
            rescored_avg - original_avg
            if rescored_avg is not None and original_avg is not None
            else None
        ),
        "note": "Compares a proposed config against stored run candidates using already-known forward returns.",
    }


def evaluate_run(run_dir: Path, *, validation_config: dict[str, Any] | None = None) -> dict[str, Any]:
    screen_path = run_dir / "screen_results.json"
    if not screen_path.exists():
        raise FileNotFoundError(f"Missing {screen_path}")

    payload = json.loads(screen_path.read_text(encoding="utf-8"))
    generated_at = parse_datetime(payload["generated_at"])
    candidates = payload.get("candidates", [])
    symbols = [candidate["symbol"] for candidate in candidates]
    download_symbols = sorted(set(symbols + list(BENCHMARKS)))
    start = (generated_at - timedelta(days=10)).date().isoformat()
    end = (datetime.now(timezone.utc) + timedelta(days=8)).date().isoformat()

    history = yf.download(
        download_symbols,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    if history.empty:
        raise RuntimeError("No price history returned for evaluation")

    benchmark_forward: dict[str, dict[str, float | None]] = {}
    for benchmark in BENCHMARKS:
        frame = symbol_frame(history, benchmark)
        closes = frame["Close"].dropna().astype(float) if "Close" in frame else pd.Series(dtype=float)
        entry = last_close_on_or_before(closes, generated_at) if not closes.empty else None
        benchmark_forward[benchmark] = {
            "1d": pct_return(entry, forward_close(closes, generated_at, 1)),
            "5d": pct_return(entry, forward_close(closes, generated_at, 5)),
        }

    evaluations: list[dict[str, Any]] = []
    for rank, candidate in enumerate(candidates, start=1):
        frame = symbol_frame(history, candidate["symbol"])
        if frame.empty or "Close" not in frame:
            close_1d = None
            close_5d = None
        else:
            closes = frame["Close"].dropna().astype(float)
            close_1d = forward_close(closes, generated_at, 1)
            close_5d = forward_close(closes, generated_at, 5)

        entry = safe_float(candidate.get("current_price"))
        forward_1d = pct_return(entry, close_1d)
        forward_5d = pct_return(entry, close_5d)
        spy_1d = benchmark_forward["SPY"]["1d"]
        spy_5d = benchmark_forward["SPY"]["5d"]
        qqq_1d = benchmark_forward["QQQ"]["1d"]
        qqq_5d = benchmark_forward["QQQ"]["5d"]

        evaluations.append(
            {
                "rank": rank,
                "symbol": candidate["symbol"],
                "name": candidate.get("name"),
                "entry_price": entry,
                "forward_close_1d": close_1d,
                "forward_close_5d": close_5d,
                "forward_return_1d": forward_1d,
                "forward_return_5d": forward_5d,
                "relative_spy_forward_1d": forward_1d - spy_1d if forward_1d is not None and spy_1d is not None else None,
                "relative_spy_forward_5d": forward_5d - spy_5d if forward_5d is not None and spy_5d is not None else None,
                "relative_qqq_forward_1d": forward_1d - qqq_1d if forward_1d is not None and qqq_1d is not None else None,
                "relative_qqq_forward_5d": forward_5d - qqq_5d if forward_5d is not None and qqq_5d is not None else None,
                "score": candidate.get("score"),
                "opportunity_score": candidate.get("opportunity_score"),
                "risk_score": candidate.get("risk_score"),
                "risk_details": candidate.get("risk_details") or {},
                "factor_scores": candidate.get("factor_scores") or {},
                "setup_details": candidate.get("setup_details") or {},
                "confidence_score": candidate.get("confidence_score"),
                "expected_direction": candidate.get("expected_direction"),
                "setup_type": candidate.get("setup_type"),
                "reason_codes": candidate.get("reason_codes") or [],
                "risk_flags": candidate.get("risk_flags") or [],
            }
        )

    summary = summarize_group(evaluations)
    result = {
        "run_dir": run_dir.as_posix(),
        "generated_at": payload["generated_at"],
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_forward": benchmark_forward,
        "summary": summary,
        "calibration": build_calibration_suggestions(evaluations),
        "candidates": evaluations,
    }
    if validation_config is not None:
        result["config_validation"] = _validate_config_on_run(
            source_candidates=candidates,
            evaluations=evaluations,
            config=validation_config,
        )

    (run_dir / "backtest_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (run_dir / "calibration_suggestions.json").write_text(
        json.dumps(result["calibration"], indent=2),
        encoding="utf-8",
    )
    if "config_validation" in result:
        (run_dir / "config_validation.json").write_text(
            json.dumps(result["config_validation"], indent=2),
            encoding="utf-8",
        )
    return result


def run_dirs_from_args(args: argparse.Namespace) -> list[Path]:
    if args.run_dir:
        return [args.run_dir]
    runs_root = ROOT / "outputs" / "runs"
    if not runs_root.exists():
        return []
    return sorted(path for path in runs_root.iterdir() if path.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate run folders against 1-day and 5-day forward returns."
    )
    parser.add_argument("--run-dir", type=Path, default=None, help="Specific outputs/runs/<timestamp> folder.")
    parser.add_argument(
        "--validate-config",
        type=Path,
        default=None,
        help="Optional config.yaml to compare against stored candidates and known forward returns.",
    )
    args = parser.parse_args()
    validation_config = None
    if args.validate_config is not None:
        validation_config = yaml.safe_load(args.validate_config.read_text(encoding="utf-8"))

    run_dirs = run_dirs_from_args(args)
    if not run_dirs:
        print("No run folders found.")
        return 1

    completed = 0
    for run_dir in run_dirs:
        try:
            result = evaluate_run(run_dir, validation_config=validation_config)
        except Exception as exc:
            print(f"Skipping {run_dir}: {exc}")
            continue
        completed += 1
        summary = result["summary"]
        print(
            f"{run_dir.name}: "
            f"1D hit={summary.get('hit_rate_1d')} "
            f"5D hit={summary.get('hit_rate_5d')} "
            f"avg5D={summary.get('avg_forward_return_5d')} "
            f"relSPY5D={summary.get('avg_relative_spy_forward_5d')}"
        )
        if "config_validation" in result:
            validation = result["config_validation"]
            print(
                f"  config validation delta relSPY5D="
                f"{validation.get('delta_avg_relative_spy_forward_5d')}"
            )

    return 0 if completed else 1


if __name__ == "__main__":
    raise SystemExit(main())
