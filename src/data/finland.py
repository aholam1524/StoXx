"""Load Nasdaq Helsinki symbols for Yahoo Finance."""

from __future__ import annotations

from io import StringIO

import pandas as pd
import requests

STOCKANALYSIS_HELSINKI_URL = "https://stockanalysis.com/list/nasdaq-helsinki/"
USER_AGENT = (
    "Mozilla/5.0 (compatible; HelsinkiScreener/1.0; "
    "+https://stockanalysis.com/; research-bot)"
)

MARKET = "Finland / Nasdaq Helsinki"
EXCHANGE = "Nasdaq Helsinki"

FALLBACK_SYMBOLS = [
    "AALLON.HE",
    "AFAGR.HE",
    "AKTIA.HE",
    "ALISA.HE",
    "ALMA.HE",
    "ANORA.HE",
    "APETIT.HE",
    "ASPO.HE",
    "ATRAV.HE",
    "BAS1V.HE",
    "BITTI.HE",
    "BOREO.HE",
    "CAPMAN.HE",
    "CGCBV.HE",
    "CTH1V.HE",
    "DIGIA.HE",
    "DNA.HE",
    "DOV1V.HE",
    "EEZY.HE",
    "EFO1V.HE",
    "ELISA.HE",
    "ENENTO.HE",
    "EQV1V.HE",
    "ETTE.HE",
    "EXL1V.HE",
    "FIA1S.HE",
    "FISKARS.HE",
    "FORTUM.HE",
    "FSKRS.HE",
    "GLA1V.HE",
    "GOFORE.HE",
    "HARVIA.HE",
    "HEEROS.HE",
    "HONBS.HE",
    "HUH1V.HE",
    "ICP1V.HE",
    "ILKKA2.HE",
    "KALMAR.HE",
    "KAMUX.HE",
    "KEMIRA.HE",
    "KESKOB.HE",
    "KNEBV.HE",
    "KOSKI.HE",
    "KREATE.HE",
    "KSLAV.HE",
    "LAT1V.HE",
    "LEADD.HE",
    "LEHTO.HE",
    "LOIHDE.HE",
    "MEKKO.HE",
    "METSO.HE",
    "MUSTI.HE",
    "NDA-FI.HE",
    "NESTE.HE",
    "NOHO.HE",
    "NOKIA.HE",
    "NOKIAN.HE",
    "OLVAS.HE",
    "OPTOMED.HE",
    "ORNBV.HE",
    "OUT1V.HE",
    "PUUILO.HE",
    "PUMU.HE",
    "QTCOM.HE",
    "RAIVV.HE",
    "RAP1V.HE",
    "REG1V.HE",
    "REKA.HE",
    "REMEDY.HE",
    "ROBIT.HE",
    "ROVIO.HE",
    "SAMPO.HE",
    "SANOMA.HE",
    "SCANFL.HE",
    "SITOWS.HE",
    "SSABAH.HE",
    "SSABBH.HE",
    "STERV.HE",
    "STOCKA.HE",
    "STOCKB.HE",
    "TAALA.HE",
    "TALENTUM.HE",
    "TELIA1.HE",
    "TEM1V.HE",
    "TIETO.HE",
    "TOKMAN.HE",
    "TRH1V.HE",
    "TYRES.HE",
    "UPM.HE",
    "VALMT.HE",
    "VERK.HE",
    "VIK1V.HE",
    "WRT1V.HE",
    "YIT.HE",
]


def _normalize_to_yahoo(symbol: str) -> str | None:
    value = str(symbol).strip().upper()
    if not value or value in {"NAN", "-"}:
        return None
    if value.endswith(".HE"):
        return value
    value = value.replace(".", "-")
    return f"{value}.HE"


def _dedupe(symbols: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for symbol in symbols:
        if symbol not in seen:
            seen.add(symbol)
            deduped.append(symbol)
    return deduped


def _load_stockanalysis_symbols() -> list[str]:
    response = requests.get(
        STOCKANALYSIS_HELSINKI_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()
    tables = pd.read_html(StringIO(response.text))
    if not tables:
        return []
    df = tables[0]
    if "Symbol" not in df.columns:
        return []
    symbols = [
        normalized
        for raw in df["Symbol"].astype(str).tolist()
        if (normalized := _normalize_to_yahoo(raw)) is not None
    ]
    return _dedupe(symbols)


def load_finland_symbols() -> list[str]:
    try:
        live_symbols = _load_stockanalysis_symbols()
    except Exception:
        live_symbols = []
    if live_symbols:
        return live_symbols
    return _dedupe(FALLBACK_SYMBOLS)


def symbol_metadata(symbols: list[str]) -> dict[str, dict[str, str]]:
    return {
        symbol: {
            "market": MARKET,
            "exchange": EXCHANGE,
        }
        for symbol in symbols
    }
