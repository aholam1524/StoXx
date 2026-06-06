#!/usr/bin/env python3
"""Generate local Ollama proposals from screener results."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent.short_term_proposals import generate_short_term_proposals  # noqa: E402


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
    if selected:
        return "custom-" + "-".join(sorted(selected))
    return "manual"


def universes_from_input(input_path: Path) -> list[str]:
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    universes = payload.get("universes")
    if isinstance(universes, list):
        return [str(universe) for universe in universes]
    universe = payload.get("universe")
    if isinstance(universe, str):
        return [part.strip() for part in universe.split(",") if part.strip()]
    return []


def run_id(universes: list[str]) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S_utc")
    return f"{timestamp}_{universe_label(universes)}"


def resolve_run_paths(
    *,
    input_path: Path,
    run_dir: Path | None,
    output_md: Path | None,
    output_json: Path | None,
    output_csv: Path | None,
) -> tuple[Path, Path, Path, Path]:
    if run_dir is None:
        run_dir = ROOT / "outputs" / "runs" / run_id(universes_from_input(input_path))
    run_dir.mkdir(parents=True, exist_ok=True)

    run_input = run_dir / "screen_results.json"
    if input_path.resolve() != run_input.resolve():
        shutil.copy2(input_path, run_input)

    return (
        run_input,
        output_md or run_dir / "proposals.md",
        output_json or run_dir / "proposals.json",
        output_csv or run_dir / "metrics_summary.csv",
    )


def update_latest(
    run_input: Path,
    output_md: Path,
    output_json: Path,
    output_csv: Path,
) -> None:
    latest_dir = ROOT / "outputs" / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(run_input, latest_dir / "screen_results.json")
    shutil.copy2(output_md, latest_dir / "proposals.md")
    shutil.copy2(output_json, latest_dir / "proposals.json")
    shutil.copy2(output_csv, latest_dir / "metrics_summary.csv")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate 1-day to 1-week short-term proposals with local Ollama."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "outputs" / "screen_results.json",
        help="Input screener JSON path.",
    )
    parser.add_argument(
        "--model",
        default="qwen2.5:0.5b",
        help="Ollama model name (default: qwen2.5:0.5b).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of top candidates to write proposals for.",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=None,
        help="Markdown output path (default: outputs/runs/<timestamp>/proposals.md).",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="JSON output path (default: outputs/runs/<timestamp>/proposals.json).",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Run history directory (default: outputs/runs/<timestamp>).",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=None,
        help="Metrics CSV output path (default: outputs/runs/<timestamp>/metrics_summary.csv).",
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
        help="Maximum recent Yahoo Finance headlines per candidate (default: 5).",
    )
    parser.add_argument(
        "--news-days",
        type=int,
        default=7,
        help="Only include Yahoo Finance headlines from the last N days (default: 7).",
    )
    args = parser.parse_args()
    input_path, output_md, output_json, output_csv = resolve_run_paths(
        input_path=args.input,
        run_dir=args.run_dir,
        output_md=args.output_md,
        output_json=args.output_json,
        output_csv=args.output_csv,
    )

    proposals = generate_short_term_proposals(
        input_path=input_path,
        output_markdown_path=output_md,
        output_json_path=output_json,
        output_summary_path=output_csv,
        model=args.model,
        top=args.top,
        use_ollama=args.use_ollama,
        include_news=not args.no_news,
        news_limit=args.news_limit,
        news_days=args.news_days,
    )
    update_latest(input_path, output_md, output_json, output_csv)
    print(f"Generated {len(proposals)} proposals.")
    print(f"Run folder: {output_md.parent}")
    print(f"Markdown: {output_md}")
    print(f"JSON: {output_json}")
    print(f"CSV: {output_csv}")
    print(f"Latest copies: {ROOT / 'outputs' / 'latest'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
