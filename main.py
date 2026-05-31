#!/usr/bin/env python3
"""Phase 1: free S&P 500 undervaluation screener (US, no API keys)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DISCLAIMER = (
    "Not financial advice. For research only. "
    "Data from Yahoo Finance may be delayed or incomplete."
)


def load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_market_cap(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,.0f}"


def _format_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def _format_number(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def _configured_universes(config: dict, cli_universes: list[str] | None) -> list[str]:
    raw = cli_universes or config.get("universes") or [config.get("universe", "sp500")]
    if isinstance(raw, str):
        raw = [raw]
    universes: list[str] = []
    for item in raw:
        value = str(item).strip().lower()
        if value and value not in universes:
            universes.append(value)
    return universes or ["sp500"]


def print_results(candidates: list, top_n: int) -> None:
    print(f"\n{DISCLAIMER}\n")
    print(f"Top {min(top_n, len(candidates))} potentially undervalued names:\n")
    header = (
        f"{'Rank':<5} {'Symbol':<8} {'Score':<7} {'P/E':<8} {'P/B':<8} "
        f"{'PEG':<8} {'Mkt Cap':<10} {'Market':<25} Sector"
    )
    print(header)
    print("-" * len(header))

    for rank, c in enumerate(candidates[:top_n], start=1):
        pe = f"{c.trailing_pe:.2f}" if c.trailing_pe is not None else "n/a"
        pb = f"{c.price_to_book:.2f}" if c.price_to_book is not None else "n/a"
        peg = f"{c.peg_ratio:.2f}" if c.peg_ratio is not None else "n/a"
        print(
            f"{rank:<5} {c.symbol:<8} {c.score:<7.3f} {pe:<8} {pb:<8} {peg:<8} "
            f"{format_market_cap(c.market_cap):<10} {(c.market or 'n/a'):<25} {c.sector}"
        )
        print(f"       {c.name}")
        print(f"       Signals: {', '.join(c.reasons)}")
        print()


def print_short_term_results(candidates: list, top_n: int) -> None:
    print(f"\n{DISCLAIMER}\n")
    print(
        f"Top {min(top_n, len(candidates))} short-term candidates "
        "(1-day to 1-week window):\n"
    )
    header = (
        f"{'Rank':<5} {'Symbol':<8} {'Score':<7} {'Risk':<7} {'Setup':<23} "
        f"{'1D':<9} {'5D':<9} {'SPY 5D':<9} {'Vol x':<8} {'RSI':<7} "
        f"{'Mkt Cap':<10} Market"
    )
    print(header)
    print("-" * len(header))

    for rank, c in enumerate(candidates[:top_n], start=1):
        print(
            f"{rank:<5} {c.symbol:<8} {c.score:<7.3f} "
            f"{_format_number(c.risk_score):<7} "
            f"{(c.setup_type or 'n/a'):<23} "
            f"{_format_percent(c.return_1d):<9} {_format_percent(c.return_5d):<9} "
            f"{_format_percent(c.rel_strength_spy_5d):<9} "
            f"{_format_number(c.volume_ratio_5d):<8} "
            f"{_format_number(c.rsi_14):<7} {format_market_cap(c.market_cap):<10} "
            f"{c.market or 'n/a'}"
        )
        print(f"       {c.name}")
        print(f"       Signals: {', '.join(c.reasons)}")
        if c.risk_flags:
            print(f"       Risk flags: {', '.join(c.risk_flags)}")
        print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Screen S&P 500 for relatively undervalued US stocks (free data)."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "config.yaml",
        help="Path to config.yaml",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="Number of results to show (default: config top_n)",
    )
    parser.add_argument(
        "--mode",
        choices=("value", "short-term"),
        default="value",
        help="Ranking mode: value or short-term (default: value)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only fetch first N symbols (for quick tests)",
    )
    parser.add_argument(
        "--universe",
        action="append",
        choices=("sp500", "finland"),
        help="Universe to load. Repeat for multiple. Overrides config universes.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds between Yahoo batch requests (default: 1.0)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "screen_results.json",
        help="JSON output path",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not write JSON output file",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use bundled sample metrics (offline test; no Yahoo requests)",
    )
    parser.add_argument(
        "--insecure-ssl",
        action="store_true",
        help="Disable SSL verification for Yahoo (if cert errors on your PC)",
    )
    args = parser.parse_args()

    from src.data.network import configure_ssl  # noqa: E402

    configure_ssl(insecure=args.insecure_ssl)

    from src.data.fetcher import fetch_many, init_yfinance_session, load_demo_metrics  # noqa: E402
    from src.data.finland import load_finland_symbols, symbol_metadata as finland_metadata  # noqa: E402
    from src.data.prices import enrich_short_term_metrics  # noqa: E402
    from src.data.sp500 import load_sp500_symbols  # noqa: E402
    from src.screen.scorer import score_candidates, score_short_term_candidates  # noqa: E402

    config = load_config(args.config)
    universes = _configured_universes(config, args.universe)
    top_n = args.top if args.top is not None else int(config.get("top_n", 10))
    scoring = config.get("scoring", {})
    short_term_scoring = config.get("short_term_scoring", {})
    filters = {
        **config.get("filters", {}),
        "min_market_cap": config.get("min_market_cap"),
        "max_market_cap": config.get("max_market_cap"),
    }

    if args.demo:
        demo_path = ROOT / "data" / "demo_metrics.json"
        print(f"Demo mode: loading sample metrics from {demo_path}")
        rows = load_demo_metrics(demo_path)
        symbols = [r.symbol for r in rows]
        print(f"Loaded {len(rows)} demo symbols.")
    else:
        init_yfinance_session(insecure_ssl=args.insecure_ssl)
        symbols: list[str] = []
        metadata: dict[str, dict[str, str]] = {}

        if "sp500" in universes:
            print("Loading S&P 500 universe from Wikipedia...")
            sp500_symbols = load_sp500_symbols()
            symbols.extend(sp500_symbols)
            metadata.update(
                {
                    symbol: {
                        "market": "US / S&P 500",
                        "exchange": "NYSE/Nasdaq",
                    }
                    for symbol in sp500_symbols
                }
            )
            print(f"S&P 500 universe: {len(sp500_symbols)} symbols")

        if "finland" in universes:
            print("Loading Finnish universe...")
            finland_symbols = load_finland_symbols()
            symbols.extend(finland_symbols)
            metadata.update(finland_metadata(finland_symbols))
            print(f"Finland universe: {len(finland_symbols)} symbols")

        symbols = list(dict.fromkeys(symbols))
        if args.limit is not None:
            symbols = symbols[: args.limit]
        print(f"Universe: {len(symbols)} symbols")

        def progress(done: int, total: int, symbol: str, ok: bool) -> None:
            status = "ok" if ok else "skip"
            print(f"\rFetching [{done}/{total}] {symbol:<8} {status}   ", end="", flush=True)

        print(
            "Fetching fundamentals from Yahoo Finance (free, may take several minutes)..."
        )
        rows = fetch_many(symbols, delay_seconds=args.delay, on_progress=progress)
        for row in rows:
            row_metadata = metadata.get(row.symbol)
            if row_metadata is not None:
                row.market = row_metadata["market"]
                row.exchange = row_metadata["exchange"]
        print(f"\nFetched metrics for {len(rows)} symbols.")
        if not rows:
            print(
                "\nNo data returned from Yahoo. Try:\n"
                "  1. pip install truststore certifi\n"
                "  2. python main.py --limit 20   (retry after a minute if rate-limited)\n"
                "  3. python main.py --demo       (offline test)\n"
            )
            return 1

    if args.mode == "short-term":
        print("Fetching recent prices for short-term indicators...")
        rows = enrich_short_term_metrics(rows)
        scored = score_short_term_candidates(
            rows,
            scoring=short_term_scoring,
            filters=filters,
        )
    else:
        scored = score_candidates(rows, scoring=scoring, filters=filters)

    if not scored:
        print("No candidates passed filters. Try relaxing config.yaml filters.")
        return 1

    if args.mode == "short-term":
        print_short_term_results(scored, top_n)
    else:
        print_results(scored, top_n)

    if not args.no_save:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "universe": ",".join(universes),
            "universes": universes,
            "mode": args.mode,
            "symbol_count": len(symbols),
            "fetched_count": len(rows),
            "disclaimer": DISCLAIMER,
            "candidates": [c.to_dict() for c in scored[:top_n]],
        }
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Saved results to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
