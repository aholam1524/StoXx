"""Generate short-term research proposals from screener candidates."""

from __future__ import annotations

import json
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


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def _allowed_observations(candidate: dict[str, Any]) -> list[str]:
    observations: list[str] = []
    return_1d = candidate.get("return_1d")
    return_5d = candidate.get("return_5d")
    volume_ratio = candidate.get("volume_ratio_5d")
    volume_ratio_20d = candidate.get("volume_ratio_20d")
    distance_high = candidate.get("distance_from_5d_high")
    rsi = candidate.get("rsi_14")
    rel_spy = candidate.get("rel_strength_spy_5d")
    rel_qqq = candidate.get("rel_strength_qqq_5d")
    atr = candidate.get("atr_14_pct")
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
    if volume_ratio is not None:
        observations.append(
            f"Latest volume is {_num(volume_ratio)}x the prior 5-day average."
        )
    if volume_ratio_20d is not None:
        observations.append(
            f"Latest volume is {_num(volume_ratio_20d)}x the prior 20-day average."
        )
    if distance_high is not None:
        observations.append(f"Price is {_pct(distance_high)} from the 5-day high.")
    if rsi is not None:
        observations.append(f"RSI 14 is {_num(rsi)}.")
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
    volume_ratio = candidate.get("volume_ratio_5d")
    volume_ratio_20d = candidate.get("volume_ratio_20d")
    rel_spy = candidate.get("rel_strength_spy_5d")
    rel_qqq = candidate.get("rel_strength_qqq_5d")
    rsi = candidate.get("rsi_14")
    distance_high = candidate.get("distance_from_5d_high")

    if return_5d is not None:
        highlights.append(f"Five-day return is {_pct(return_5d)}.")
    if rel_spy is not None:
        highlights.append(f"5-day relative strength vs SPY is {_pct(rel_spy)}.")
    if rel_qqq is not None:
        highlights.append(f"5-day relative strength vs QQQ is {_pct(rel_qqq)}.")
    if volume_ratio is not None:
        highlights.append(f"Latest volume is {_num(volume_ratio)}x the prior 5-day average.")
    if volume_ratio_20d is not None:
        highlights.append(f"Latest volume is {_num(volume_ratio_20d)}x the prior 20-day average.")
    if distance_high is not None:
        highlights.append(f"Price is {_pct(distance_high)} from the 5-day high.")
    if rsi is not None:
        highlights.append(f"RSI 14 is {_num(rsi)}.")

    return highlights[:5] or ["Short-term composite score ranked highly."]


def _risk_observations(candidate: dict[str, Any]) -> list[str]:
    risks: list[str] = []
    risk_score = candidate.get("risk_score")
    risk_flags = candidate.get("risk_flags") or []

    for flag in risk_flags:
        if flag != "no major short-term risk flags":
            risks.append(flag)

    if risk_score is not None:
        risks.append(f"Risk score is {_num(risk_score)} on a 0 to 1 scale.")
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
            "**Why it screens well:**",
            *[f"- {item}" for item in why],
            f"- Opportunity score is {_num(candidate.get('opportunity_score'))}; risk score is {_num(candidate.get('risk_score'))}.",
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


def _proposal_is_safe(text: str) -> bool:
    banned_terms = [
        " buy",
        "buy:",
        "portfolio",
        "moving average",
        "support",
        "resistance",
        "earnings",
        "analyst",
        "macro",
        "news",
        "guaranteed",
    ]
    lowered = f" {text.lower()}"
    return not any(term in lowered for term in banned_terms)


def build_short_term_prompt(candidate: dict[str, Any], rank: int) -> str:
    reasons = ", ".join(candidate.get("reasons") or [])
    allowed_observations = "\n".join(f"- {item}" for item in _allowed_observations(candidate))
    risk_observations = "\n".join(f"- {item}" for item in _risk_observations(candidate))
    return f"""
You are a cautious market research assistant. Write a very concise 1-day to
1-week short-term trading research note using ONLY the facts below.

Rules:
- Do not invent news, catalysts, earnings dates, support/resistance levels, or prices.
- Do not mention moving averages, analyst ratings, macro news, or precise stop prices.
- Do not create new RSI thresholds; only use the current RSI fact or the provided risk notes.
- Do not say "buy" or "guaranteed"; use "candidate", "setup", and "watch".
- Keep it practical for a short holding window, not long-term investing.
- Mention risk clearly using only the allowed risk notes.
- Include a simple invalidation idea: losing momentum or fading relative volume.
- End with: "Not financial advice."

Candidate facts:
- Rank: {rank}
- Symbol: {candidate.get("symbol")}
- Name: {candidate.get("name")}
- Screener score: {candidate.get("score")}
- Current price: {_num(candidate.get("current_price"))}
- Market cap: {_market_cap(candidate.get("market_cap"))}
- 1-day return: {_pct(candidate.get("return_1d"))}
- 5-day return: {_pct(candidate.get("return_5d"))}
- Latest volume vs prior 5-day average: {_num(candidate.get("volume_ratio_5d"))}x
- Distance from 5-day high: {_pct(candidate.get("distance_from_5d_high"))}
- Distance from 5-day low: {_pct(candidate.get("distance_from_5d_low"))}
- 20-day return: {_pct(candidate.get("return_20d"))}
- Latest volume vs prior 20-day average: {_num(candidate.get("volume_ratio_20d"))}x
- Gap from previous close to latest open: {_pct(candidate.get("gap_1d"))}
- ATR 14 as pct of price: {_pct(candidate.get("atr_14_pct"))}
- RSI 14: {_num(candidate.get("rsi_14"))}
- 5-day relative strength vs SPY: {_pct(candidate.get("rel_strength_spy_5d"))}
- 5-day relative strength vs QQQ: {_pct(candidate.get("rel_strength_qqq_5d"))}
- Setup type: {candidate.get("setup_type")}
- Opportunity score: {_num(candidate.get("opportunity_score"))}
- Risk score: {_num(candidate.get("risk_score"))}
- Risk flags: {", ".join(candidate.get("risk_flags") or [])}
- Upcoming earnings days: {_num(candidate.get("upcoming_earnings_days"))}
- Valuation context: trailing P/E {_num(candidate.get("trailing_pe"))}, P/B {_num(candidate.get("price_to_book"))}
- Screener signals: {reasons}

Allowed observations to use:
{allowed_observations}

Allowed risk notes to use:
{risk_observations}

Required format:
### SYMBOL - NAME
**Setup:** 1-2 sentences.
**Why it screens well:** 2 bullets.
**1-day to 1-week plan:** 2 bullets focused on what to watch.
**Main risks:** 2 bullets.
**Verdict:** one sentence.
""".strip()


def generate_short_term_proposals(
    *,
    input_path: Path,
    output_markdown_path: Path,
    output_json_path: Path,
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
            if generated and _proposal_is_safe(generated):
                proposal = generated
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
    return proposals
