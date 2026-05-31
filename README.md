# Short-Term Stock Research Agent

Python tooling for screening US S&P 500 and Finnish Nasdaq Helsinki stocks, then generating short-term research notes for a 1-day to 1-week watchlist. It uses free data sources and local-only generation by default.

> Not financial advice. This project is for research only. Short-term trading is high risk.

## What It Does

- Screens S&P 500 and Nasdaq Helsinki stocks with free Yahoo Finance data through `yfinance`.
- Focuses on short-term candidates using 1-day to 1-week metrics.
- Includes smaller companies down to `min_market_cap` in `config.yaml`.
- Filters out very large companies with `max_market_cap` in `config.yaml`.
- Scores both opportunity and risk. Risk has a non-zero floor because short-term stock risk is never zero.
- Labels setups as `momentum continuation`, `relative strength`, `breakout watch`, `overextended`, `earnings risk`, or `pullback risk`.
- Generates Markdown and JSON proposal notes from the ranked candidates.

## Current Short-Term Signals

- 1-day return
- 5-day return
- 10-day return
- 20-day return
- 5-day and 20-day relative volume
- 5-day volume trend versus 20-day volume
- dollar volume for liquidity context
- distance from 5-day and 20-day highs/lows
- 5-day average versus 20-day average
- close versus 20-day average
- 5-day and 10-day up-day ratios
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
│   ├── evaluate_runs.py
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

Run the configured short-term screen and generate 10 proposals:

```powershell
python scripts\run_short_term_agent.py
```

By default, `config.yaml` loads:

```yaml
universes:
  - sp500
  - finland
```

Run only the US S&P 500 universe:

```powershell
python scripts\run_short_term_agent.py --universe sp500
```

Run only the Finnish universe:

```powershell
python scripts\run_short_term_agent.py --universe finland
```

Run both explicitly:

```powershell
python scripts\run_short_term_agent.py --universe sp500 --universe finland
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

Ollama output must still be valid structured JSON with required metric references. If it fails those structure checks, proposal generation falls back to fact-only notes. The code no longer rejects Ollama output just because it uses specific prohibited words.

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
- enabled `universes`
- valuation filters
- short-term scoring weights

The current default includes smaller companies above roughly `100M` market cap and excludes companies above `$150B` market cap:

```yaml
min_market_cap: 100_000_000
max_market_cap: 150_000_000_000
```

For Finnish names, Yahoo usually reports market cap in the local listing currency, so treat this threshold as approximate. Smaller companies can be less liquid and may have wider spreads.

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

## CI/CD

This project uses GitHub Actions for pull-request validation and main-branch artifact packaging.

Branch flow:

- Push to `dev` runs validation and opens a pull request into `test` if validation passes.
- Review and merge the automated `dev` -> `test` pull request when ready.
- Open pull requests into `main` for release-ready validation.
- Pushes to `main` create a downloadable source zip artifact.

Workflows:

- `.github/workflows/promote-dev-to-test.yml` runs on pushes to `dev`, validates the project, and creates a `dev` -> `test` pull request.
- `.github/workflows/ci.yml` runs on pull requests into `test` and `main`.
- `.github/workflows/release.yml` runs on pushes to `main`.

The CI checks install dependencies, compile the Python files, and run lightweight smoke tests. They intentionally do not run the live screener or Ollama because Yahoo/Wikipedia can rate-limit and Ollama is local to your PC.

The release workflow uploads `stock-agent-source.zip` as a GitHub Actions artifact. The package excludes generated outputs, caches, virtual environments, and local secret files.
