# Free Short-Term S&P 500 Research Agent

Python tooling for screening S&P 500 stocks and generating short-term research notes for a 1-day to 1-week watchlist. It uses free data sources and local-only generation by default.

> Not financial advice. This project is for research only. Short-term trading is high risk.

## What It Does

- Screens S&P 500 stocks with free Yahoo Finance data through `yfinance`.
- Focuses on short-term candidates using 1-day to 1-week metrics.
- Filters out very large companies with `max_market_cap` in `config.yaml`.
- Scores both opportunity and risk.
- Labels setups as `momentum continuation`, `relative strength`, `breakout watch`, `overextended`, `earnings risk`, or `pullback risk`.
- Generates Markdown and JSON proposal notes from the ranked candidates.

## Current Short-Term Signals

- 1-day return
- 5-day return
- 20-day return
- 5-day and 20-day relative volume
- distance from 5-day high and low
- RSI 14
- ATR 14 as percent of price
- gap from previous close to latest open
- relative strength vs `SPY` and `QQQ`
- upcoming earnings risk when available

## Project Layout

```text
.
├── config.yaml
├── main.py
├── requirements.txt
├── scripts/
│   ├── generate_proposals.py
│   ├── run_short_term_agent.py
│   └── verify_ssl.py
├── src/
│   ├── agent/
│   ├── data/
│   ├── models/
│   └── screen/
└── outputs/
    └── .gitkeep
```

Generated files in `outputs/` are ignored by Git to avoid committing machine-specific paths or stale research results.

## Setup

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

If Windows certificate verification fails, check:

```powershell
python scripts\verify_ssl.py
```

## Run The Short-Term Agent

Run the full S&P 500 short-term screen and generate 10 proposals:

```powershell
python scripts\run_short_term_agent.py
```

Useful faster test:

```powershell
python scripts\run_short_term_agent.py --limit 80 --top 10 --proposal-top 10
```

Each run creates a timestamped history folder:

```text
outputs/runs/YYYYMMDD_HHMMSS/
├── screen_results.json
├── proposals.md
├── proposals.json
├── metrics_summary.csv
├── backtest_result.json
└── calibration_suggestions.json
```

The newest run is also copied to:

```text
outputs/latest/
├── screen_results.json
├── proposals.md
├── proposals.json
└── metrics_summary.csv
```

## Run Only The Screener

```powershell
python main.py --mode short-term --top 10
```

Run the original value-oriented screen:

```powershell
python main.py --mode value --top 10
```

## Run Only Proposal Generation

Use the latest `outputs/screen_results.json`:

```powershell
python scripts\generate_proposals.py --top 10
```

This also creates a new `outputs/runs/<timestamp>/` proposal history folder and updates `outputs/latest/`.

By default, proposals are deterministic and fact-only. Optional Ollama wording can be tested with:

```powershell
python scripts\generate_proposals.py --top 10 --use-ollama
```

Unsafe or overly broad Ollama output falls back to fact-only notes.

## Evaluate Old Runs

After at least one later trading day has passed, evaluate historical runs:

```powershell
python scripts\evaluate_runs.py
```

Evaluate one specific run:

```powershell
python scripts\evaluate_runs.py --run-dir outputs\runs\YYYYMMDD_HHMMSS
```

This writes:

```text
outputs/runs/YYYYMMDD_HHMMSS/backtest_result.json
outputs/runs/YYYYMMDD_HHMMSS/calibration_suggestions.json
```

Use `calibration_suggestions.json` to decide which short-term scoring weights or risk penalties should be increased or reduced after enough completed runs exist.

## Configuration

Edit `config.yaml` to tune:

- `min_market_cap`
- `max_market_cap`
- valuation filters
- short-term scoring weights

The current default excludes companies above `$150B` market cap:

```yaml
max_market_cap: 150_000_000_000
```

## GitHub Safety

The `.gitignore` excludes:

- generated files in `outputs/`
- Python cache files
- virtual environments
- `.env` and secret-like files
- editor and OS noise

Generated history folders under `outputs/runs/` are local-only by default. They are useful for comparing old proposal runs, but they are ignored by Git.

Before pushing, check:

```powershell
git status --short
```

Do not commit generated proposal/result files if they contain time-sensitive research output.

python scripts\run_short_term_agent.py --use-ollama to run agent
