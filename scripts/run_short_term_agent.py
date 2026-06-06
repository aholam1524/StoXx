#!/usr/bin/env python3
"""Run the full short-term flow: screen S&P 500, then generate proposals."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def universe_label(universes: list[str]) -> str:
    selected = set(universes)
    if selected == {"sp500", "sp400", "finland"}:
        return "all"
    if selected == {"sp500", "sp400"}:
        return "us"
    if selected == {"sp400"}:
        return "sp400"
    if selected == {"finland"}:
        return "finland"
    return "custom-" + "-".join(sorted(selected))


def configured_universes() -> list[str]:
    config_path = ROOT / "config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    universes = config.get("universes") or [config.get("universe", "sp500")]
    return [str(universe) for universe in universes]


def run_id(universes: list[str]) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S_utc")
    return f"{timestamp}_{universe_label(universes)}"


def run(command: list[str]) -> None:
    print(f"\n> {' '.join(command)}")
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run configured short-term screen and local AI proposals."
    )
    parser.add_argument(
        "--top",
        type=int,
        default=150,
        help="Top screen results to save for evaluation/calibration.",
    )
    parser.add_argument(
        "--proposal-top",
        type=int,
        default=10,
        help="Top candidates to generate proposals for.",
    )
    parser.add_argument(
        "--model",
        default="qwen2.5:0.5b",
        help="Ollama model name (default: qwen2.5:0.5b).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional symbol limit for faster tests.",
    )
    parser.add_argument(
        "--universe",
        action="append",
        choices=("sp500", "sp400", "finland"),
        help="Universe to load. Repeat for multiple. Overrides config universes.",
    )
    parser.add_argument(
        "--use-ollama",
        action="store_true",
        help="Try local Ollama wording; unsafe outputs fall back to fact-only notes.",
    )
    parser.add_argument(
        "--no-news",
        action="store_true",
        help="Skip Yahoo Finance news context in proposals.",
    )
    parser.add_argument(
        "--news-limit",
        type=int,
        default=5,
        help="Maximum recent Yahoo Finance headlines per proposal candidate.",
    )
    parser.add_argument(
        "--news-days",
        type=int,
        default=7,
        help="Only include Yahoo Finance headlines from the last N days.",
    )
    args = parser.parse_args()
    selected_universes = args.universe or configured_universes()
    run_dir = ROOT / "outputs" / "runs" / run_id(selected_universes)
    run_dir.mkdir(parents=True, exist_ok=True)

    screen_cmd = [
        sys.executable,
        "main.py",
        "--mode",
        "short-term",
        "--top",
        str(args.top),
        "--output",
        str(run_dir / "screen_results.json"),
    ]
    if args.limit is not None:
        screen_cmd.extend(["--limit", str(args.limit)])
    if args.universe:
        for universe in args.universe:
            screen_cmd.extend(["--universe", universe])
    run(screen_cmd)

    proposal_cmd = [
        sys.executable,
        "scripts/generate_proposals.py",
        "--top",
        str(args.proposal_top),
        "--model",
        args.model,
        "--input",
        str(run_dir / "screen_results.json"),
        "--run-dir",
        str(run_dir),
    ]
    if args.use_ollama:
        proposal_cmd.append("--use-ollama")
    if args.no_news:
        proposal_cmd.append("--no-news")
    proposal_cmd.extend(["--news-limit", str(args.news_limit)])
    proposal_cmd.extend(["--news-days", str(args.news_days)])
    run(proposal_cmd)
    print(f"\nDone. Run folder: {run_dir}")
    print("Latest copies are in outputs/latest/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
