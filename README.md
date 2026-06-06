# Short-Term Stock Research Agent

Python tooling for screening US S&P 500, S&P MidCap 400, and Finnish Nasdaq Helsinki stocks, then generating short-term research notes for a 1-day to 1-week watchlist. It uses free data sources and local-only generation by default.

> Not financial advice. This project is for research only. Short-term trading is high risk.

See `outputs/proposals.md` for a committed sample generated report. Live run history under `outputs/runs/` and the moving latest copy under `outputs/latest/` are ignored by Git.

## What It Does

- Screens S&P 500, S&P MidCap 400, and Nasdaq Helsinki stocks with free Yahoo Finance data through `yfinance`.
- Focuses on short-term candidates using 1-day to 1-week metrics.
- Includes smaller companies down to `min_market_cap` in `config.yaml`.
- Filters out very large companies with `max_market_cap` in `config.yaml`.
- Scores both opportunity and risk. Risk has a non-zero floor because short-term stock risk is never zero.
- Labels setups as `momentum continuation`, `relative strength`, `breakout watch`, `overextended`, `earnings risk`, or `pullback risk`.
- Generates Markdown, JSON, and CSV proposal notes from the ranked candidates.
- Adds setup and lifecycle diagnostics to explain whether a candidate looks more like continuation, exhaustion, reversal, or volatility expansion.

## Current Short-Term Signals

- Recent returns: 1-day, 5-day, 10-day, and 20-day returns.
- Trend structure: 5-day average versus 20-day average, close versus 20-day average, and 5-day/10-day up-day ratios.
- Range position: distance from 5-day and 20-day highs/lows, plus close location inside the 1-day, 5-day, and 20-day ranges.
- Benchmark context: relative strength versus `SPY` and `QQQ` across multiple windows.
- Sector context: relative strength versus the median return of same-sector names in the screened universe.
- Market regime: broad `SPY`/`QQQ` backdrop score and regime label.
- Volume participation: 5-day and 20-day relative volume, 5-day volume trend versus 20-day volume, elevated-volume persistence, and latest-volume z-score.
- Volume quality: up-volume/down-volume ratio, volume acceleration, price/volume efficiency, effort-versus-result, and distribution-day count.
- Liquidity context: dollar volume and liquidity tier.
- Extension and volatility: RSI 14, ATR 14 as percent of price, gap from previous close to latest open, and stretch versus ATR.
- Failure detectors: failed gap or intraday fade, relative-strength decoupling, and distribution pressure.
- Setup diagnostics: scores for trend confirmation, momentum continuation, breakout watch, and pullback risk.
- Lifecycle diagnostics: heuristic phase scores for ignition, expansion, euphoria, exhaustion, and reversal, plus continuation/mean-reversion/volatility-expansion probabilities.
- Upcoming earnings risk when available.

## Project Layout

```text
.
├── config.yaml
├── main.py
├── requirements.txt
├── data/
│   └── sp400_symbols.txt
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
    ├── .gitkeep
    └── proposals.md
```

Generated files in `outputs/` are ignored by Git to avoid committing machine-specific paths or stale research results. The exception is `outputs/proposals.md`, which is intentionally committed as a sample report.

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

Run the configured short-term screen. By default this saves the top 150 candidates for evaluation/calibration and generates proposals for the top 10:

```powershell
python scripts\run_short_term_agent.py
```

By default, `config.yaml` loads:

```yaml
universes:
  - sp500
  - sp400
  - finland
```

Run only the US S&P 500 universe:

```powershell
python scripts\run_short_term_agent.py --universe sp500
```

Run only the S&P MidCap 400 universe:

```powershell
python scripts\run_short_term_agent.py --universe sp400
```

Run only the Finnish universe:

```powershell
python scripts\run_short_term_agent.py --universe finland
```

Run the US universes explicitly:

```powershell
python scripts\run_short_term_agent.py --universe sp500 --universe sp400
```

Run all universes explicitly:

```powershell
python scripts\run_short_term_agent.py --universe sp500 --universe sp400 --universe finland
```

Useful faster test:

```powershell
python scripts\run_short_term_agent.py --limit 80 --top 10 --proposal-top 5
```

Each run creates a timestamped history folder:

```text
outputs/runs/YYYY-MM-DD_HH-MM-SS_utc_all/
├── screen_results.json
├── proposals.md
├── proposals.json
├── metrics_summary.csv
├── backtest_result.json
└── calibration_suggestions.json
```

The suffix shows the screened universe: `_all`, `_us`, `_sp400`, `_finland`, or `_custom-...`.

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
python scripts\evaluate_runs.py --run-dir outputs\runs\YYYY-MM-DD_HH-MM-SS_utc_all
```

Evaluate only recent runs:

```powershell
python scripts\evaluate_runs.py --last-days 5
python scripts\evaluate_runs.py --last-runs 5
```

Paper-trade returns use default costs of 0.10% commission per side and 30% tax on positive profit after commission. Override them if needed:

```powershell
python scripts\evaluate_runs.py --last-days 5 --commission-rate 0.001 --tax-rate 0.30
```

This writes:

```text
outputs/runs/YYYY-MM-DD_HH-MM-SS_utc_all/backtest_result.json
outputs/runs/YYYY-MM-DD_HH-MM-SS_utc_all/calibration_suggestions.json
outputs/paper_trade_summary.json
```

`backtest_result.json` includes candidate-level 1D/3D/5D forward returns plus net paper-trade simulations for equal-weight top-10 portfolios. `paper_trade_summary.json` aggregates evaluated runs with win rate, average winner/loser, drawdown, turnover, and SPY/QQQ comparisons. Use `calibration_suggestions.json` to decide which short-term scoring weights, risk penalties, or entry-quality checks should be increased or reduced after enough completed runs exist.

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
- except `outputs/proposals.md`, which is a committed sample report
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
