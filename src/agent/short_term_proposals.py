"""Generate short-term research proposals from screener candidates."""

from __future__ import annotations

import json
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from src.agent.ollama_client import OllamaClient

DISCLAIMER = (
    "Not financial advice. Short-term trading is high risk. "
    "Use this only as research and define your own position sizing and risk limits."
)


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def _num(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def _market_cap(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    return f"${value:,.0f}"


def _metric_guide() -> list[str]:
    return [
        "## How To Read This Report",
        "",
        "- **Returns:** Recent price change over 1, 5, 10, and 20 trading days.",
        "- **Relative strength:** Return compared with SPY/QQQ. Positive means the stock outperformed that benchmark.",
        "- **Volume ratios:** Current/recent volume compared with normal volume. Above 1.00x means higher than average activity.",
        "- **Range/volatility:** Distance from recent highs/lows shows if price is near a breakout or already extended. ATR14 estimates normal daily movement.",
        "- **Trend quality:** SMA and up-day ratios show whether the move is consistent or just a one-day spike.",
        "- **Scores:** Opportunity ranks setup quality; risk estimates visible short-term risk; confidence combines opportunity and risk.",
        "",
    ]


def _metric_block(candidate: dict[str, Any]) -> list[str]:
    return [
        "**Metrics:**",
        f"- **Snapshot:** {candidate.get('market') or 'n/a'} / {candidate.get('exchange') or 'n/a'}; price {_num(candidate.get('current_price'))}; market cap {_market_cap(candidate.get('market_cap'))}.",
        f"- **Returns:** 1D {_pct(candidate.get('return_1d'))}; 5D {_pct(candidate.get('return_5d'))}; 10D {_pct(candidate.get('return_10d'))}; 20D {_pct(candidate.get('return_20d'))}.",
        f"- **Relative strength:** SPY 1D {_pct(candidate.get('rel_strength_spy_1d'))}; SPY 5D {_pct(candidate.get('rel_strength_spy_5d'))}; QQQ 1D {_pct(candidate.get('rel_strength_qqq_1d'))}; QQQ 5D {_pct(candidate.get('rel_strength_qqq_5d'))}.",
        f"- **Volume/liquidity:** 5D volume {_num(candidate.get('volume_ratio_5d'))}x; 20D volume {_num(candidate.get('volume_ratio_20d'))}x; 5D/20D trend {_num(candidate.get('volume_trend_5d_20d'))}x; dollar volume {_market_cap(candidate.get('dollar_volume'))}.",
        f"- **Range/volatility:** 5D high {_pct(candidate.get('distance_from_5d_high'))}; 5D low {_pct(candidate.get('distance_from_5d_low'))}; 20D high {_pct(candidate.get('distance_from_20d_high'))}; 20D low {_pct(candidate.get('distance_from_20d_low'))}; ATR14 {_pct(candidate.get('atr_14_pct'))}; gap {_pct(candidate.get('gap_1d'))}.",
        f"- **Trend quality:** SMA 5/20 {_pct(candidate.get('sma_5_20_ratio'))}; close vs SMA20 {_pct(candidate.get('close_vs_sma_20'))}; up-day ratio 5D {_pct(candidate.get('up_day_ratio_5d'))}; up-day ratio 10D {_pct(candidate.get('up_day_ratio_10d'))}.",
        f"- **Other context:** RSI14 {_num(candidate.get('rsi_14'))}; upcoming earnings days {_num(candidate.get('upcoming_earnings_days'))}.",
        f"- **Scores:** rank {_num(candidate.get('score'))}; opportunity {_num(candidate.get('opportunity_score'))}; risk {_num(candidate.get('risk_score'))} ({candidate.get('risk_level') or 'n/a'}); confidence {_num(candidate.get('confidence_score'))}.",
        f"- **Prediction:** {candidate.get('expected_direction') or 'n/a'} over {candidate.get('expected_window') or 'n/a'}; setup {candidate.get('setup_type') or 'n/a'}.",
    ]


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def _allowed_observations(candidate: dict[str, Any]) -> list[str]:
    observations: list[str] = []
    return_1d = candidate.get("return_1d")
    return_5d = candidate.get("return_5d")
    return_10d = candidate.get("return_10d")
    volume_ratio = candidate.get("volume_ratio_5d")
    volume_ratio_20d = candidate.get("volume_ratio_20d")
    volume_trend = candidate.get("volume_trend_5d_20d")
    distance_high = candidate.get("distance_from_5d_high")
    distance_high_20d = candidate.get("distance_from_20d_high")
    rsi = candidate.get("rsi_14")
    rel_spy = candidate.get("rel_strength_spy_5d")
    rel_qqq = candidate.get("rel_strength_qqq_5d")
    atr = candidate.get("atr_14_pct")
    sma_ratio = candidate.get("sma_5_20_ratio")
    close_vs_sma = candidate.get("close_vs_sma_20")
    up_day_5d = candidate.get("up_day_ratio_5d")
    if return_1d is not None:
        if return_1d > 0:
            observations.append(f"Latest session was positive at {_pct(return_1d)}.")
        else:
            observations.append(f"Latest session was negative at {_pct(return_1d)}.")
    if return_5d is not None:
        if return_5d > 0:
            observations.append(f"Five-day return is positive at {_pct(return_5d)}.")
        else:
            observations.append(f"Five-day return is negative at {_pct(return_5d)}.")
    if return_10d is not None:
        observations.append(f"Ten-day return is {_pct(return_10d)}.")
    if volume_ratio is not None:
        observations.append(
            f"Latest volume is {_num(volume_ratio)}x the prior 5-day average."
        )
    if volume_ratio_20d is not None:
        observations.append(
            f"Latest volume is {_num(volume_ratio_20d)}x the prior 20-day average."
        )
    if volume_trend is not None:
        observations.append(f"Recent 5-day volume trend is {_num(volume_trend)}x the 20-day average.")
    if distance_high is not None:
        observations.append(f"Price is {_pct(distance_high)} from the 5-day high.")
    if distance_high_20d is not None:
        observations.append(f"Price is {_pct(distance_high_20d)} from the 20-day high.")
    if rsi is not None:
        observations.append(f"RSI 14 is {_num(rsi)}.")
    if sma_ratio is not None:
        observations.append(f"SMA 5/20 trend ratio is {_pct(sma_ratio)}.")
    if close_vs_sma is not None:
        observations.append(f"Price is {_pct(close_vs_sma)} versus SMA20.")
    if up_day_5d is not None:
        observations.append(f"Up-day ratio over 5 days is {_pct(up_day_5d)}.")
    if rel_spy is not None:
        observations.append(f"5-day relative strength vs SPY is {_pct(rel_spy)}.")
    if rel_qqq is not None:
        observations.append(f"5-day relative strength vs QQQ is {_pct(rel_qqq)}.")
    if atr is not None:
        observations.append(f"ATR 14 is {_pct(atr)} of price.")
    observations.extend(candidate.get("reasons") or [])
    return observations


def _proposal_highlights(candidate: dict[str, Any]) -> list[str]:
    highlights: list[str] = []
    return_5d = candidate.get("return_5d")
    return_10d = candidate.get("return_10d")
    volume_ratio = candidate.get("volume_ratio_5d")
    volume_ratio_20d = candidate.get("volume_ratio_20d")
    volume_trend = candidate.get("volume_trend_5d_20d")
    rel_spy = candidate.get("rel_strength_spy_5d")
    rel_qqq = candidate.get("rel_strength_qqq_5d")
    rsi = candidate.get("rsi_14")
    distance_high = candidate.get("distance_from_5d_high")
    sma_ratio = candidate.get("sma_5_20_ratio")
    up_day_5d = candidate.get("up_day_ratio_5d")

    if return_5d is not None:
        highlights.append(f"Five-day return is {_pct(return_5d)}.")
    if return_10d is not None:
        highlights.append(f"Ten-day return is {_pct(return_10d)}.")
    if rel_spy is not None:
        highlights.append(f"5-day relative strength vs SPY is {_pct(rel_spy)}.")
    if rel_qqq is not None:
        highlights.append(f"5-day relative strength vs QQQ is {_pct(rel_qqq)}.")
    if volume_ratio is not None:
        highlights.append(f"Latest volume is {_num(volume_ratio)}x the prior 5-day average.")
    if volume_ratio_20d is not None:
        highlights.append(f"Latest volume is {_num(volume_ratio_20d)}x the prior 20-day average.")
    if volume_trend is not None:
        highlights.append(f"5-day volume trend is {_num(volume_trend)}x the 20-day average.")
    if distance_high is not None:
        highlights.append(f"Price is {_pct(distance_high)} from the 5-day high.")
    if rsi is not None:
        highlights.append(f"RSI 14 is {_num(rsi)}.")
    if sma_ratio is not None:
        highlights.append(f"SMA 5/20 trend ratio is {_pct(sma_ratio)}.")
    if up_day_5d is not None:
        highlights.append(f"Up-day ratio over 5 days is {_pct(up_day_5d)}.")

    return highlights[:5] or ["Short-term composite score ranked highly."]


def _risk_observations(candidate: dict[str, Any]) -> list[str]:
    risks: list[str] = []
    risk_score = candidate.get("risk_score")
    risk_level = candidate.get("risk_level")
    risk_flags = candidate.get("risk_flags") or []

    for flag in risk_flags:
        if flag != "low visible short-term risk flags":
            risks.append(flag)

    if risk_score is not None:
        risks.append(
            f"Risk score is {_num(risk_score)} ({risk_level or 'n/a'}) on a 0 to 1 scale."
        )
    market_cap = candidate.get("market_cap")
    dollar_volume = candidate.get("dollar_volume")
    if market_cap is not None and market_cap < 1_000_000_000:
        risks.append("smaller market-cap name; liquidity and spreads may matter more")
    if dollar_volume is not None and dollar_volume < 25_000_000:
        risks.append("lower dollar volume; entries and exits may be harder")
    deduped = list(dict.fromkeys(risks))
    if not deduped:
        risks.append("Main invalidation is loss of positive momentum or fading relative volume.")
        return risks
    return deduped


def _deterministic_proposal(candidate: dict[str, Any]) -> str:
    observations = _proposal_highlights(candidate)
    risks = _risk_observations(candidate)
    symbol = candidate.get("symbol")
    name = candidate.get("name")
    setup_type = candidate.get("setup_type") or "short-term"
    article = "an" if setup_type[:1].lower() in {"a", "e", "i", "o", "u"} else "a"

    why = observations[:5] if observations else ["Short-term composite score ranked highly."]
    risk_lines = risks[:4]

    return "\n".join(
        [
            f"### {symbol} - {name}",
            f"**Setup:** {symbol} is {article} {setup_type} candidate based on the current 1-day to 1-week screen. "
            f"The setup is driven by recent price action, relative volume, market-relative strength, and risk flags.",
            "",
            *_metric_block(candidate),
            "",
            "**Why it screens well:**",
            *[f"- {item}" for item in why],
            f"- Opportunity score is {_num(candidate.get('opportunity_score'))}; risk score is {_num(candidate.get('risk_score'))}.",
            f"- Reason codes: {', '.join(candidate.get('reason_codes') or ['n/a'])}.",
            "",
            "**1-day to 1-week plan:**",
            "- Watch whether the stock continues to outperform SPY/QQQ over the next session.",
            "- Watch whether relative volume stays supportive; fading volume weakens the setup.",
            "- Treat loss of momentum plus fading relative volume as invalidation.",
            "",
            "**Main risks:**",
            *[f"- {item}" for item in risk_lines],
            "",
            "**Verdict:** This is a watchlist candidate for short-term research only; the setup depends on momentum and volume staying intact. Not financial advice.",
        ]
    )


def _format_ollama_json(candidate: dict[str, Any], payload: dict[str, Any]) -> str:
    sections = [
        f"### {candidate.get('symbol')} - {candidate.get('name')}",
        str(payload["setup"]).strip(),
        "",
        *_metric_block(candidate),
        "",
        "**Why it screens well:**",
        *[f"- {item}" for item in payload["why_it_screens_well"]],
        "",
        "**1-day to 1-week plan:**",
        *[f"- {item}" for item in payload["plan"]],
        "",
        "**Main risks:**",
        *[f"- {item}" for item in payload["risks"]],
        "",
        f"**Verdict:** {str(payload['verdict']).strip()} Not financial advice.",
    ]
    return "\n".join(sections)


def _parse_json_response(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _ollama_payload_is_valid(candidate: dict[str, Any], payload: dict[str, Any]) -> bool:
    required_fields = {"setup", "why_it_screens_well", "plan", "risks", "verdict", "metric_refs"}
    if not required_fields.issubset(payload):
        return False

    list_fields = ["why_it_screens_well", "plan", "risks", "metric_refs"]
    if not all(isinstance(payload.get(field), list) for field in list_fields):
        return False
    if not all(isinstance(payload.get(field), str) for field in ["setup", "verdict"]):
        return False

    metric_refs = {str(item) for item in payload["metric_refs"]}
    required_refs = {
        "return_1d",
        "return_5d",
        "return_10d",
        "return_20d",
        "volume_ratio_5d",
        "volume_ratio_20d",
        "volume_trend_5d_20d",
        "rel_strength_spy_5d",
        "rel_strength_qqq_5d",
        "sma_5_20_ratio",
        "close_vs_sma_20",
        "up_day_ratio_5d",
        "rsi_14",
        "atr_14_pct",
        "risk_score",
        "confidence_score",
    }
    if not required_refs.issubset(metric_refs):
        return False

    # Require the model to acknowledge the deterministic prediction fields.
    combined = json.dumps(payload).lower()
    return str(candidate.get("expected_direction") or "").lower() in combined


def build_short_term_prompt(candidate: dict[str, Any], rank: int) -> str:
    reasons = ", ".join(candidate.get("reasons") or [])
    allowed_observations = "\n".join(f"- {item}" for item in _allowed_observations(candidate))
    risk_observations = "\n".join(f"- {item}" for item in _risk_observations(candidate))
    return f"""
You are a cautious market research assistant. Return ONLY valid JSON using
the schema below. Use ONLY the facts below.

Rules:
- Do not invent news, catalysts, earnings dates, support/resistance levels, or prices.
- Do not mention moving averages, analyst ratings, macro news, or precise stop prices.
- Do not create new RSI thresholds; only use the current RSI fact or the provided risk notes.
- Do not say "buy" or "guaranteed"; use "candidate", "setup", and "watch".
- Keep it practical for a short holding window, not long-term investing.
- Mention risk clearly using only the allowed risk notes.
- Include a simple invalidation idea: losing momentum or fading relative volume.
- Reference every required metric in metric_refs.

Candidate facts:
- Rank: {rank}
- Symbol: {candidate.get("symbol")}
- Name: {candidate.get("name")}
- Market: {candidate.get("market")}
- Exchange: {candidate.get("exchange")}
- Screener score: {candidate.get("score")}
- Current price: {_num(candidate.get("current_price"))}
- Market cap: {_market_cap(candidate.get("market_cap"))}
- 1-day return: {_pct(candidate.get("return_1d"))}
- 5-day return: {_pct(candidate.get("return_5d"))}
- 10-day return: {_pct(candidate.get("return_10d"))}
- 20-day return: {_pct(candidate.get("return_20d"))}
- Latest volume vs prior 5-day average: {_num(candidate.get("volume_ratio_5d"))}x
- Latest volume vs prior 20-day average: {_num(candidate.get("volume_ratio_20d"))}x
- 5-day volume trend vs 20-day average: {_num(candidate.get("volume_trend_5d_20d"))}x
- Dollar volume: {_market_cap(candidate.get("dollar_volume"))}
- Distance from 5-day high: {_pct(candidate.get("distance_from_5d_high"))}
- Distance from 5-day low: {_pct(candidate.get("distance_from_5d_low"))}
- Distance from 20-day high: {_pct(candidate.get("distance_from_20d_high"))}
- Distance from 20-day low: {_pct(candidate.get("distance_from_20d_low"))}
- SMA 5/20 trend ratio: {_pct(candidate.get("sma_5_20_ratio"))}
- Close vs SMA20: {_pct(candidate.get("close_vs_sma_20"))}
- Up-day ratio 5D: {_pct(candidate.get("up_day_ratio_5d"))}
- Up-day ratio 10D: {_pct(candidate.get("up_day_ratio_10d"))}
- Gap from previous close to latest open: {_pct(candidate.get("gap_1d"))}
- ATR 14 as pct of price: {_pct(candidate.get("atr_14_pct"))}
- RSI 14: {_num(candidate.get("rsi_14"))}
- 5-day relative strength vs SPY: {_pct(candidate.get("rel_strength_spy_5d"))}
- 5-day relative strength vs QQQ: {_pct(candidate.get("rel_strength_qqq_5d"))}
- Setup type: {candidate.get("setup_type")}
- Opportunity score: {_num(candidate.get("opportunity_score"))}
- Risk score: {_num(candidate.get("risk_score"))}
- Risk level: {candidate.get("risk_level")}
- Confidence score: {_num(candidate.get("confidence_score"))}
- Expected direction: {candidate.get("expected_direction")}
- Expected window: {candidate.get("expected_window")}
- Reason codes: {", ".join(candidate.get("reason_codes") or [])}
- Risk flags: {", ".join(candidate.get("risk_flags") or [])}
- Upcoming earnings days: {_num(candidate.get("upcoming_earnings_days"))}
- Valuation context: trailing P/E {_num(candidate.get("trailing_pe"))}, P/B {_num(candidate.get("price_to_book"))}
- Screener signals: {reasons}

Allowed observations to use:
{allowed_observations}

Allowed risk notes to use:
{risk_observations}

Required JSON schema:
{{
  "setup": "1-2 cautious sentences",
  "why_it_screens_well": ["2-4 fact-based bullets"],
  "plan": ["2-4 bullets focused on what to watch"],
  "risks": ["2-4 bullets using only allowed risk notes"],
  "verdict": "one cautious sentence",
  "metric_refs": ["return_1d", "return_5d", "return_10d", "return_20d", "volume_ratio_5d", "volume_ratio_20d", "volume_trend_5d_20d", "rel_strength_spy_5d", "rel_strength_qqq_5d", "sma_5_20_ratio", "close_vs_sma_20", "up_day_ratio_5d", "rsi_14", "atr_14_pct", "risk_score", "confidence_score"]
}}
""".strip()


def generate_short_term_proposals(
    *,
    input_path: Path,
    output_markdown_path: Path,
    output_json_path: Path,
    output_summary_path: Path,
    model: str,
    top: int,
    use_ollama: bool = False,
) -> list[dict[str, Any]]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    candidates = payload.get("candidates", [])[:top]
    if not candidates:
        raise ValueError(f"No candidates found in {input_path}")

    client = OllamaClient(model=model) if use_ollama else None
    if client is not None and not client.is_available():
        print(
            f"Ollama model '{model}' is not available; using fact-only proposals. "
            f"Run 'ollama pull {model}' to enable it."
        )
        client = None

    proposals: list[dict[str, Any]] = []
    markdown_parts = [
        "# Short-Term Research Proposals",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"Model: `{model}`",
        f"Source: `{_display_path(input_path)}`",
        "",
        DISCLAIMER,
        "",
        *_metric_guide(),
    ]

    for rank, candidate in enumerate(candidates, start=1):
        print(f"Generating proposal {rank}/{len(candidates)}: {candidate.get('symbol')}")
        proposal = _deterministic_proposal(candidate)
        used_ollama = False
        if client is not None:
            prompt = build_short_term_prompt(candidate, rank)
            try:
                generated = client.generate(prompt)
            except requests.RequestException:
                generated = ""
            payload = _parse_json_response(generated) if generated else None
            if payload is not None and _ollama_payload_is_valid(candidate, payload):
                proposal = _format_ollama_json(candidate, payload)
                used_ollama = True
            else:
                print(
                    f"Using fact-only fallback for {candidate.get('symbol')} "
                    "because the local model output was unsafe or too broad."
                )
        proposals.append(
            {
                "rank": rank,
                "symbol": candidate.get("symbol"),
                "name": candidate.get("name"),
                "used_ollama": used_ollama,
                "proposal": proposal,
                "source_metrics": candidate,
            }
        )
        markdown_parts.append(proposal)
        markdown_parts.append("")
        markdown_parts.append("---")
        markdown_parts.append("")

    output_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_summary_path.parent.mkdir(parents=True, exist_ok=True)
    output_markdown_path.write_text("\n".join(markdown_parts).strip() + "\n", encoding="utf-8")
    output_json_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "model": model,
                "input": _display_path(input_path),
                "disclaimer": DISCLAIMER,
                "proposals": proposals,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_metrics_summary(candidates, output_summary_path)
    return proposals


SUMMARY_COLUMNS = [
    "rank",
    "symbol",
    "name",
    "market",
    "exchange",
    "score",
    "opportunity_score",
    "risk_score",
    "risk_level",
    "confidence_score",
    "expected_direction",
    "expected_window",
    "setup_type",
    "market_cap",
    "current_price",
    "return_1d",
    "return_5d",
    "return_10d",
    "return_20d",
    "rel_strength_spy_1d",
    "rel_strength_spy_5d",
    "rel_strength_qqq_1d",
    "rel_strength_qqq_5d",
    "volume_ratio_5d",
    "volume_ratio_20d",
    "volume_trend_5d_20d",
    "distance_from_5d_high",
    "distance_from_5d_low",
    "distance_from_20d_high",
    "distance_from_20d_low",
    "gap_1d",
    "sma_5_20_ratio",
    "close_vs_sma_20",
    "up_day_ratio_5d",
    "up_day_ratio_10d",
    "dollar_volume",
    "atr_14_pct",
    "rsi_14",
    "upcoming_earnings_days",
    "risk_flags",
    "reason_codes",
]


def write_metrics_summary(candidates: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        for rank, candidate in enumerate(candidates, start=1):
            row = {column: candidate.get(column) for column in SUMMARY_COLUMNS}
            row["rank"] = rank
            row["risk_flags"] = "; ".join(candidate.get("risk_flags") or [])
            row["reason_codes"] = "; ".join(candidate.get("reason_codes") or [])
            writer.writerow(row)
