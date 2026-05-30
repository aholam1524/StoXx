#!/usr/bin/env python3
"""Run the full short-term flow: screen S&P 500, then generate proposals."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    print(f"\n> {' '.join(command)}")
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run S&P 500 short-term screen and local AI proposals."
    )
    parser.add_argument("--top", type=int, default=10, help="Top screen results to save.")
    parser.add_argument(
        "--proposal-top",
        type=int,
        default=5,
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
        "--use-ollama",
        action="store_true",
        help="Try local Ollama wording; unsafe outputs fall back to fact-only notes.",
    )
    args = parser.parse_args()

    screen_cmd = [sys.executable, "main.py", "--mode", "short-term", "--top", str(args.top)]
    if args.limit is not None:
        screen_cmd.extend(["--limit", str(args.limit)])
    run(screen_cmd)

    proposal_cmd = [
        sys.executable,
        "scripts/generate_proposals.py",
        "--top",
        str(args.proposal_top),
        "--model",
        args.model,
    ]
    if args.use_ollama:
        proposal_cmd.append("--use-ollama")
    run(proposal_cmd)
    print("\nDone. Open outputs/proposals.md for the AI research notes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
