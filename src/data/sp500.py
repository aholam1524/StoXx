"""Load S&P 500 constituents from Wikipedia (no API key)."""

from __future__ import annotations

from io import StringIO

import pandas as pd
import requests

WIKIPEDIA_SP500_URL = (
    "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
)
USER_AGENT = (
    "Mozilla/5.0 (compatible; SP500Screener/1.0; "
    "+https://www.wikipedia.org/; research-bot)"
)


def load_sp500_symbols() -> list[str]:
    response = requests.get(
        WIKIPEDIA_SP500_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()
    tables = pd.read_html(StringIO(response.text))
    df = tables[0]
    symbols = df["Symbol"].astype(str).str.strip()
    # Yahoo Finance uses '-' instead of '.' (e.g. BRK.B -> BRK-B)
    return symbols.str.replace(".", "-", regex=False).tolist()
