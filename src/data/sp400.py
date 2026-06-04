"""Load S&P MidCap 400 symbols from a static local list."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYMBOL_PATH = ROOT / "data" / "sp400_symbols.txt"
MARKET = "US / S&P MidCap 400"
EXCHANGE = "NYSE/Nasdaq"


def load_sp400_symbols(path: Path = SYMBOL_PATH) -> list[str]:
    symbols = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    # Yahoo Finance uses '-' instead of '.' (e.g. MOG.A -> MOG-A)
    return [symbol.replace(".", "-") for symbol in symbols]


def symbol_metadata(symbols: list[str]) -> dict[str, dict[str, str]]:
    return {
        symbol: {
            "market": MARKET,
            "exchange": EXCHANGE,
        }
        for symbol in symbols
    }
