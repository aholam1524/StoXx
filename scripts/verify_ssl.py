#!/usr/bin/env python3
"""Quick check that HTTPS and Yahoo Finance work on this machine."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.network import configure_ssl  # noqa: E402


def main() -> int:
    configure_ssl()

    from src.data.fetcher import _fetch_quote_batch, init_yfinance_session  # noqa: E402

    init_yfinance_session()

    import requests

    print("Testing https://www.google.com ...")
    try:
        status = requests.get("https://www.google.com", timeout=15).status_code
        print(f"  Google: HTTP {status}")
    except Exception as exc:
        print(f"  Google: FAILED ({exc})")
        return 1

    print("Testing Yahoo Finance batch quote (AAPL) ...")
    rows = _fetch_quote_batch(["AAPL"])
    if not rows:
        print("  Yahoo: no data (rate-limited or network issue — wait 1–2 min, retry)")
        return 1

    row = rows[0]
    print(f"  Yahoo: OK — {row.symbol} P/E={row.trailing_pe} price={row.current_price}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
