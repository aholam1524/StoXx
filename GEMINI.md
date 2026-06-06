# Project Instructions: fproject

This file contains team-shared architecture, conventions, and workflows for the `fproject` repository.

## Project Overview
A Python-based project involving financial data fetching, screening, and an agent-based proposal generation system.

## Model Accuracy Improvements (June 2026)
- **Wilder's Smoothing:** RSI and ATR now use Wilder's Smoothing (EMA-based) instead of simple averages, aligning with market standards and reducing indicator lag.
- **Ratio-Based Relative Strength:** Switched from absolute subtraction to ratio-based performance comparison (`(1+r)/(1+benchmark)-1`) for better mathematical consistency.
- **Regime-Aware Weighting:** Factor weights (Trend, Momentum, etc.) now adapt dynamically based on the detected market regime (Supportive, Mixed, or Weak).
- **Volatility-Adjusted Risk:** Extension risk assessment now prioritizes `stretch_vs_atr` to tailor risk thresholds to each stock's unique volatility profile.

## Key Directories
- `src/agent/`: Agent logic and clients (e.g., Ollama).
- `src/data/`: Data fetchers for various markets (S&P 400, S&P 500, Finland).
- `src/models/`: Data models and candidate definitions.
- `src/screen/`: Scoring and screening logic.
- `scripts/`: Execution scripts for running the agent and evaluation.
- `tests/`: Smoke tests and unit tests.

## Conventions
- **Language:** Python 3.x
- **Testing:** Use `pytest` for running tests (based on `tests/` directory).
- **Environment:** Dependencies are managed via `requirements.txt`.
- **Code Style:** Follow standard Python (PEP 8) conventions.

## Workflows
- **Running the Agent:** Use `python scripts/run_short_term_agent.py`.
- **Fetching Data:** Use modules in `src/data/`.
- **Evaluation:** Run `python scripts/evaluate_runs.py`.
