#!/usr/bin/env python3
"""Generate local Ollama proposals from screener results."""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent.short_term_proposals import generate_short_term_proposals  # noqa: E402


def run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def resolve_run_paths(
    *,
    input_path: Path,
    run_dir: Path | None,
    output_md: Path | None,
    output_json: Path | None,
) -> tuple[Path, Path, Path]:
    if run_dir is None:
        run_dir = ROOT / "outputs" / "runs" / run_id()
    run_dir.mkdir(parents=True, exist_ok=True)

    run_input = run_dir / "screen_results.json"
    if input_path.resolve() != run_input.resolve():
        shutil.copy2(input_path, run_input)

    return (
        run_input,
        output_md or run_dir / "proposals.md",
        output_json or run_dir / "proposals.json",
    )


def update_latest(run_input: Path, output_md: Path, output_json: Path) -> None:
    latest_dir = ROOT / "outputs" / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(run_input, latest_dir / "screen_results.json")
    shutil.copy2(output_md, latest_dir / "proposals.md")
    shutil.copy2(output_json, latest_dir / "proposals.json")


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
        "--use-ollama",
        action="store_true",
        help="Try local Ollama wording; unsafe outputs fall back to fact-only notes.",
    )
    args = parser.parse_args()
    input_path, output_md, output_json = resolve_run_paths(
        input_path=args.input,
        run_dir=args.run_dir,
        output_md=args.output_md,
        output_json=args.output_json,
    )

    proposals = generate_short_term_proposals(
        input_path=input_path,
        output_markdown_path=output_md,
        output_json_path=output_json,
        model=args.model,
        top=args.top,
        use_ollama=args.use_ollama,
    )
    update_latest(input_path, output_md, output_json)
    print(f"Generated {len(proposals)} proposals.")
    print(f"Run folder: {output_md.parent}")
    print(f"Markdown: {output_md}")
    print(f"JSON: {output_json}")
    print(f"Latest copies: {ROOT / 'outputs' / 'latest'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
