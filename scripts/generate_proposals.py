#!/usr/bin/env python3
"""Generate local Ollama proposals from screener results."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent.short_term_proposals import generate_short_term_proposals  # noqa: E402


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
        default=ROOT / "outputs" / "proposals.md",
        help="Markdown output path.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=ROOT / "outputs" / "proposals.json",
        help="JSON output path.",
    )
    parser.add_argument(
        "--use-ollama",
        action="store_true",
        help="Try local Ollama wording; unsafe outputs fall back to fact-only notes.",
    )
    args = parser.parse_args()

    proposals = generate_short_term_proposals(
        input_path=args.input,
        output_markdown_path=args.output_md,
        output_json_path=args.output_json,
        model=args.model,
        top=args.top,
        use_ollama=args.use_ollama,
    )
    print(f"Generated {len(proposals)} proposals.")
    print(f"Markdown: {args.output_md}")
    print(f"JSON: {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
