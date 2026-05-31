# Short-Term Research Proposals

Generated at: 2026-05-31T11:00:02.985332+00:00
Model: `qwen2.5:0.5b`
Source: `outputs/runs/20260531_105712/screen_results.json`

Not financial advice. Short-term trading is high risk. Use this only as research and define your own position sizing and risk limits.

## How To Read This Report

Each candidate starts with a quick scorecard and plain-English factor notes. The detailed formula math is included in a collapsible section so the report stays readable while remaining auditable.

### Score Basics

- **Factor scores:** 0 to 1 scores for trend, momentum, relative strength, participation, and extension control.
- **Percentile rank (`pct`):** Where the metric sits inside the screened universe. `0.90` means stronger than about 90% of screened names for that metric.
- **Z-score (`z`):** How unusual the raw value is versus the screened universe average. Positive is above average; negative is below average.
- **Weight:** The component's influence inside that factor formula.
- **Regime language:** The setup describes a conditional market regime, not a price forecast.

### Risk Target Ranges

- **Low risk:** < 0.25. No major risk bucket is elevated, though normal short-term market risk still applies.
- **Medium risk:** 0.25-0.49. At least one risk bucket is moderately elevated and should be monitored.
- **High risk:** >= 0.50. Extension, volatility, liquidity, trend failure, or event risk is materially elevated.
- **Risk buckets:** extension, volatility, liquidity/participation, trend failure, and earnings/event timing.

### Factor Target Ranges

- **General score guide:** >= 0.70 is strong/good, 0.45-0.69 is mixed/watch, and < 0.45 is weak or risky for that bucket.
- **Trend:** Good: score >= 0.70 with price above SMA20, positive SMA 5/20, and frequent up days. Mixed: 0.45-0.69. Weak: < 0.45 or price structure below average.
- **Momentum:** Good: score >= 0.70 with positive 5D/10D/20D returns. Mixed: 0.45-0.69. Weak: < 0.45 or fading/negative recent returns.
- **Relative strength:** Good: score >= 0.70 with positive SPY/QQQ outperformance, especially 10D/20D. Mixed: 0.45-0.69. Weak: < 0.45 or benchmark underperformance.
- **Participation:** Good: score >= 0.70 with relative volume > 1.0x, positive volume z-score, persistence, and non-thin liquidity. Mixed: 0.45-0.69. Weak: < 0.45 or thin/fading volume.
- **Extension control:** Good: score >= 0.70 means less stretched. Mixed: 0.45-0.69. Risky: < 0.45, often from high RSI, high ATR, a large gap, or being far above the 20D low.

### Factor Glossary

- **Trend:** Price structure: longer-window return, short-vs-medium moving average alignment, close vs SMA20, and recent up-day consistency.
- **Momentum:** Recent price movement across 1D, 5D, 10D, and 20D windows.
- **Relative Strength:** Outperformance or underperformance versus SPY and QQQ across multiple windows.
- **Participation:** Volume and liquidity support: relative volume, persistence of elevated volume, volume z-score, and dollar volume.
- **Extension:** Stretch/risk control: RSI, ATR, gap size, move-vs-ATR, and position above the 20D low. Higher is less stretched.

### Metric Glossary

- **score:** Composite rank score used to order candidates.
- **opportunity_score:** Weighted average of factor scores before risk adjustment.
- **risk_score:** Continuous short-term risk score from extension, volatility, liquidity, trend failure, and event components.
- **risk_details:** Component-level breakdown of the risk score, including weights, contributions, and metric scores.
- **confidence_score:** Blend of opportunity and risk; it is not a price prediction.
- **return_1d/5d/10d/20d:** Recent total return over the named trading window.
- **rel_strength_*:** Candidate return minus SPY or QQQ return for the same window.
- **sector_relative_strength_*:** Candidate return minus the median return of its sector peers in the screened universe.
- **market_regime_score:** Broad SPY/QQQ backdrop score from recent benchmark trend and moving-average position.
- **close_location_1d/5d/20d:** Where the close sits inside the day or recent range; 1.0 means near the high.
- **volume_ratio_5d/20d:** Latest volume divided by the prior 5D or 20D average.
- **volume_trend_5d_20d:** Recent 5D average volume divided by the 20D average volume.
- **volume_persistence_5d/10d:** Share of recent days with volume above the 20D average.
- **up_volume_ratio_10d:** Volume on up days divided by volume on down days over the last 10 sessions.
- **volume_acceleration_5d_20d:** Latest volume participation versus the recent 5D/20D volume trend.
- **price_volume_efficiency_5d:** 5D return per unit of relative volume; falling efficiency can warn of exhaustion.
- **effort_vs_result_5d:** Volume effort divided by absolute 5D price result; high values can mean heavy effort with little progress.
- **distribution_day_count_10d:** Count of recent down days with above-average volume.
- **volume_z_score_20d:** How many standard deviations latest volume is from the trailing 20D average.
- **liquidity_tier:** Dollar-volume bucket: high, medium, low, or thin.
- **dollar_volume:** Latest close multiplied by latest volume.
- **sma_5_20_ratio:** 5D average price versus 20D average price.
- **close_vs_sma_20:** Latest close versus the 20D average price.
- **up_day_ratio_5d/10d:** Share of recent sessions that closed higher than the prior session.
- **distance_from_5d/20d_high:** How far the latest close is below or above the recent high.
- **distance_from_5d/20d_low:** How far the latest close is above the recent low.
- **atr_14_pct:** 14D average true range as a percent of price; higher means more volatility.
- **rsi_14:** 14D relative strength index; high values can indicate stretch.
- **gap_1d:** Latest open compared with the prior close.
- **failed_gap_or_fade:** True when a gap/strong session closes weakly inside the daily range.
- **rs_decoupling:** True when price rises but relative-strength momentum fades.
- **distribution_pressure:** True when multiple high-volume down days suggest distribution.
- **setup_details:** Setup-specific scores used to diagnose which setup style the candidate best fits.
- **lifecycle_details:** Heuristic phase/regime diagnostics such as ignition, expansion, euphoria, exhaustion, and reversal.
- **upcoming_earnings_days:** Days until earnings; negative means the date is already past.

### NUE - Nucor Corporation
**Setup:** NUE is a trend confirmation candidate based on the current 1-day to 1-week screen. The setup is a conditional market regime, not a standalone price forecast.

**Quick scorecard:**
- **Factor scores:** trend 0.86; momentum 0.88; relative strength 0.89; participation 0.80; extension control 0.36.
- **Read this as:** higher trend/momentum/relative strength/participation is better; higher extension control means less stretched.
- Trend 0.86: SMA 5/20 4.9%, close vs SMA20 7.6%, 20D close location 95.6%, market regime supportive.
- Momentum 0.88: acceleration 6.7%, 1D 0.3%, 5D close location 94.2%, price/volume efficiency 4.1%.
- Relative strength 0.89: strongest window 5D vs SPY 8.6% (pct n/a); 5D SPY 8.6%, RS momentum 7.1%, 10D sector 6.2%.
- Participation 0.80: volume z-score 6.06, 5D persistence 80.0%, 10D persistence 40.0% (pct 0.53), volume acceleration 1.58, up/down volume 2.70x, efficiency 4.1%, liquidity tier high ($847.0M).
- Extension control 0.36: RSI 72.92, ATR14 2.3%, gap -0.1%, 20D low distance 13.9%, fade/distribution flags False/False.

<details>
<summary><strong>Formula details</strong> - expand for component math</summary>

Component fields: `raw` is the observed value, `pct` is screened-universe percentile, `z` is standard deviations from average, `weight` is formula influence, and `score` is the component score after direction adjustment.

**Trend**
- Meaning: Price structure: longer-window return, short-vs-medium moving average alignment, close vs SMA20, and recent up-day consistency.
- Formula: `0.35 * pct_rank(sma_5_20_ratio) + 0.25 * pct_rank(close_vs_sma_20) + 0.15 * pct_rank(up_day_ratio_10d) + 0.15 * pct_rank(close_location_20d) + 0.10 * pct_rank(market_regime_score)`
  - sma_5_20_ratio: raw 4.90%; pct 0.89; z 1.07; weight 0.35; score 0.89.
  - close_vs_sma_20: raw 7.65%; pct 0.90; z 1.12; weight 0.25; score 0.90.
  - up_day_ratio_10d: raw 70.00%; pct 0.87; z 1.19; weight 0.15; score 0.87.
  - close_location_20d: raw 95.64%; pct 0.93; z 1.50; weight 0.15; score 0.93.
  - market_regime_score: raw 0.91; pct 0.50; z n/a; weight 0.10; score 0.50.

**Momentum**
- Meaning: Recent price movement across 1D, 5D, 10D, and 20D windows.
- Formula: `0.35 * pct_rank(momentum_acceleration_5d_10d) + 0.15 * pct_rank(return_1d) + 0.20 * pct_rank(close_location_5d) + 0.15 * pct_rank(rs_momentum_5d_20d) + 0.15 * pct_rank(price_volume_efficiency_5d)`
  - momentum_acceleration_5d_10d: raw 6.72%; pct 0.96; z 2.03; weight 0.35; score 0.96.
  - return_1d: raw 0.28%; pct 0.64; z 0.14; weight 0.15; score 0.64.
  - close_location_5d: raw 94.16%; pct 0.93; z 1.54; weight 0.20; score 0.93.
  - rs_momentum_5d_20d: raw 0.07; pct 0.93; z 1.49; weight 0.15; score 0.93.
  - price_volume_efficiency_5d: raw 4.07%; pct 0.84; z 0.64; weight 0.15; score 0.84.

**Relative Strength**
- Meaning: Outperformance or underperformance versus SPY and QQQ across multiple windows.
- Formula: `0.25 * pct_rank(rs_momentum_5d_20d) + 0.20 * pct_rank(rel_strength_spy_10d) + 0.15 * pct_rank(rel_strength_qqq_10d) + 0.15 * pct_rank(sector_relative_strength_5d) + 0.15 * pct_rank(sector_relative_strength_10d) + 0.10 * pct_rank(sector_relative_strength_20d)`
  - rs_momentum_5d_20d: raw 0.07; pct 0.93; z 1.49; weight 0.25; score 0.93.
  - rel_strength_spy_10d: raw 6.25%; pct 0.85; z 0.67; weight 0.20; score 0.85.
  - rel_strength_qqq_10d: raw 4.79%; pct 0.85; z 0.67; weight 0.15; score 0.85.
  - sector_relative_strength_5d: raw 9.86%; pct 0.95; z 1.61; weight 0.15; score 0.95.
  - sector_relative_strength_10d: raw 6.17%; pct 0.85; z 0.67; weight 0.15; score 0.85.
  - sector_relative_strength_20d: raw 11.30%; pct 0.88; z 0.95; weight 0.10; score 0.88.

**Participation**
- Meaning: Volume and liquidity support: relative volume, persistence of elevated volume, volume z-score, and dollar volume.
- Formula: `0.14 * pct_rank(volume_acceleration_5d_20d) + 0.14 * pct_rank(volume_ratio_5d) + 0.10 * pct_rank(volume_trend_5d_20d) + 0.14 * pct_rank(volume_persistence_5d) + 0.14 * pct_rank(volume_persistence_10d) + 0.10 * pct_rank(volume_z_score_20d) + 0.10 * pct_rank(up_volume_ratio_10d) + 0.10 * pct_rank(price_volume_efficiency_5d) + 0.05 * pct_rank(dollar_volume)`
  - volume_acceleration_5d_20d: raw 1.58x; pct 0.83; z 0.62; weight 0.14; score 0.83.
  - volume_ratio_5d: raw 2.56x; pct 0.85; z 0.71; weight 0.14; score 0.85.
  - volume_trend_5d_20d: raw 0.98x; pct 0.68; z 0.22; weight 0.10; score 0.68.
  - volume_persistence_5d: raw 80.00%; pct 0.91; z 1.54; weight 0.14; score 0.91.
  - volume_persistence_10d: raw 40.00%; pct 0.53; z 0.04; weight 0.14; score 0.53.
  - volume_z_score_20d: raw 6.06; pct 0.91; z 1.16; weight 0.10; score 0.91.
  - up_volume_ratio_10d: raw 2.70x; pct 0.89; z 0.66; weight 0.10; score 0.89.
  - price_volume_efficiency_5d: raw 4.07%; pct 0.84; z 0.64; weight 0.10; score 0.84.
  - dollar_volume: raw $846,975,000; pct 0.80; z 0.65; weight 0.05; score 0.80.

**Extension**
- Meaning: Stretch/risk control: RSI, ATR, gap size, move-vs-ATR, and position above the 20D low. Higher is less stretched.
- Formula: `0.24 * pct_rank(rsi_control) + 0.24 * (1 - pct_rank(atr_14_pct)) + 0.19 * (1 - pct_rank(stretch_vs_atr)) + 0.14 * (1 - pct_rank(distance_from_20d_low)) + 0.10 * (1 - pct_rank(abs_gap_1d)) + 0.05 * (1 - pct_rank(failed_gap_or_fade)) + 0.05 * (1 - pct_rank(distribution_pressure))`
  - rsi_control: raw 0.60; pct 0.20; z -0.63; weight 0.24; score 0.20.
  - atr_14_pct: raw 2.30%; pct 0.38; z -0.46; weight 0.24; score 0.62.
  - stretch_vs_atr: raw 4.53x; pct 0.98; z 2.47; weight 0.19; score 0.02.
  - distance_from_20d_low: raw 13.90%; pct 0.84; z 0.61; weight 0.14; score 0.16.
  - abs_gap_1d: raw 0.00; pct 0.15; z -0.58; weight 0.10; score 0.85.
  - failed_gap_or_fade: raw 0.00; pct 0.49; z -0.10; weight 0.05; score 0.51.
  - distribution_pressure: raw 0.00; pct 0.38; z -0.57; weight 0.05; score 0.62.

</details>

<details>
<summary><strong>Risk details</strong> - expand for component math</summary>

Risk fields: `score` is the bucket risk from 0 to 1, `weight` is bucket influence, and `contribution` is the weighted risk added to the final score.

**Extension Risk**
- Score 0.47; weight 0.33; contribution 0.15; severity moderate.
- Evidence: RSI 72.92, 5D return 10.4%, 10D return 7.4%, 20D low distance 13.9%
  - rsi_14: raw 72.92; risk score 0.65; range 60.00-80.00.
  - return_5d: raw 10.40%; risk score 0.53; range 0.04-0.16.
  - return_10d: raw 7.37%; risk score 0.00; range 0.08-0.24.
  - return_20d: raw 10.97%; risk score 0.05; range 0.10-0.30.
  - distance_from_20d_low: raw 13.90%; risk score 0.29; range 0.08-0.28.
  - distance_from_20d_high: raw -0.55%; risk score 0.74; range -0.08-0.02.
  - stretch_vs_atr: raw 4.53x; risk score 1.00; range 1.00-3.50.

**Volatility Risk**
- Score 0.02; weight 0.20; contribution 0.00; severity low.
- Evidence: ATR14 2.3%, gap -0.1%, 1D return 0.3%, fade/distribution False/False
  - atr_14_pct: raw 2.30%; risk score 0.06; range 0.02-0.07.
  - abs_gap_1d: raw 0.00; risk score 0.00; range 0.01-0.06.
  - abs_return_1d: raw 0.00; risk score 0.00; range 0.02-0.08.
  - failed_gap_or_fade: raw n/a; risk score n/a; range n/a-n/a.
  - distribution_pressure: raw n/a; risk score n/a; range n/a-n/a.

**Liquidity/Participation Risk**
- Score 0.27; weight 0.20; contribution 0.05; severity low.
- Evidence: tier high, dollar volume $847.0M, 5D volume 2.56x
  - liquidity_tier: raw n/a; risk score 0.00; range n/a-n/a.
  - dollar_volume: raw $846,975,000; risk score 0.00; range 5000000.00-100000000.00.
  - volume_ratio_5d: raw 2.56x; risk score 0.42; range 1.50-4.00.
  - volume_persistence_10d: raw 40.00%; risk score 0.67; range 0.20-0.80.

**Trend Failure Risk**
- Score 0.00; weight 0.15; contribution 0.00; severity low.
- Evidence: close vs SMA20 7.6%, SMA 5/20 4.9%, up-day ratio 10D 70.0%, RS decoupling False
  - close_vs_sma_20: raw 7.65%; risk score 0.00; range 0.00-0.08.
  - sma_5_20_ratio: raw 4.90%; risk score 0.00; range 0.00-0.06.
  - up_day_ratio_10d: raw 70.00%; risk score 0.00; range 0.30-0.70.
  - rs_decoupling: raw n/a; risk score n/a; range n/a-n/a.

**Event Risk**
- Score 0.00; weight 0.12; contribution 0.00; severity low.
- Evidence: earnings in -33.62 days
  - upcoming_earnings_days: raw -33.62; risk score 0.00; range n/a-n/a.

</details>

**Setup diagnostics:**
- Best diagnostic setup: breakout watch with score 0.87.
- trend confirmation: 0.85.
- momentum continuation: 0.78.
- breakout watch: 0.87.
- pullback risk: 0.25.

**Lifecycle and failure diagnostics:**
- Current phase estimate: ignition.
- Regime probabilities: continuation 0.82; mean reversion 0.25; volatility expansion 0.48.
- Phase scores: ignition 0.93; expansion 0.77; euphoria 0.69; exhaustion 0.06; reversal 0.08.
- Failure signals: poor efficiency 0.00; distribution False; fade False; RS decoupling False.
- Note: Heuristic regime probabilities; not yet calibrated to historical forward outcomes.

**Metrics:**
- **Snapshot:** US / S&P 500 / NYSE/Nasdaq; price 250.00; market cap $56.94B.
- **Scores:** rank 0.78; opportunity 0.78; risk 0.21 (low); confidence 0.78.
- **Regime:** bullish regime if conditions persist over 1d-5d; setup trend confirmation.

**Price action:**
- Returns: 1D 0.28%; 5D 10.40%; 10D 7.37%; 20D 10.97%.
- Trend quality: SMA 5/20 4.90%; close vs SMA20 7.65%; up days 5D 100.00%; up days 10D 70.00%.
- Range and volatility: 5D high -0.55%; 5D low 9.85%; 20D high -0.55%; 20D low 13.90%; close location 1D 64.27%; 5D 94.16%; 20D 95.64%; ATR14 2.30%; gap -0.08%; RSI14 72.92; fade flag False.
- Acceleration/failure: momentum acceleration 6.72%; RS momentum 7.13%; RS decoupling False; distribution pressure False.

**Benchmark relative strength:**
- Versus SPY: 1D 0.03%; 5D 8.55%; 10D 6.25%; 20D 5.71%.
- Versus QQQ: 1D -0.09%; 5D 7.07%; 10D 4.79%; 20D 0.40%.
- Versus sector peers: 5D 9.86%; 10D 6.17%; 20D 11.30%.
- Market regime: 0.91 (supportive).

**Volume and liquidity:**
- Relative volume: 5D 2.56x; 20D 2.51x; 5D/20D trend 0.98x.
- Participation evidence: volume z-score 6.06; elevated-volume persistence 5D 80.00%; 10D 40.00%; up/down volume 10D 2.70x.
- Volume quality: acceleration 1.58; price/volume efficiency 4.07%; effort/result 24.58x; distribution days 10D 0.00.
- Liquidity: tier high; dollar volume $846,975,000.

**Other context:**
- Upcoming earnings days: -33.62.

**Why it screens well:**
- Trend 0.86: SMA 5/20 4.9%, close vs SMA20 7.6%, 20D close location 95.6%, market regime supportive.
- Momentum 0.88: acceleration 6.7%, 1D 0.3%, 5D close location 94.2%, price/volume efficiency 4.1%.
- Relative strength 0.89: strongest window 5D vs SPY 8.6% (pct n/a); 5D SPY 8.6%, RS momentum 7.1%, 10D sector 6.2%.
- Participation 0.80: volume z-score 6.06, 5D persistence 80.0%, 10D persistence 40.0% (pct 0.53), volume acceleration 1.58, up/down volume 2.70x, efficiency 4.1%, liquidity tier high ($847.0M).
- Extension control 0.36: RSI 72.92, ATR14 2.3%, gap -0.1%, 20D low distance 13.9%, fade/distribution flags False/False.
- Opportunity score is 0.78; risk score is 0.21.
- Factor reason codes: TREND_CONSTRUCTIVE, MOMENTUM_POSITIVE, RELATIVE_STRENGTH_SUPPORTIVE, PARTICIPATION_EXPANDING, EXTENSION_ELEVATED, RSI_STRETCHED.

**1-day to 1-week plan:**
- Watch whether the stock continues to outperform SPY/QQQ over the next session.
- Watch whether relative volume stays supportive; fading volume weakens the setup.
- Treat loss of factor support plus fading relative volume as invalidation.

**Main risks:**
- moderate extension risk: RSI 72.92, 5D return 10.4%, 10D return 7.4%, 20D low distance 13.9%
- Risk score is 0.21 (low) on a continuous 0 to 1 scale.

**Verdict:** This is a watchlist candidate for short-term research only; the setup depends on momentum and volume staying intact. Not financial advice.

---

### STLD - Steel Dynamics, Inc.
**Setup:** STLD is a trend confirmation candidate based on the current 1-day to 1-week screen. The setup is a conditional market regime, not a standalone price forecast.

**Quick scorecard:**
- **Factor scores:** trend 0.85; momentum 0.87; relative strength 0.93; participation 0.78; extension control 0.29.
- **Read this as:** higher trend/momentum/relative strength/participation is better; higher extension control means less stretched.
- Trend 0.85: SMA 5/20 6.7%, close vs SMA20 9.4%, 20D close location 93.3%, market regime supportive.
- Momentum 0.87: acceleration 6.8%, 1D -0.2%, 5D close location 90.2%, price/volume efficiency 6.4%.
- Relative strength 0.93: strongest window 5D vs SPY 10.4% (pct n/a); 5D SPY 10.4%, RS momentum 8.2%, 10D sector 9.7%.
- Participation 0.78: volume z-score 6.47, 5D persistence 100.0%, 10D persistence 70.0% (pct 0.93), volume acceleration 0.80, up/down volume 1.27x, efficiency 6.4%, liquidity tier high ($551.3M).
- Extension control 0.29: RSI 70.87, ATR14 2.9%, gap -0.1%, 20D low distance 18.8%, fade/distribution flags False/False.

<details>
<summary><strong>Formula details</strong> - expand for component math</summary>

Component fields: `raw` is the observed value, `pct` is screened-universe percentile, `z` is standard deviations from average, `weight` is formula influence, and `score` is the component score after direction adjustment.

**Trend**
- Meaning: Price structure: longer-window return, short-vs-medium moving average alignment, close vs SMA20, and recent up-day consistency.
- Formula: `0.35 * pct_rank(sma_5_20_ratio) + 0.25 * pct_rank(close_vs_sma_20) + 0.15 * pct_rank(up_day_ratio_10d) + 0.15 * pct_rank(close_location_20d) + 0.10 * pct_rank(market_regime_score)`
  - sma_5_20_ratio: raw 6.74%; pct 0.94; z 1.59; weight 0.35; score 0.94.
  - close_vs_sma_20: raw 9.35%; pct 0.93; z 1.42; weight 0.25; score 0.93.
  - up_day_ratio_10d: raw 60.00%; pct 0.69; z 0.50; weight 0.15; score 0.69.
  - close_location_20d: raw 93.33%; pct 0.92; z 1.42; weight 0.15; score 0.92.
  - market_regime_score: raw 0.91; pct 0.50; z n/a; weight 0.10; score 0.50.

**Momentum**
- Meaning: Recent price movement across 1D, 5D, 10D, and 20D windows.
- Formula: `0.35 * pct_rank(momentum_acceleration_5d_10d) + 0.15 * pct_rank(return_1d) + 0.20 * pct_rank(close_location_5d) + 0.15 * pct_rank(rs_momentum_5d_20d) + 0.15 * pct_rank(price_volume_efficiency_5d)`
  - momentum_acceleration_5d_10d: raw 6.78%; pct 0.96; z 2.05; weight 0.35; score 0.96.
  - return_1d: raw -0.23%; pct 0.51; z -0.10; weight 0.15; score 0.51.
  - close_location_5d: raw 90.18%; pct 0.89; z 1.41; weight 0.20; score 0.89.
  - rs_momentum_5d_20d: raw 0.08; pct 0.95; z 1.73; weight 0.15; score 0.95.
  - price_volume_efficiency_5d: raw 6.45%; pct 0.91; z 1.16; weight 0.15; score 0.91.

**Relative Strength**
- Meaning: Outperformance or underperformance versus SPY and QQQ across multiple windows.
- Formula: `0.25 * pct_rank(rs_momentum_5d_20d) + 0.20 * pct_rank(rel_strength_spy_10d) + 0.15 * pct_rank(rel_strength_qqq_10d) + 0.15 * pct_rank(sector_relative_strength_5d) + 0.15 * pct_rank(sector_relative_strength_10d) + 0.10 * pct_rank(sector_relative_strength_20d)`
  - rs_momentum_5d_20d: raw 0.08; pct 0.95; z 1.73; weight 0.25; score 0.95.
  - rel_strength_spy_10d: raw 9.74%; pct 0.90; z 1.14; weight 0.20; score 0.90.
  - rel_strength_qqq_10d: raw 8.28%; pct 0.90; z 1.14; weight 0.15; score 0.90.
  - sector_relative_strength_5d: raw 11.67%; pct 0.97; z 1.93; weight 0.15; score 0.97.
  - sector_relative_strength_10d: raw 9.66%; pct 0.90; z 1.14; weight 0.15; score 0.90.
  - sector_relative_strength_20d: raw 14.10%; pct 0.93; z 1.21; weight 0.10; score 0.93.

**Participation**
- Meaning: Volume and liquidity support: relative volume, persistence of elevated volume, volume z-score, and dollar volume.
- Formula: `0.14 * pct_rank(volume_acceleration_5d_20d) + 0.14 * pct_rank(volume_ratio_5d) + 0.10 * pct_rank(volume_trend_5d_20d) + 0.14 * pct_rank(volume_persistence_5d) + 0.14 * pct_rank(volume_persistence_10d) + 0.10 * pct_rank(volume_z_score_20d) + 0.10 * pct_rank(up_volume_ratio_10d) + 0.10 * pct_rank(price_volume_efficiency_5d) + 0.05 * pct_rank(dollar_volume)`
  - volume_acceleration_5d_20d: raw 0.80x; pct 0.51; z -0.08; weight 0.14; score 0.51.
  - volume_ratio_5d: raw 1.89x; pct 0.63; z 0.08; weight 0.14; score 0.63.
  - volume_trend_5d_20d: raw 1.10x; pct 0.82; z 0.66; weight 0.10; score 0.82.
  - volume_persistence_5d: raw 100.00%; pct 0.98; z 2.30; weight 0.14; score 0.98.
  - volume_persistence_10d: raw 70.00%; pct 0.93; z 1.62; weight 0.14; score 0.93.
  - volume_z_score_20d: raw 6.47; pct 0.94; z 1.28; weight 0.10; score 0.94.
  - up_volume_ratio_10d: raw 1.27x; pct 0.58; z -0.17; weight 0.10; score 0.58.
  - price_volume_efficiency_5d: raw 6.45%; pct 0.91; z 1.16; weight 0.10; score 0.91.
  - dollar_volume: raw $551,335,882; pct 0.62; z 0.07; weight 0.05; score 0.62.

**Extension**
- Meaning: Stretch/risk control: RSI, ATR, gap size, move-vs-ATR, and position above the 20D low. Higher is less stretched.
- Formula: `0.24 * pct_rank(rsi_control) + 0.24 * (1 - pct_rank(atr_14_pct)) + 0.19 * (1 - pct_rank(stretch_vs_atr)) + 0.14 * (1 - pct_rank(distance_from_20d_low)) + 0.10 * (1 - pct_rank(abs_gap_1d)) + 0.05 * (1 - pct_rank(failed_gap_or_fade)) + 0.05 * (1 - pct_rank(distribution_pressure))`
  - rsi_control: raw 0.60; pct 0.20; z -0.63; weight 0.24; score 0.20.
  - atr_14_pct: raw 2.88%; pct 0.63; z 0.16; weight 0.24; score 0.37.
  - stretch_vs_atr: raw 4.25x; pct 0.97; z 2.30; weight 0.19; score 0.03.
  - distance_from_20d_low: raw 18.77%; pct 0.90; z 1.13; weight 0.14; score 0.10.
  - abs_gap_1d: raw 0.00; pct 0.18; z -0.55; weight 0.10; score 0.82.
  - failed_gap_or_fade: raw 0.00; pct 0.49; z -0.10; weight 0.05; score 0.51.
  - distribution_pressure: raw 0.00; pct 0.38; z -0.57; weight 0.05; score 0.62.

</details>

<details>
<summary><strong>Risk details</strong> - expand for component math</summary>

Risk fields: `score` is the bucket risk from 0 to 1, `weight` is bucket influence, and `contribution` is the weighted risk added to the final score.

**Extension Risk**
- Score 0.55; weight 0.33; contribution 0.18; severity moderate.
- Evidence: RSI 70.87, 5D return 12.2%, 10D return 10.9%, 20D low distance 18.8%
  - rsi_14: raw 70.87; risk score 0.54; range 60.00-80.00.
  - return_5d: raw 12.21%; risk score 0.68; range 0.04-0.16.
  - return_10d: raw 10.85%; risk score 0.18; range 0.08-0.24.
  - return_20d: raw 13.77%; risk score 0.19; range 0.10-0.30.
  - distance_from_20d_low: raw 18.77%; risk score 0.54; range 0.08-0.28.
  - distance_from_20d_high: raw -1.12%; risk score 0.69; range -0.08-0.02.
  - stretch_vs_atr: raw 4.25x; risk score 1.00; range 1.00-3.50.

**Volatility Risk**
- Score 0.06; weight 0.20; contribution 0.01; severity low.
- Evidence: ATR14 2.9%, gap -0.1%, 1D return -0.2%, fade/distribution False/False
  - atr_14_pct: raw 2.88%; risk score 0.18; range 0.02-0.07.
  - abs_gap_1d: raw 0.00; risk score 0.00; range 0.01-0.06.
  - abs_return_1d: raw 0.00; risk score 0.00; range 0.02-0.08.
  - failed_gap_or_fade: raw n/a; risk score n/a; range n/a-n/a.
  - distribution_pressure: raw n/a; risk score n/a; range n/a-n/a.

**Liquidity/Participation Risk**
- Score 0.08; weight 0.20; contribution 0.02; severity low.
- Evidence: tier high, dollar volume $551.3M, 5D volume 1.89x
  - liquidity_tier: raw n/a; risk score 0.00; range n/a-n/a.
  - dollar_volume: raw $551,335,882; risk score 0.00; range 5000000.00-100000000.00.
  - volume_ratio_5d: raw 1.89x; risk score 0.16; range 1.50-4.00.
  - volume_persistence_10d: raw 70.00%; risk score 0.17; range 0.20-0.80.

**Trend Failure Risk**
- Score 0.08; weight 0.15; contribution 0.01; severity low.
- Evidence: close vs SMA20 9.4%, SMA 5/20 6.7%, up-day ratio 10D 60.0%, RS decoupling False
  - close_vs_sma_20: raw 9.35%; risk score 0.00; range 0.00-0.08.
  - sma_5_20_ratio: raw 6.74%; risk score 0.00; range 0.00-0.06.
  - up_day_ratio_10d: raw 60.00%; risk score 0.25; range 0.30-0.70.
  - rs_decoupling: raw n/a; risk score n/a; range n/a-n/a.

**Event Risk**
- Score 0.00; weight 0.12; contribution 0.00; severity low.
- Evidence: earnings in -40.62 days
  - upcoming_earnings_days: raw -40.62; risk score 0.00; range n/a-n/a.

</details>

**Setup diagnostics:**
- Best diagnostic setup: breakout watch with score 0.86.
- trend confirmation: 0.85.
- momentum continuation: 0.77.
- breakout watch: 0.86.
- pullback risk: 0.27.

**Lifecycle and failure diagnostics:**
- Current phase estimate: ignition.
- Regime probabilities: continuation 0.78; mean reversion 0.38; volatility expansion 0.42.
- Phase scores: ignition 0.82; expansion 0.75; euphoria 0.64; exhaustion 0.26; reversal 0.27.
- Failure signals: poor efficiency 0.00; distribution False; fade False; RS decoupling False.
- Note: Heuristic regime probabilities; not yet calibrated to historical forward outcomes.

**Metrics:**
- **Snapshot:** US / S&P 500 / NYSE/Nasdaq; price 260.15; market cap $37.52B.
- **Scores:** rank 0.78; opportunity 0.77; risk 0.22 (low); confidence 0.78.
- **Regime:** bullish regime if conditions persist over 1d-5d; setup trend confirmation.

**Price action:**
- Returns: 1D -0.23%; 5D 12.21%; 10D 10.85%; 20D 13.77%.
- Trend quality: SMA 5/20 6.74%; close vs SMA20 9.35%; up days 5D 80.00%; up days 10D 60.00%.
- Range and volatility: 5D high -1.12%; 5D low 11.58%; 20D high -1.12%; 20D low 18.77%; close location 1D 42.69%; 5D 90.18%; 20D 93.33%; ATR14 2.88%; gap -0.10%; RSI14 70.87; fade flag False.
- Acceleration/failure: momentum acceleration 6.78%; RS momentum 8.23%; RS decoupling False; distribution pressure False.

**Benchmark relative strength:**
- Versus SPY: 1D -0.48%; 5D 10.36%; 10D 9.74%; 20D 8.51%.
- Versus QQQ: 1D -0.60%; 5D 8.88%; 10D 8.28%; 20D 3.20%.
- Versus sector peers: 5D 11.67%; 10D 9.66%; 20D 14.10%.
- Market regime: 0.91 (supportive).

**Volume and liquidity:**
- Relative volume: 5D 1.89x; 20D 2.08x; 5D/20D trend 1.10x.
- Participation evidence: volume z-score 6.47; elevated-volume persistence 5D 100.00%; 10D 70.00%; up/down volume 10D 1.27x.
- Volume quality: acceleration 0.80; price/volume efficiency 6.45%; effort/result 15.51x; distribution days 10D 3.00.
- Liquidity: tier high; dollar volume $551,335,882.

**Other context:**
- Upcoming earnings days: -40.62.

**Why it screens well:**
- Trend 0.85: SMA 5/20 6.7%, close vs SMA20 9.4%, 20D close location 93.3%, market regime supportive.
- Momentum 0.87: acceleration 6.8%, 1D -0.2%, 5D close location 90.2%, price/volume efficiency 6.4%.
- Relative strength 0.93: strongest window 5D vs SPY 10.4% (pct n/a); 5D SPY 10.4%, RS momentum 8.2%, 10D sector 9.7%.
- Participation 0.78: volume z-score 6.47, 5D persistence 100.0%, 10D persistence 70.0% (pct 0.93), volume acceleration 0.80, up/down volume 1.27x, efficiency 6.4%, liquidity tier high ($551.3M).
- Extension control 0.29: RSI 70.87, ATR14 2.9%, gap -0.1%, 20D low distance 18.8%, fade/distribution flags False/False.
- Opportunity score is 0.77; risk score is 0.22.
- Factor reason codes: TREND_CONSTRUCTIVE, MOMENTUM_POSITIVE, RELATIVE_STRENGTH_SUPPORTIVE, PARTICIPATION_EXPANDING, EXTENSION_ELEVATED, RSI_STRETCHED.

**1-day to 1-week plan:**
- Watch whether the stock continues to outperform SPY/QQQ over the next session.
- Watch whether relative volume stays supportive; fading volume weakens the setup.
- Treat loss of factor support plus fading relative volume as invalidation.

**Main risks:**
- moderate extension risk: RSI 70.87, 5D return 12.2%, 10D return 10.9%, 20D low distance 18.8%
- Risk score is 0.22 (low) on a continuous 0 to 1 scale.

**Verdict:** This is a watchlist candidate for short-term research only; the setup depends on momentum and volume staying intact. Not financial advice.

---

### PPG - PPG Industries, Inc.
**Setup:** PPG is a trend confirmation candidate based on the current 1-day to 1-week screen. The setup is a conditional market regime, not a standalone price forecast.

**Quick scorecard:**
- **Factor scores:** trend 0.82; momentum 0.80; relative strength 0.83; participation 0.65; extension control 0.44.
- **Read this as:** higher trend/momentum/relative strength/participation is better; higher extension control means less stretched.
- Trend 0.82: SMA 5/20 3.7%, close vs SMA20 5.4%, 20D close location 90.3%, market regime supportive.
- Momentum 0.80: acceleration 2.6%, 1D 0.1%, 5D close location 82.9%, price/volume efficiency 4.6%.
- Relative strength 0.83: strongest window 10D vs SPY 5.6% (pct 0.82); 5D SPY 4.1%, RS momentum 4.2%, 10D sector 5.5%.
- Participation 0.65: volume z-score 1.33, 5D persistence 80.0%, 10D persistence 70.0% (pct 0.93), volume acceleration 0.21, up/down volume 2.79x, efficiency 4.6%, liquidity tier high ($295.7M).
- Extension control 0.44: RSI 59.50, ATR14 2.8%, gap -0.2%, 20D low distance 13.0%, fade/distribution flags False/False.

<details>
<summary><strong>Formula details</strong> - expand for component math</summary>

Component fields: `raw` is the observed value, `pct` is screened-universe percentile, `z` is standard deviations from average, `weight` is formula influence, and `score` is the component score after direction adjustment.

**Trend**
- Meaning: Price structure: longer-window return, short-vs-medium moving average alignment, close vs SMA20, and recent up-day consistency.
- Formula: `0.35 * pct_rank(sma_5_20_ratio) + 0.25 * pct_rank(close_vs_sma_20) + 0.15 * pct_rank(up_day_ratio_10d) + 0.15 * pct_rank(close_location_20d) + 0.10 * pct_rank(market_regime_score)`
  - sma_5_20_ratio: raw 3.71%; pct 0.85; z 0.73; weight 0.35; score 0.85.
  - close_vs_sma_20: raw 5.36%; pct 0.84; z 0.72; weight 0.25; score 0.84.
  - up_day_ratio_10d: raw 70.00%; pct 0.87; z 1.19; weight 0.15; score 0.87.
  - close_location_20d: raw 90.26%; pct 0.90; z 1.32; weight 0.15; score 0.90.
  - market_regime_score: raw 0.91; pct 0.50; z n/a; weight 0.10; score 0.50.

**Momentum**
- Meaning: Recent price movement across 1D, 5D, 10D, and 20D windows.
- Formula: `0.35 * pct_rank(momentum_acceleration_5d_10d) + 0.15 * pct_rank(return_1d) + 0.20 * pct_rank(close_location_5d) + 0.15 * pct_rank(rs_momentum_5d_20d) + 0.15 * pct_rank(price_volume_efficiency_5d)`
  - momentum_acceleration_5d_10d: raw 2.62%; pct 0.83; z 0.81; weight 0.35; score 0.83.
  - return_1d: raw 0.11%; pct 0.60; z 0.06; weight 0.15; score 0.60.
  - close_location_5d: raw 82.95%; pct 0.81; z 1.19; weight 0.20; score 0.81.
  - rs_momentum_5d_20d: raw 0.04; pct 0.86; z 0.85; weight 0.15; score 0.86.
  - price_volume_efficiency_5d: raw 4.58%; pct 0.87; z 0.75; weight 0.15; score 0.87.

**Relative Strength**
- Meaning: Outperformance or underperformance versus SPY and QQQ across multiple windows.
- Formula: `0.25 * pct_rank(rs_momentum_5d_20d) + 0.20 * pct_rank(rel_strength_spy_10d) + 0.15 * pct_rank(rel_strength_qqq_10d) + 0.15 * pct_rank(sector_relative_strength_5d) + 0.15 * pct_rank(sector_relative_strength_10d) + 0.10 * pct_rank(sector_relative_strength_20d)`
  - rs_momentum_5d_20d: raw 0.04; pct 0.86; z 0.85; weight 0.25; score 0.86.
  - rel_strength_spy_10d: raw 5.55%; pct 0.82; z 0.57; weight 0.20; score 0.82.
  - rel_strength_qqq_10d: raw 4.09%; pct 0.82; z 0.57; weight 0.15; score 0.82.
  - sector_relative_strength_5d: raw 5.41%; pct 0.86; z 0.84; weight 0.15; score 0.86.
  - sector_relative_strength_10d: raw 5.47%; pct 0.82; z 0.57; weight 0.15; score 0.82.
  - sector_relative_strength_20d: raw 5.14%; pct 0.77; z 0.37; weight 0.10; score 0.77.

**Participation**
- Meaning: Volume and liquidity support: relative volume, persistence of elevated volume, volume z-score, and dollar volume.
- Formula: `0.14 * pct_rank(volume_acceleration_5d_20d) + 0.14 * pct_rank(volume_ratio_5d) + 0.10 * pct_rank(volume_trend_5d_20d) + 0.14 * pct_rank(volume_persistence_5d) + 0.14 * pct_rank(volume_persistence_10d) + 0.10 * pct_rank(volume_z_score_20d) + 0.10 * pct_rank(up_volume_ratio_10d) + 0.10 * pct_rank(price_volume_efficiency_5d) + 0.05 * pct_rank(dollar_volume)`
  - volume_acceleration_5d_20d: raw 0.21x; pct 0.22; z -0.60; weight 0.14; score 0.22.
  - volume_ratio_5d: raw 1.30x; pct 0.30; z -0.48; weight 0.14; score 0.30.
  - volume_trend_5d_20d: raw 1.09x; pct 0.82; z 0.63; weight 0.10; score 0.82.
  - volume_persistence_5d: raw 80.00%; pct 0.91; z 1.54; weight 0.14; score 0.91.
  - volume_persistence_10d: raw 70.00%; pct 0.93; z 1.62; weight 0.14; score 0.93.
  - volume_z_score_20d: raw 1.33; pct 0.48; z -0.27; weight 0.10; score 0.48.
  - up_volume_ratio_10d: raw 2.79x; pct 0.90; z 0.71; weight 0.10; score 0.90.
  - price_volume_efficiency_5d: raw 4.58%; pct 0.87; z 0.75; weight 0.10; score 0.87.
  - dollar_volume: raw $295,657,371; pct 0.39; z -0.42; weight 0.05; score 0.39.

**Extension**
- Meaning: Stretch/risk control: RSI, ATR, gap size, move-vs-ATR, and position above the 20D low. Higher is less stretched.
- Formula: `0.24 * pct_rank(rsi_control) + 0.24 * (1 - pct_rank(atr_14_pct)) + 0.19 * (1 - pct_rank(stretch_vs_atr)) + 0.14 * (1 - pct_rank(distance_from_20d_low)) + 0.10 * (1 - pct_rank(abs_gap_1d)) + 0.05 * (1 - pct_rank(failed_gap_or_fade)) + 0.05 * (1 - pct_rank(distribution_pressure))`
  - rsi_control: raw 1.00; pct 0.73; z 0.79; weight 0.24; score 0.73.
  - atr_14_pct: raw 2.82%; pct 0.60; z 0.10; weight 0.24; score 0.40.
  - stretch_vs_atr: raw 2.11x; pct 0.88; z 1.08; weight 0.19; score 0.12.
  - distance_from_20d_low: raw 12.98%; pct 0.82; z 0.51; weight 0.14; score 0.18.
  - abs_gap_1d: raw 0.00; pct 0.33; z -0.41; weight 0.10; score 0.67.
  - failed_gap_or_fade: raw 0.00; pct 0.49; z -0.10; weight 0.05; score 0.51.
  - distribution_pressure: raw 0.00; pct 0.38; z -0.57; weight 0.05; score 0.62.

</details>

<details>
<summary><strong>Risk details</strong> - expand for component math</summary>

Risk fields: `score` is the bucket risk from 0 to 1, `weight` is bucket influence, and `contribution` is the weighted risk added to the final score.

**Extension Risk**
- Score 0.22; weight 0.33; contribution 0.07; severity low.
- Evidence: RSI 59.50, 5D return 6.0%, 10D return 6.7%, 20D low distance 13.0%
  - rsi_14: raw 59.50; risk score 0.00; range 60.00-80.00.
  - return_5d: raw 5.96%; risk score 0.16; range 0.04-0.16.
  - return_10d: raw 6.67%; risk score 0.00; range 0.08-0.24.
  - return_20d: raw 4.81%; risk score 0.00; range 0.10-0.30.
  - distance_from_20d_low: raw 12.98%; risk score 0.25; range 0.08-0.28.
  - distance_from_20d_high: raw -1.22%; risk score 0.68; range -0.08-0.02.
  - stretch_vs_atr: raw 2.11x; risk score 0.45; range 1.00-3.50.

**Volatility Risk**
- Score 0.05; weight 0.20; contribution 0.01; severity low.
- Evidence: ATR14 2.8%, gap -0.2%, 1D return 0.1%, fade/distribution False/False
  - atr_14_pct: raw 2.82%; risk score 0.16; range 0.02-0.07.
  - abs_gap_1d: raw 0.00; risk score 0.00; range 0.01-0.06.
  - abs_return_1d: raw 0.00; risk score 0.00; range 0.02-0.08.
  - failed_gap_or_fade: raw n/a; risk score n/a; range n/a-n/a.
  - distribution_pressure: raw n/a; risk score n/a; range n/a-n/a.

**Liquidity/Participation Risk**
- Score 0.04; weight 0.20; contribution 0.01; severity low.
- Evidence: tier high, dollar volume $295.7M, 5D volume 1.30x
  - liquidity_tier: raw n/a; risk score 0.00; range n/a-n/a.
  - dollar_volume: raw $295,657,371; risk score 0.00; range 5000000.00-100000000.00.
  - volume_ratio_5d: raw 1.30x; risk score 0.00; range 1.50-4.00.
  - volume_persistence_10d: raw 70.00%; risk score 0.17; range 0.20-0.80.

**Trend Failure Risk**
- Score 0.00; weight 0.15; contribution 0.00; severity low.
- Evidence: close vs SMA20 5.4%, SMA 5/20 3.7%, up-day ratio 10D 70.0%, RS decoupling False
  - close_vs_sma_20: raw 5.36%; risk score 0.00; range 0.00-0.08.
  - sma_5_20_ratio: raw 3.71%; risk score 0.00; range 0.00-0.06.
  - up_day_ratio_10d: raw 70.00%; risk score 0.00; range 0.30-0.70.
  - rs_decoupling: raw n/a; risk score n/a; range n/a-n/a.

**Event Risk**
- Score 0.00; weight 0.12; contribution 0.00; severity low.
- Evidence: earnings in -32.62 days
  - upcoming_earnings_days: raw -32.62; risk score 0.00; range n/a-n/a.

</details>

**Setup diagnostics:**
- Best diagnostic setup: trend confirmation with score 0.80.
- trend confirmation: 0.80.
- momentum continuation: 0.75.
- breakout watch: 0.79.
- pullback risk: 0.24.

**Lifecycle and failure diagnostics:**
- Current phase estimate: expansion.
- Regime probabilities: continuation 0.70; mean reversion 0.27; volatility expansion 0.29.
- Phase scores: ignition 0.61; expansion 0.73; euphoria 0.49; exhaustion 0.18; reversal 0.17.
- Failure signals: poor efficiency 0.00; distribution False; fade False; RS decoupling False.
- Note: Heuristic regime probabilities; not yet calibrated to historical forward outcomes.

**Metrics:**
- **Snapshot:** US / S&P 500 / NYSE/Nasdaq; price 112.98; market cap $25.18B.
- **Scores:** rank 0.77; opportunity 0.73; risk 0.10 (low); confidence 0.80.
- **Regime:** bullish regime if conditions persist over 1d-5d; setup trend confirmation.

**Price action:**
- Returns: 1D 0.11%; 5D 5.96%; 10D 6.67%; 20D 4.81%.
- Trend quality: SMA 5/20 3.71%; close vs SMA20 5.36%; up days 5D 80.00%; up days 10D 70.00%.
- Range and volatility: 5D high -1.22%; 5D low 6.41%; 20D high -1.22%; 20D low 12.98%; close location 1D 51.35%; 5D 82.95%; 20D 90.26%; ATR14 2.82%; gap -0.19%; RSI14 59.50; fade flag False.
- Acceleration/failure: momentum acceleration 2.62%; RS momentum 4.22%; RS decoupling False; distribution pressure False.

**Benchmark relative strength:**
- Versus SPY: 1D -0.14%; 5D 4.10%; 10D 5.55%; 20D -0.45%.
- Versus QQQ: 1D -0.26%; 5D 2.62%; 10D 4.09%; 20D -5.76%.
- Versus sector peers: 5D 5.41%; 10D 5.47%; 20D 5.14%.
- Market regime: 0.91 (supportive).

**Volume and liquidity:**
- Relative volume: 5D 1.30x; 20D 1.42x; 5D/20D trend 1.09x.
- Participation evidence: volume z-score 1.33; elevated-volume persistence 5D 80.00%; 10D 70.00%; up/down volume 10D 2.79x.
- Volume quality: acceleration 0.21; price/volume efficiency 4.58%; effort/result 21.84x; distribution days 10D 2.00.
- Liquidity: tier high; dollar volume $295,657,371.

**Other context:**
- Upcoming earnings days: -32.62.

**Why it screens well:**
- Trend 0.82: SMA 5/20 3.7%, close vs SMA20 5.4%, 20D close location 90.3%, market regime supportive.
- Momentum 0.80: acceleration 2.6%, 1D 0.1%, 5D close location 82.9%, price/volume efficiency 4.6%.
- Relative strength 0.83: strongest window 10D vs SPY 5.6% (pct 0.82); 5D SPY 4.1%, RS momentum 4.2%, 10D sector 5.5%.
- Participation 0.65: volume z-score 1.33, 5D persistence 80.0%, 10D persistence 70.0% (pct 0.93), volume acceleration 0.21, up/down volume 2.79x, efficiency 4.6%, liquidity tier high ($295.7M).
- Extension control 0.44: RSI 59.50, ATR14 2.8%, gap -0.2%, 20D low distance 13.0%, fade/distribution flags False/False.
- Opportunity score is 0.73; risk score is 0.10.
- Factor reason codes: TREND_CONSTRUCTIVE, MOMENTUM_POSITIVE, RELATIVE_STRENGTH_SUPPORTIVE, PARTICIPATION_EXPANDING, EXTENSION_ELEVATED, RSI_CONSTRUCTIVE.

**1-day to 1-week plan:**
- Watch whether the stock continues to outperform SPY/QQQ over the next session.
- Watch whether relative volume stays supportive; fading volume weakens the setup.
- Treat loss of factor support plus fading relative volume as invalidation.

**Main risks:**
- controlled volatility: ATR/gap/1D move are not elevated
- no near-term earnings flag
- liquidity adequate: tier high, dollar volume $295.7M
- Risk score is 0.10 (low) on a continuous 0 to 1 scale.

**Verdict:** This is a watchlist candidate for short-term research only; the setup depends on momentum and volume staying intact. Not financial advice.

---

### GM - General Motors Company
**Setup:** GM is a trend confirmation candidate based on the current 1-day to 1-week screen. The setup is a conditional market regime, not a standalone price forecast.

**Quick scorecard:**
- **Factor scores:** trend 0.83; momentum 0.76; relative strength 0.86; participation 0.77; extension control 0.33.
- **Read this as:** higher trend/momentum/relative strength/participation is better; higher extension control means less stretched.
- Trend 0.83: SMA 5/20 5.7%, close vs SMA20 7.2%, 20D close location 86.8%, market regime supportive.
- Momentum 0.76: acceleration 4.3%, 1D -1.3%, 5D close location 74.0%, price/volume efficiency 3.6%.
- Relative strength 0.86: strongest window 5D vs SPY 6.0% (pct n/a); 5D SPY 6.0%, RS momentum 5.2%, 10D sector 5.9%.
- Participation 0.77: volume z-score 4.60, 5D persistence 60.0%, 10D persistence 60.0% (pct 0.84), volume acceleration 1.14, up/down volume 1.20x, efficiency 3.6%, liquidity tier high ($1.3B).
- Extension control 0.33: RSI 58.82, ATR14 3.4%, gap 0.5%, 20D low distance 18.2%, fade/distribution flags False/False.

<details>
<summary><strong>Formula details</strong> - expand for component math</summary>

Component fields: `raw` is the observed value, `pct` is screened-universe percentile, `z` is standard deviations from average, `weight` is formula influence, and `score` is the component score after direction adjustment.

**Trend**
- Meaning: Price structure: longer-window return, short-vs-medium moving average alignment, close vs SMA20, and recent up-day consistency.
- Formula: `0.35 * pct_rank(sma_5_20_ratio) + 0.25 * pct_rank(close_vs_sma_20) + 0.15 * pct_rank(up_day_ratio_10d) + 0.15 * pct_rank(close_location_20d) + 0.10 * pct_rank(market_regime_score)`
  - sma_5_20_ratio: raw 5.67%; pct 0.92; z 1.29; weight 0.35; score 0.92.
  - close_vs_sma_20: raw 7.20%; pct 0.90; z 1.04; weight 0.25; score 0.90.
  - up_day_ratio_10d: raw 60.00%; pct 0.69; z 0.50; weight 0.15; score 0.69.
  - close_location_20d: raw 86.79%; pct 0.86; z 1.20; weight 0.15; score 0.86.
  - market_regime_score: raw 0.91; pct 0.50; z n/a; weight 0.10; score 0.50.

**Momentum**
- Meaning: Recent price movement across 1D, 5D, 10D, and 20D windows.
- Formula: `0.35 * pct_rank(momentum_acceleration_5d_10d) + 0.15 * pct_rank(return_1d) + 0.20 * pct_rank(close_location_5d) + 0.15 * pct_rank(rs_momentum_5d_20d) + 0.15 * pct_rank(price_volume_efficiency_5d)`
  - momentum_acceleration_5d_10d: raw 4.28%; pct 0.91; z 1.30; weight 0.35; score 0.91.
  - return_1d: raw -1.32%; pct 0.23; z -0.61; weight 0.15; score 0.23.
  - close_location_5d: raw 74.00%; pct 0.74; z 0.91; weight 0.20; score 0.74.
  - rs_momentum_5d_20d: raw 0.05; pct 0.90; z 1.07; weight 0.15; score 0.90.
  - price_volume_efficiency_5d: raw 3.60%; pct 0.82; z 0.54; weight 0.15; score 0.82.

**Relative Strength**
- Meaning: Outperformance or underperformance versus SPY and QQQ across multiple windows.
- Formula: `0.25 * pct_rank(rs_momentum_5d_20d) + 0.20 * pct_rank(rel_strength_spy_10d) + 0.15 * pct_rank(rel_strength_qqq_10d) + 0.15 * pct_rank(sector_relative_strength_5d) + 0.15 * pct_rank(sector_relative_strength_10d) + 0.10 * pct_rank(sector_relative_strength_20d)`
  - rs_momentum_5d_20d: raw 0.05; pct 0.90; z 1.07; weight 0.25; score 0.90.
  - rel_strength_spy_10d: raw 5.95%; pct 0.84; z 0.63; weight 0.20; score 0.84.
  - rel_strength_qqq_10d: raw 4.49%; pct 0.84; z 0.63; weight 0.15; score 0.84.
  - sector_relative_strength_5d: raw 7.27%; pct 0.90; z 1.16; weight 0.15; score 0.90.
  - sector_relative_strength_10d: raw 5.87%; pct 0.84; z 0.63; weight 0.15; score 0.84.
  - sector_relative_strength_20d: raw 8.59%; pct 0.84; z 0.69; weight 0.10; score 0.84.

**Participation**
- Meaning: Volume and liquidity support: relative volume, persistence of elevated volume, volume z-score, and dollar volume.
- Formula: `0.14 * pct_rank(volume_acceleration_5d_20d) + 0.14 * pct_rank(volume_ratio_5d) + 0.10 * pct_rank(volume_trend_5d_20d) + 0.14 * pct_rank(volume_persistence_5d) + 0.14 * pct_rank(volume_persistence_10d) + 0.10 * pct_rank(volume_z_score_20d) + 0.10 * pct_rank(up_volume_ratio_10d) + 0.10 * pct_rank(price_volume_efficiency_5d) + 0.05 * pct_rank(dollar_volume)`
  - volume_acceleration_5d_20d: raw 1.14x; pct 0.70; z 0.23; weight 0.14; score 0.70.
  - volume_ratio_5d: raw 2.17x; pct 0.75; z 0.34; weight 0.14; score 0.75.
  - volume_trend_5d_20d: raw 1.03x; pct 0.76; z 0.41; weight 0.10; score 0.76.
  - volume_persistence_5d: raw 60.00%; pct 0.76; z 0.78; weight 0.14; score 0.76.
  - volume_persistence_10d: raw 60.00%; pct 0.84; z 1.09; weight 0.14; score 0.84.
  - volume_z_score_20d: raw 4.60; pct 0.84; z 0.72; weight 0.10; score 0.84.
  - up_volume_ratio_10d: raw 1.20x; pct 0.56; z -0.21; weight 0.10; score 0.56.
  - price_volume_efficiency_5d: raw 3.60%; pct 0.82; z 0.54; weight 0.10; score 0.82.
  - dollar_volume: raw $1.29B; pct 0.94; z 1.52; weight 0.05; score 0.94.

**Extension**
- Meaning: Stretch/risk control: RSI, ATR, gap size, move-vs-ATR, and position above the 20D low. Higher is less stretched.
- Formula: `0.24 * pct_rank(rsi_control) + 0.24 * (1 - pct_rank(atr_14_pct)) + 0.19 * (1 - pct_rank(stretch_vs_atr)) + 0.14 * (1 - pct_rank(distance_from_20d_low)) + 0.10 * (1 - pct_rank(abs_gap_1d)) + 0.05 * (1 - pct_rank(failed_gap_or_fade)) + 0.05 * (1 - pct_rank(distribution_pressure))`
  - rsi_control: raw 1.00; pct 0.73; z 0.79; weight 0.24; score 0.73.
  - atr_14_pct: raw 3.38%; pct 0.81; z 0.70; weight 0.24; score 0.19.
  - stretch_vs_atr: raw 2.31x; pct 0.90; z 1.19; weight 0.19; score 0.10.
  - distance_from_20d_low: raw 18.19%; pct 0.89; z 1.07; weight 0.14; score 0.11.
  - abs_gap_1d: raw 0.01; pct 0.74; z 0.10; weight 0.10; score 0.26.
  - failed_gap_or_fade: raw 0.00; pct 0.49; z -0.10; weight 0.05; score 0.51.
  - distribution_pressure: raw 0.00; pct 0.38; z -0.57; weight 0.05; score 0.62.

</details>

<details>
<summary><strong>Risk details</strong> - expand for component math</summary>

Risk fields: `score` is the bucket risk from 0 to 1, `weight` is bucket influence, and `contribution` is the weighted risk added to the final score.

**Extension Risk**
- Score 0.27; weight 0.33; contribution 0.09; severity low.
- Evidence: RSI 58.82, 5D return 7.8%, 10D return 7.1%, 20D low distance 18.2%
  - rsi_14: raw 58.82; risk score 0.00; range 60.00-80.00.
  - return_5d: raw 7.81%; risk score 0.32; range 0.04-0.16.
  - return_10d: raw 7.06%; risk score 0.00; range 0.08-0.24.
  - return_20d: raw 8.26%; risk score 0.00; range 0.10-0.30.
  - distance_from_20d_low: raw 18.19%; risk score 0.51; range 0.08-0.28.
  - distance_from_20d_high: raw -2.29%; risk score 0.57; range -0.08-0.02.
  - stretch_vs_atr: raw 2.31x; risk score 0.52; range 1.00-3.50.

**Volatility Risk**
- Score 0.09; weight 0.20; contribution 0.02; severity low.
- Evidence: ATR14 3.4%, gap 0.5%, 1D return -1.3%, fade/distribution False/False
  - atr_14_pct: raw 3.38%; risk score 0.28; range 0.02-0.07.
  - abs_gap_1d: raw 0.01; risk score 0.00; range 0.01-0.06.
  - abs_return_1d: raw 0.01; risk score 0.00; range 0.02-0.08.
  - failed_gap_or_fade: raw n/a; risk score n/a; range n/a-n/a.
  - distribution_pressure: raw n/a; risk score n/a; range n/a-n/a.

**Liquidity/Participation Risk**
- Score 0.15; weight 0.20; contribution 0.03; severity low.
- Evidence: tier high, dollar volume $1.3B, 5D volume 2.17x
  - liquidity_tier: raw n/a; risk score 0.00; range n/a-n/a.
  - dollar_volume: raw $1.29B; risk score 0.00; range 5000000.00-100000000.00.
  - volume_ratio_5d: raw 2.17x; risk score 0.27; range 1.50-4.00.
  - volume_persistence_10d: raw 60.00%; risk score 0.33; range 0.20-0.80.

**Trend Failure Risk**
- Score 0.08; weight 0.15; contribution 0.01; severity low.
- Evidence: close vs SMA20 7.2%, SMA 5/20 5.7%, up-day ratio 10D 60.0%, RS decoupling False
  - close_vs_sma_20: raw 7.20%; risk score 0.00; range 0.00-0.08.
  - sma_5_20_ratio: raw 5.67%; risk score 0.00; range 0.00-0.06.
  - up_day_ratio_10d: raw 60.00%; risk score 0.25; range 0.30-0.70.
  - rs_decoupling: raw n/a; risk score n/a; range n/a-n/a.

**Event Risk**
- Score 0.00; weight 0.12; contribution 0.00; severity low.
- Evidence: earnings in 51.06 days
  - upcoming_earnings_days: raw 51.06; risk score 0.00; range n/a-n/a.

</details>

**Setup diagnostics:**
- Best diagnostic setup: breakout watch with score 0.81.
- trend confirmation: 0.81.
- momentum continuation: 0.73.
- breakout watch: 0.81.
- pullback risk: 0.28.

**Lifecycle and failure diagnostics:**
- Current phase estimate: ignition.
- Regime probabilities: continuation 0.78; mean reversion 0.37; volatility expansion 0.45.
- Phase scores: ignition 0.84; expansion 0.73; euphoria 0.62; exhaustion 0.27; reversal 0.25.
- Failure signals: poor efficiency 0.07; distribution False; fade False; RS decoupling False.
- Note: Heuristic regime probabilities; not yet calibrated to historical forward outcomes.

**Metrics:**
- **Snapshot:** US / S&P 500 / NYSE/Nasdaq; price 83.24; market cap $75.05B.
- **Scores:** rank 0.77; opportunity 0.74; risk 0.15 (low); confidence 0.78.
- **Regime:** bullish regime if conditions persist over 1d-5d; setup trend confirmation.

**Price action:**
- Returns: 1D -1.32%; 5D 7.81%; 10D 7.06%; 20D 8.26%.
- Trend quality: SMA 5/20 5.67%; close vs SMA20 7.20%; up days 5D 80.00%; up days 10D 60.00%.
- Range and volatility: 5D high -2.29%; 5D low 7.14%; 20D high -2.29%; 20D low 18.19%; close location 1D 53.30%; 5D 74.00%; 20D 86.79%; ATR14 3.38%; gap 0.53%; RSI14 58.82; fade flag False.
- Acceleration/failure: momentum acceleration 4.28%; RS momentum 5.21%; RS decoupling False; distribution pressure False.

**Benchmark relative strength:**
- Versus SPY: 1D -1.57%; 5D 5.96%; 10D 5.95%; 20D 3.00%.
- Versus QQQ: 1D -1.68%; 5D 4.48%; 10D 4.49%; 20D -2.31%.
- Versus sector peers: 5D 7.27%; 10D 5.87%; 20D 8.59%.
- Market regime: 0.91 (supportive).

**Volume and liquidity:**
- Relative volume: 5D 2.17x; 20D 2.24x; 5D/20D trend 1.03x.
- Participation evidence: volume z-score 4.60; elevated-volume persistence 5D 60.00%; 10D 60.00%; up/down volume 10D 1.20x.
- Volume quality: acceleration 1.14; price/volume efficiency 3.60%; effort/result 27.77x; distribution days 10D 3.00.
- Liquidity: tier high; dollar volume $1.29B.

**Other context:**
- Upcoming earnings days: 51.06.

**Why it screens well:**
- Trend 0.83: SMA 5/20 5.7%, close vs SMA20 7.2%, 20D close location 86.8%, market regime supportive.
- Momentum 0.76: acceleration 4.3%, 1D -1.3%, 5D close location 74.0%, price/volume efficiency 3.6%.
- Relative strength 0.86: strongest window 5D vs SPY 6.0% (pct n/a); 5D SPY 6.0%, RS momentum 5.2%, 10D sector 5.9%.
- Participation 0.77: volume z-score 4.60, 5D persistence 60.0%, 10D persistence 60.0% (pct 0.84), volume acceleration 1.14, up/down volume 1.20x, efficiency 3.6%, liquidity tier high ($1.3B).
- Extension control 0.33: RSI 58.82, ATR14 3.4%, gap 0.5%, 20D low distance 18.2%, fade/distribution flags False/False.
- Opportunity score is 0.74; risk score is 0.15.
- Factor reason codes: TREND_CONSTRUCTIVE, MOMENTUM_POSITIVE, RELATIVE_STRENGTH_SUPPORTIVE, PARTICIPATION_EXPANDING, EXTENSION_ELEVATED, RSI_CONSTRUCTIVE.

**1-day to 1-week plan:**
- Watch whether the stock continues to outperform SPY/QQQ over the next session.
- Watch whether relative volume stays supportive; fading volume weakens the setup.
- Treat loss of factor support plus fading relative volume as invalidation.

**Main risks:**
- controlled volatility: ATR/gap/1D move are not elevated
- no near-term earnings flag
- liquidity adequate: tier high, dollar volume $1.3B
- Risk score is 0.15 (low) on a continuous 0 to 1 scale.

**Verdict:** This is a watchlist candidate for short-term research only; the setup depends on momentum and volume staying intact. Not financial advice.

---

### CTSH - Cognizant Technology Solutions Corporation
**Setup:** CTSH is a trend confirmation candidate based on the current 1-day to 1-week screen. The setup is a conditional market regime, not a standalone price forecast.

**Quick scorecard:**
- **Factor scores:** trend 0.89; momentum 0.61; relative strength 0.92; participation 0.76; extension control 0.34.
- **Read this as:** higher trend/momentum/relative strength/participation is better; higher extension control means less stretched.
- Trend 0.89: SMA 5/20 5.2%, close vs SMA20 9.7%, 20D close location 96.5%, market regime supportive.
- Momentum 0.61: acceleration -4.4%, 1D 3.5%, 5D close location 92.5%, price/volume efficiency 4.2%.
- Relative strength 0.92: strongest window 10D vs SPY 20.8% (pct 0.97); 5D SPY 4.7%, RS momentum 4.5%, 10D sector 20.7%.
- Participation 0.76: volume z-score 2.92, 5D persistence 100.0%, 10D persistence 90.0% (pct 1.00), volume acceleration 0.47, up/down volume 4.03x, efficiency 4.2%, liquidity tier high ($822.3M).
- Extension control 0.34: RSI 61.88, ATR14 3.9%, gap 0.3%, 20D low distance 23.5%, fade/distribution flags False/False.

<details>
<summary><strong>Formula details</strong> - expand for component math</summary>

Component fields: `raw` is the observed value, `pct` is screened-universe percentile, `z` is standard deviations from average, `weight` is formula influence, and `score` is the component score after direction adjustment.

**Trend**
- Meaning: Price structure: longer-window return, short-vs-medium moving average alignment, close vs SMA20, and recent up-day consistency.
- Formula: `0.35 * pct_rank(sma_5_20_ratio) + 0.25 * pct_rank(close_vs_sma_20) + 0.15 * pct_rank(up_day_ratio_10d) + 0.15 * pct_rank(close_location_20d) + 0.10 * pct_rank(market_regime_score)`
  - sma_5_20_ratio: raw 5.18%; pct 0.90; z 1.15; weight 0.35; score 0.90.
  - close_vs_sma_20: raw 9.69%; pct 0.94; z 1.48; weight 0.25; score 0.94.
  - up_day_ratio_10d: raw 80.00%; pct 0.96; z 1.89; weight 0.15; score 0.96.
  - close_location_20d: raw 96.54%; pct 0.95; z 1.53; weight 0.15; score 0.95.
  - market_regime_score: raw 0.91; pct 0.50; z n/a; weight 0.10; score 0.50.

**Momentum**
- Meaning: Recent price movement across 1D, 5D, 10D, and 20D windows.
- Formula: `0.35 * pct_rank(momentum_acceleration_5d_10d) + 0.15 * pct_rank(return_1d) + 0.20 * pct_rank(close_location_5d) + 0.15 * pct_rank(rs_momentum_5d_20d) + 0.15 * pct_rank(price_volume_efficiency_5d)`
  - momentum_acceleration_5d_10d: raw -4.39%; pct 0.06; z -1.27; weight 0.35; score 0.06.
  - return_1d: raw 3.55%; pct 0.95; z 1.67; weight 0.15; score 0.95.
  - close_location_5d: raw 92.46%; pct 0.91; z 1.48; weight 0.20; score 0.91.
  - rs_momentum_5d_20d: raw 0.05; pct 0.88; z 0.91; weight 0.15; score 0.88.
  - price_volume_efficiency_5d: raw 4.18%; pct 0.84; z 0.66; weight 0.15; score 0.84.

**Relative Strength**
- Meaning: Outperformance or underperformance versus SPY and QQQ across multiple windows.
- Formula: `0.25 * pct_rank(rs_momentum_5d_20d) + 0.20 * pct_rank(rel_strength_spy_10d) + 0.15 * pct_rank(rel_strength_qqq_10d) + 0.15 * pct_rank(sector_relative_strength_5d) + 0.15 * pct_rank(sector_relative_strength_10d) + 0.10 * pct_rank(sector_relative_strength_20d)`
  - rs_momentum_5d_20d: raw 0.05; pct 0.88; z 0.91; weight 0.25; score 0.88.
  - rel_strength_spy_10d: raw 20.83%; pct 0.97; z 2.65; weight 0.20; score 0.97.
  - rel_strength_qqq_10d: raw 19.37%; pct 0.97; z 2.65; weight 0.15; score 0.97.
  - sector_relative_strength_5d: raw 6.03%; pct 0.87; z 0.95; weight 0.15; score 0.87.
  - sector_relative_strength_10d: raw 20.75%; pct 0.97; z 2.65; weight 0.15; score 0.97.
  - sector_relative_strength_20d: raw 6.48%; pct 0.80; z 0.49; weight 0.10; score 0.80.

**Participation**
- Meaning: Volume and liquidity support: relative volume, persistence of elevated volume, volume z-score, and dollar volume.
- Formula: `0.14 * pct_rank(volume_acceleration_5d_20d) + 0.14 * pct_rank(volume_ratio_5d) + 0.10 * pct_rank(volume_trend_5d_20d) + 0.14 * pct_rank(volume_persistence_5d) + 0.14 * pct_rank(volume_persistence_10d) + 0.10 * pct_rank(volume_z_score_20d) + 0.10 * pct_rank(up_volume_ratio_10d) + 0.10 * pct_rank(price_volume_efficiency_5d) + 0.05 * pct_rank(dollar_volume)`
  - volume_acceleration_5d_20d: raw 0.47x; pct 0.36; z -0.37; weight 0.14; score 0.36.
  - volume_ratio_5d: raw 1.57x; pct 0.46; z -0.23; weight 0.14; score 0.46.
  - volume_trend_5d_20d: raw 1.10x; pct 0.83; z 0.68; weight 0.10; score 0.83.
  - volume_persistence_5d: raw 100.00%; pct 0.98; z 2.30; weight 0.14; score 0.98.
  - volume_persistence_10d: raw 90.00%; pct 1.00; z 2.67; weight 0.14; score 1.00.
  - volume_z_score_20d: raw 2.92; pct 0.71; z 0.21; weight 0.10; score 0.71.
  - up_volume_ratio_10d: raw 4.03x; pct 0.94; z 1.43; weight 0.10; score 0.94.
  - price_volume_efficiency_5d: raw 4.18%; pct 0.84; z 0.66; weight 0.10; score 0.84.
  - dollar_volume: raw $822,309,423; pct 0.79; z 0.60; weight 0.05; score 0.79.

**Extension**
- Meaning: Stretch/risk control: RSI, ATR, gap size, move-vs-ATR, and position above the 20D low. Higher is less stretched.
- Formula: `0.24 * pct_rank(rsi_control) + 0.24 * (1 - pct_rank(atr_14_pct)) + 0.19 * (1 - pct_rank(stretch_vs_atr)) + 0.14 * (1 - pct_rank(distance_from_20d_low)) + 0.10 * (1 - pct_rank(abs_gap_1d)) + 0.05 * (1 - pct_rank(failed_gap_or_fade)) + 0.05 * (1 - pct_rank(distribution_pressure))`
  - rsi_control: raw 1.00; pct 0.73; z 0.79; weight 0.24; score 0.73.
  - atr_14_pct: raw 3.93%; pct 0.91; z 1.29; weight 0.24; score 0.09.
  - stretch_vs_atr: raw 1.67x; pct 0.84; z 0.83; weight 0.19; score 0.16.
  - distance_from_20d_low: raw 23.47%; pct 0.93; z 1.64; weight 0.14; score 0.07.
  - abs_gap_1d: raw 0.00; pct 0.47; z -0.26; weight 0.10; score 0.53.
  - failed_gap_or_fade: raw 0.00; pct 0.49; z -0.10; weight 0.05; score 0.51.
  - distribution_pressure: raw 0.00; pct 0.38; z -0.57; weight 0.05; score 0.62.

</details>

<details>
<summary><strong>Risk details</strong> - expand for component math</summary>

Risk fields: `score` is the bucket risk from 0 to 1, `weight` is bucket influence, and `contribution` is the weighted risk added to the final score.

**Extension Risk**
- Score 0.42; weight 0.33; contribution 0.14; severity moderate.
- Evidence: RSI 61.88, 5D return 6.6%, 10D return 21.9%, 20D low distance 23.5%
  - rsi_14: raw 61.88; risk score 0.09; range 60.00-80.00.
  - return_5d: raw 6.57%; risk score 0.21; range 0.04-0.16.
  - return_10d: raw 21.94%; risk score 0.87; range 0.08-0.24.
  - return_20d: raw 6.15%; risk score 0.00; range 0.10-0.30.
  - distance_from_20d_low: raw 23.47%; risk score 0.77; range 0.08-0.28.
  - distance_from_20d_high: raw -0.68%; risk score 0.73; range -0.08-0.02.
  - stretch_vs_atr: raw 1.67x; risk score 0.27; range 1.00-3.50.

**Volatility Risk**
- Score 0.21; weight 0.20; contribution 0.04; severity low.
- Evidence: ATR14 3.9%, gap 0.3%, 1D return 3.5%, fade/distribution False/False
  - atr_14_pct: raw 3.93%; risk score 0.39; range 0.02-0.07.
  - abs_gap_1d: raw 0.00; risk score 0.00; range 0.01-0.06.
  - abs_return_1d: raw 0.04; risk score 0.26; range 0.02-0.08.
  - failed_gap_or_fade: raw n/a; risk score n/a; range n/a-n/a.
  - distribution_pressure: raw n/a; risk score n/a; range n/a-n/a.

**Liquidity/Participation Risk**
- Score 0.01; weight 0.20; contribution 0.00; severity low.
- Evidence: tier high, dollar volume $822.3M, 5D volume 1.57x
  - liquidity_tier: raw n/a; risk score 0.00; range n/a-n/a.
  - dollar_volume: raw $822,309,423; risk score 0.00; range 5000000.00-100000000.00.
  - volume_ratio_5d: raw 1.57x; risk score 0.03; range 1.50-4.00.
  - volume_persistence_10d: raw 90.00%; risk score 0.00; range 0.20-0.80.

**Trend Failure Risk**
- Score 0.00; weight 0.15; contribution 0.00; severity low.
- Evidence: close vs SMA20 9.7%, SMA 5/20 5.2%, up-day ratio 10D 80.0%, RS decoupling False
  - close_vs_sma_20: raw 9.69%; risk score 0.00; range 0.00-0.08.
  - sma_5_20_ratio: raw 5.18%; risk score 0.00; range 0.00-0.06.
  - up_day_ratio_10d: raw 80.00%; risk score 0.00; range 0.30-0.70.
  - rs_decoupling: raw n/a; risk score n/a; range n/a-n/a.

**Event Risk**
- Score 0.00; weight 0.12; contribution 0.00; severity low.
- Evidence: earnings in -31.94 days
  - upcoming_earnings_days: raw -31.94; risk score 0.00; range n/a-n/a.

</details>

**Setup diagnostics:**
- Best diagnostic setup: breakout watch with score 0.83.
- trend confirmation: 0.81.
- momentum continuation: 0.70.
- breakout watch: 0.83.
- pullback risk: 0.31.

**Lifecycle and failure diagnostics:**
- Current phase estimate: expansion.
- Regime probabilities: continuation 0.65; mean reversion 0.29; volatility expansion 0.39.
- Phase scores: ignition 0.47; expansion 0.70; euphoria 0.52; exhaustion 0.19; reversal 0.19.
- Failure signals: poor efficiency 0.00; distribution False; fade False; RS decoupling False.
- Note: Heuristic regime probabilities; not yet calibrated to historical forward outcomes.

**Metrics:**
- **Snapshot:** US / S&P 500 / NYSE/Nasdaq; price 55.76; market cap $26.37B.
- **Scores:** rank 0.76; opportunity 0.74; risk 0.18 (low); confidence 0.77.
- **Regime:** bullish regime if conditions persist over 1d-5d; setup trend confirmation.

**Price action:**
- Returns: 1D 3.55%; 5D 6.57%; 10D 21.94%; 20D 6.15%.
- Trend quality: SMA 5/20 5.18%; close vs SMA20 9.69%; up days 5D 80.00%; up days 10D 80.00%.
- Range and volatility: 5D high -0.68%; 5D low 9.12%; 20D high -0.68%; 20D low 23.47%; close location 1D 87.29%; 5D 92.46%; 20D 96.54%; ATR14 3.93%; gap 0.30%; RSI14 61.88; fade flag False.
- Acceleration/failure: momentum acceleration -4.39%; RS momentum 4.50%; RS decoupling False; distribution pressure False.

**Benchmark relative strength:**
- Versus SPY: 1D 3.30%; 5D 4.72%; 10D 20.83%; 20D 0.89%.
- Versus QQQ: 1D 3.18%; 5D 3.24%; 10D 19.37%; 20D -4.42%.
- Versus sector peers: 5D 6.03%; 10D 20.75%; 20D 6.48%.
- Market regime: 0.91 (supportive).

**Volume and liquidity:**
- Relative volume: 5D 1.57x; 20D 1.74x; 5D/20D trend 1.10x.
- Participation evidence: volume z-score 2.92; elevated-volume persistence 5D 100.00%; 10D 90.00%; up/down volume 10D 4.03x.
- Volume quality: acceleration 0.47; price/volume efficiency 4.18%; effort/result 23.93x; distribution days 10D 2.00.
- Liquidity: tier high; dollar volume $822,309,423.

**Other context:**
- Upcoming earnings days: -31.94.

**Why it screens well:**
- Trend 0.89: SMA 5/20 5.2%, close vs SMA20 9.7%, 20D close location 96.5%, market regime supportive.
- Momentum 0.61: acceleration -4.4%, 1D 3.5%, 5D close location 92.5%, price/volume efficiency 4.2%.
- Relative strength 0.92: strongest window 10D vs SPY 20.8% (pct 0.97); 5D SPY 4.7%, RS momentum 4.5%, 10D sector 20.7%.
- Participation 0.76: volume z-score 2.92, 5D persistence 100.0%, 10D persistence 90.0% (pct 1.00), volume acceleration 0.47, up/down volume 4.03x, efficiency 4.2%, liquidity tier high ($822.3M).
- Extension control 0.34: RSI 61.88, ATR14 3.9%, gap 0.3%, 20D low distance 23.5%, fade/distribution flags False/False.
- Opportunity score is 0.74; risk score is 0.18.
- Factor reason codes: TREND_CONSTRUCTIVE, MOMENTUM_POSITIVE, RELATIVE_STRENGTH_SUPPORTIVE, PARTICIPATION_EXPANDING, EXTENSION_ELEVATED, RSI_CONSTRUCTIVE.

**1-day to 1-week plan:**
- Watch whether the stock continues to outperform SPY/QQQ over the next session.
- Watch whether relative volume stays supportive; fading volume weakens the setup.
- Treat loss of factor support plus fading relative volume as invalidation.

**Main risks:**
- moderate extension risk: RSI 61.88, 5D return 6.6%, 10D return 21.9%, 20D low distance 23.5%
- Risk score is 0.18 (low) on a continuous 0 to 1 scale.

**Verdict:** This is a watchlist candidate for short-term research only; the setup depends on momentum and volume staying intact. Not financial advice.

---

### MSCI - MSCI Inc.
**Setup:** MSCI is a trend confirmation candidate based on the current 1-day to 1-week screen. The setup is a conditional market regime, not a standalone price forecast.

**Quick scorecard:**
- **Factor scores:** trend 0.84; momentum 0.85; relative strength 0.90; participation 0.65; extension control 0.33.
- **Read this as:** higher trend/momentum/relative strength/participation is better; higher extension control means less stretched.
- Trend 0.84: SMA 5/20 3.7%, close vs SMA20 7.7%, 20D close location 89.9%, market regime supportive.
- Momentum 0.85: acceleration 2.8%, 1D 0.8%, 5D close location 85.4%, price/volume efficiency 5.2%.
- Relative strength 0.90: strongest window 10D vs SPY 10.1% (pct 0.91); 5D SPY 6.6%, RS momentum 6.1%, 10D sector 10.0%.
- Participation 0.65: volume z-score 2.12, 5D persistence 60.0%, 10D persistence 40.0% (pct 0.53), volume acceleration 0.55, up/down volume 2.52x, efficiency 5.2%, liquidity tier high ($692.6M).
- Extension control 0.33: RSI 73.07, ATR14 2.7%, gap 0.1%, 20D low distance 14.3%, fade/distribution flags False/False.

<details>
<summary><strong>Formula details</strong> - expand for component math</summary>

Component fields: `raw` is the observed value, `pct` is screened-universe percentile, `z` is standard deviations from average, `weight` is formula influence, and `score` is the component score after direction adjustment.

**Trend**
- Meaning: Price structure: longer-window return, short-vs-medium moving average alignment, close vs SMA20, and recent up-day consistency.
- Formula: `0.35 * pct_rank(sma_5_20_ratio) + 0.25 * pct_rank(close_vs_sma_20) + 0.15 * pct_rank(up_day_ratio_10d) + 0.15 * pct_rank(close_location_20d) + 0.10 * pct_rank(market_regime_score)`
  - sma_5_20_ratio: raw 3.70%; pct 0.85; z 0.73; weight 0.35; score 0.85.
  - close_vs_sma_20: raw 7.75%; pct 0.91; z 1.14; weight 0.25; score 0.91.
  - up_day_ratio_10d: raw 70.00%; pct 0.87; z 1.19; weight 0.15; score 0.87.
  - close_location_20d: raw 89.87%; pct 0.89; z 1.31; weight 0.15; score 0.89.
  - market_regime_score: raw 0.91; pct 0.50; z n/a; weight 0.10; score 0.50.

**Momentum**
- Meaning: Recent price movement across 1D, 5D, 10D, and 20D windows.
- Formula: `0.35 * pct_rank(momentum_acceleration_5d_10d) + 0.15 * pct_rank(return_1d) + 0.20 * pct_rank(close_location_5d) + 0.15 * pct_rank(rs_momentum_5d_20d) + 0.15 * pct_rank(price_volume_efficiency_5d)`
  - momentum_acceleration_5d_10d: raw 2.81%; pct 0.85; z 0.87; weight 0.35; score 0.85.
  - return_1d: raw 0.78%; pct 0.76; z 0.37; weight 0.15; score 0.76.
  - close_location_5d: raw 85.43%; pct 0.85; z 1.26; weight 0.20; score 0.85.
  - rs_momentum_5d_20d: raw 0.06; pct 0.91; z 1.26; weight 0.15; score 0.91.
  - price_volume_efficiency_5d: raw 5.24%; pct 0.89; z 0.89; weight 0.15; score 0.89.

**Relative Strength**
- Meaning: Outperformance or underperformance versus SPY and QQQ across multiple windows.
- Formula: `0.25 * pct_rank(rs_momentum_5d_20d) + 0.20 * pct_rank(rel_strength_spy_10d) + 0.15 * pct_rank(rel_strength_qqq_10d) + 0.15 * pct_rank(sector_relative_strength_5d) + 0.15 * pct_rank(sector_relative_strength_10d) + 0.10 * pct_rank(sector_relative_strength_20d)`
  - rs_momentum_5d_20d: raw 0.06; pct 0.91; z 1.26; weight 0.25; score 0.91.
  - rel_strength_spy_10d: raw 10.12%; pct 0.91; z 1.19; weight 0.20; score 0.91.
  - rel_strength_qqq_10d: raw 8.66%; pct 0.91; z 1.19; weight 0.15; score 0.91.
  - sector_relative_strength_5d: raw 7.88%; pct 0.92; z 1.27; weight 0.15; score 0.92.
  - sector_relative_strength_10d: raw 10.04%; pct 0.91; z 1.19; weight 0.15; score 0.91.
  - sector_relative_strength_20d: raw 7.47%; pct 0.81; z 0.59; weight 0.10; score 0.81.

**Participation**
- Meaning: Volume and liquidity support: relative volume, persistence of elevated volume, volume z-score, and dollar volume.
- Formula: `0.14 * pct_rank(volume_acceleration_5d_20d) + 0.14 * pct_rank(volume_ratio_5d) + 0.10 * pct_rank(volume_trend_5d_20d) + 0.14 * pct_rank(volume_persistence_5d) + 0.14 * pct_rank(volume_persistence_10d) + 0.10 * pct_rank(volume_z_score_20d) + 0.10 * pct_rank(up_volume_ratio_10d) + 0.10 * pct_rank(price_volume_efficiency_5d) + 0.05 * pct_rank(dollar_volume)`
  - volume_acceleration_5d_20d: raw 0.55x; pct 0.40; z -0.30; weight 0.14; score 0.40.
  - volume_ratio_5d: raw 1.61x; pct 0.48; z -0.19; weight 0.14; score 0.48.
  - volume_trend_5d_20d: raw 1.05x; pct 0.80; z 0.50; weight 0.10; score 0.80.
  - volume_persistence_5d: raw 60.00%; pct 0.76; z 0.78; weight 0.14; score 0.76.
  - volume_persistence_10d: raw 40.00%; pct 0.53; z 0.04; weight 0.14; score 0.53.
  - volume_z_score_20d: raw 2.12; pct 0.62; z -0.03; weight 0.10; score 0.62.
  - up_volume_ratio_10d: raw 2.52x; pct 0.87; z 0.56; weight 0.10; score 0.87.
  - price_volume_efficiency_5d: raw 5.24%; pct 0.89; z 0.89; weight 0.10; score 0.89.
  - dollar_volume: raw $692,560,727; pct 0.72; z 0.35; weight 0.05; score 0.72.

**Extension**
- Meaning: Stretch/risk control: RSI, ATR, gap size, move-vs-ATR, and position above the 20D low. Higher is less stretched.
- Formula: `0.24 * pct_rank(rsi_control) + 0.24 * (1 - pct_rank(atr_14_pct)) + 0.19 * (1 - pct_rank(stretch_vs_atr)) + 0.14 * (1 - pct_rank(distance_from_20d_low)) + 0.10 * (1 - pct_rank(abs_gap_1d)) + 0.05 * (1 - pct_rank(failed_gap_or_fade)) + 0.05 * (1 - pct_rank(distribution_pressure))`
  - rsi_control: raw 0.60; pct 0.20; z -0.63; weight 0.24; score 0.20.
  - atr_14_pct: raw 2.67%; pct 0.53; z -0.06; weight 0.24; score 0.47.
  - stretch_vs_atr: raw 3.16x; pct 0.94; z 1.68; weight 0.19; score 0.06.
  - distance_from_20d_low: raw 14.27%; pct 0.85; z 0.65; weight 0.14; score 0.15.
  - abs_gap_1d: raw 0.00; pct 0.17; z -0.57; weight 0.10; score 0.83.
  - failed_gap_or_fade: raw 0.00; pct 0.49; z -0.10; weight 0.05; score 0.51.
  - distribution_pressure: raw 0.00; pct 0.38; z -0.57; weight 0.05; score 0.62.

</details>

<details>
<summary><strong>Risk details</strong> - expand for component math</summary>

Risk fields: `score` is the bucket risk from 0 to 1, `weight` is bucket influence, and `contribution` is the weighted risk added to the final score.

**Extension Risk**
- Score 0.44; weight 0.33; contribution 0.14; severity moderate.
- Evidence: RSI 73.07, 5D return 8.4%, 10D return 11.2%, 20D low distance 14.3%
  - rsi_14: raw 73.07; risk score 0.65; range 60.00-80.00.
  - return_5d: raw 8.42%; risk score 0.37; range 0.04-0.16.
  - return_10d: raw 11.23%; risk score 0.20; range 0.08-0.24.
  - return_20d: raw 7.14%; risk score 0.00; range 0.10-0.30.
  - distance_from_20d_low: raw 14.27%; risk score 0.31; range 0.08-0.28.
  - distance_from_20d_high: raw -1.39%; risk score 0.66; range -0.08-0.02.
  - stretch_vs_atr: raw 3.16x; risk score 0.86; range 1.00-3.50.

**Volatility Risk**
- Score 0.04; weight 0.20; contribution 0.01; severity low.
- Evidence: ATR14 2.7%, gap 0.1%, 1D return 0.8%, fade/distribution False/False
  - atr_14_pct: raw 2.67%; risk score 0.13; range 0.02-0.07.
  - abs_gap_1d: raw 0.00; risk score 0.00; range 0.01-0.06.
  - abs_return_1d: raw 0.01; risk score 0.00; range 0.02-0.08.
  - failed_gap_or_fade: raw n/a; risk score n/a; range n/a-n/a.
  - distribution_pressure: raw n/a; risk score n/a; range n/a-n/a.

**Liquidity/Participation Risk**
- Score 0.18; weight 0.20; contribution 0.04; severity low.
- Evidence: tier high, dollar volume $692.6M, 5D volume 1.61x
  - liquidity_tier: raw n/a; risk score 0.00; range n/a-n/a.
  - dollar_volume: raw $692,560,727; risk score 0.00; range 5000000.00-100000000.00.
  - volume_ratio_5d: raw 1.61x; risk score 0.04; range 1.50-4.00.
  - volume_persistence_10d: raw 40.00%; risk score 0.67; range 0.20-0.80.

**Trend Failure Risk**
- Score 0.00; weight 0.15; contribution 0.00; severity low.
- Evidence: close vs SMA20 7.7%, SMA 5/20 3.7%, up-day ratio 10D 70.0%, RS decoupling False
  - close_vs_sma_20: raw 7.75%; risk score 0.00; range 0.00-0.08.
  - sma_5_20_ratio: raw 3.70%; risk score 0.00; range 0.00-0.06.
  - up_day_ratio_10d: raw 70.00%; risk score 0.00; range 0.30-0.70.
  - rs_decoupling: raw n/a; risk score n/a; range n/a-n/a.

**Event Risk**
- Score 0.00; weight 0.12; contribution 0.00; severity low.
- Evidence: earnings in 51.06 days
  - upcoming_earnings_days: raw 51.06; risk score 0.00; range n/a-n/a.

</details>

**Setup diagnostics:**
- Best diagnostic setup: trend confirmation with score 0.82.
- trend confirmation: 0.82.
- momentum continuation: 0.75.
- breakout watch: 0.81.
- pullback risk: 0.27.

**Lifecycle and failure diagnostics:**
- Current phase estimate: expansion.
- Regime probabilities: continuation 0.70; mean reversion 0.27; volatility expansion 0.37.
- Phase scores: ignition 0.67; expansion 0.72; euphoria 0.59; exhaustion 0.13; reversal 0.14.
- Failure signals: poor efficiency 0.00; distribution False; fade False; RS decoupling False.
- Note: Heuristic regime probabilities; not yet calibrated to historical forward outcomes.

**Metrics:**
- **Snapshot:** US / S&P 500 / NYSE/Nasdaq; price 631.38; market cap $45.92B.
- **Scores:** rank 0.76; opportunity 0.74; risk 0.19 (low); confidence 0.77.
- **Regime:** bullish regime if conditions persist over 1d-5d; setup trend confirmation.

**Price action:**
- Returns: 1D 0.78%; 5D 8.42%; 10D 11.23%; 20D 7.14%.
- Trend quality: SMA 5/20 3.70%; close vs SMA20 7.75%; up days 5D 80.00%; up days 10D 70.00%.
- Range and volatility: 5D high -1.39%; 5D low 9.00%; 20D high -1.39%; 20D low 14.27%; close location 1D 48.52%; 5D 85.43%; 20D 89.87%; ATR14 2.67%; gap 0.09%; RSI14 73.07; fade flag False.
- Acceleration/failure: momentum acceleration 2.81%; RS momentum 6.10%; RS decoupling False; distribution pressure False.

**Benchmark relative strength:**
- Versus SPY: 1D 0.53%; 5D 6.57%; 10D 10.12%; 20D 1.88%.
- Versus QQQ: 1D 0.41%; 5D 5.09%; 10D 8.66%; 20D -3.42%.
- Versus sector peers: 5D 7.88%; 10D 10.04%; 20D 7.47%.
- Market regime: 0.91 (supportive).

**Volume and liquidity:**
- Relative volume: 5D 1.61x; 20D 1.70x; 5D/20D trend 1.05x.
- Participation evidence: volume z-score 2.12; elevated-volume persistence 5D 60.00%; 10D 40.00%; up/down volume 10D 2.52x.
- Volume quality: acceleration 0.55; price/volume efficiency 5.24%; effort/result 19.09x; distribution days 10D 1.00.
- Liquidity: tier high; dollar volume $692,560,727.

**Other context:**
- Upcoming earnings days: 51.06.

**Why it screens well:**
- Trend 0.84: SMA 5/20 3.7%, close vs SMA20 7.7%, 20D close location 89.9%, market regime supportive.
- Momentum 0.85: acceleration 2.8%, 1D 0.8%, 5D close location 85.4%, price/volume efficiency 5.2%.
- Relative strength 0.90: strongest window 10D vs SPY 10.1% (pct 0.91); 5D SPY 6.6%, RS momentum 6.1%, 10D sector 10.0%.
- Participation 0.65: volume z-score 2.12, 5D persistence 60.0%, 10D persistence 40.0% (pct 0.53), volume acceleration 0.55, up/down volume 2.52x, efficiency 5.2%, liquidity tier high ($692.6M).
- Extension control 0.33: RSI 73.07, ATR14 2.7%, gap 0.1%, 20D low distance 14.3%, fade/distribution flags False/False.
- Opportunity score is 0.74; risk score is 0.19.
- Factor reason codes: TREND_CONSTRUCTIVE, MOMENTUM_POSITIVE, RELATIVE_STRENGTH_SUPPORTIVE, PARTICIPATION_EXPANDING, EXTENSION_ELEVATED, RSI_STRETCHED.

**1-day to 1-week plan:**
- Watch whether the stock continues to outperform SPY/QQQ over the next session.
- Watch whether relative volume stays supportive; fading volume weakens the setup.
- Treat loss of factor support plus fading relative volume as invalidation.

**Main risks:**
- moderate extension risk: RSI 73.07, 5D return 8.4%, 10D return 11.2%, 20D low distance 14.3%
- Risk score is 0.19 (low) on a continuous 0 to 1 scale.

**Verdict:** This is a watchlist candidate for short-term research only; the setup depends on momentum and volume staying intact. Not financial advice.

---

### UPS - United Parcel Service, Inc.
**Setup:** UPS is a trend confirmation candidate based on the current 1-day to 1-week screen. The setup is a conditional market regime, not a standalone price forecast.

**Quick scorecard:**
- **Factor scores:** trend 0.86; momentum 0.85; relative strength 0.88; participation 0.62; extension control 0.37.
- **Read this as:** higher trend/momentum/relative strength/participation is better; higher extension control means less stretched.
- Trend 0.86: SMA 5/20 4.7%, close vs SMA20 7.3%, 20D close location 90.6%, market regime supportive.
- Momentum 0.85: acceleration 3.5%, 1D 0.0%, 5D close location 92.7%, price/volume efficiency 4.3%.
- Relative strength 0.88: strongest window 10D vs SPY 9.1% (pct 0.90); 5D SPY 6.7%, RS momentum 8.1%, 10D sector 9.0%.
- Participation 0.62: volume z-score 1.41, 5D persistence 40.0%, 10D persistence 30.0% (pct 0.33), volume acceleration 1.18, up/down volume 4.37x, efficiency 4.3%, liquidity tier high ($1.1B).
- Extension control 0.37: RSI 72.29, ATR14 2.2%, gap -0.1%, 20D low distance 13.7%, fade/distribution flags False/False.

<details>
<summary><strong>Formula details</strong> - expand for component math</summary>

Component fields: `raw` is the observed value, `pct` is screened-universe percentile, `z` is standard deviations from average, `weight` is formula influence, and `score` is the component score after direction adjustment.

**Trend**
- Meaning: Price structure: longer-window return, short-vs-medium moving average alignment, close vs SMA20, and recent up-day consistency.
- Formula: `0.35 * pct_rank(sma_5_20_ratio) + 0.25 * pct_rank(close_vs_sma_20) + 0.15 * pct_rank(up_day_ratio_10d) + 0.15 * pct_rank(close_location_20d) + 0.10 * pct_rank(market_regime_score)`
  - sma_5_20_ratio: raw 4.74%; pct 0.88; z 1.02; weight 0.35; score 0.88.
  - close_vs_sma_20: raw 7.28%; pct 0.90; z 1.06; weight 0.25; score 0.90.
  - up_day_ratio_10d: raw 80.00%; pct 0.96; z 1.89; weight 0.15; score 0.96.
  - close_location_20d: raw 90.61%; pct 0.90; z 1.33; weight 0.15; score 0.90.
  - market_regime_score: raw 0.91; pct 0.50; z n/a; weight 0.10; score 0.50.

**Momentum**
- Meaning: Recent price movement across 1D, 5D, 10D, and 20D windows.
- Formula: `0.35 * pct_rank(momentum_acceleration_5d_10d) + 0.15 * pct_rank(return_1d) + 0.20 * pct_rank(close_location_5d) + 0.15 * pct_rank(rs_momentum_5d_20d) + 0.15 * pct_rank(price_volume_efficiency_5d)`
  - momentum_acceleration_5d_10d: raw 3.48%; pct 0.88; z 1.07; weight 0.35; score 0.88.
  - return_1d: raw 0.02%; pct 0.58; z 0.02; weight 0.15; score 0.58.
  - close_location_5d: raw 92.69%; pct 0.92; z 1.49; weight 0.20; score 0.92.
  - rs_momentum_5d_20d: raw 0.08; pct 0.95; z 1.71; weight 0.15; score 0.95.
  - price_volume_efficiency_5d: raw 4.26%; pct 0.85; z 0.68; weight 0.15; score 0.85.

**Relative Strength**
- Meaning: Outperformance or underperformance versus SPY and QQQ across multiple windows.
- Formula: `0.25 * pct_rank(rs_momentum_5d_20d) + 0.20 * pct_rank(rel_strength_spy_10d) + 0.15 * pct_rank(rel_strength_qqq_10d) + 0.15 * pct_rank(sector_relative_strength_5d) + 0.15 * pct_rank(sector_relative_strength_10d) + 0.10 * pct_rank(sector_relative_strength_20d)`
  - rs_momentum_5d_20d: raw 0.08; pct 0.95; z 1.71; weight 0.25; score 0.95.
  - rel_strength_spy_10d: raw 9.12%; pct 0.90; z 1.06; weight 0.20; score 0.90.
  - rel_strength_qqq_10d: raw 7.66%; pct 0.90; z 1.06; weight 0.15; score 0.90.
  - sector_relative_strength_5d: raw 8.05%; pct 0.92; z 1.30; weight 0.15; score 0.92.
  - sector_relative_strength_10d: raw 9.04%; pct 0.90; z 1.06; weight 0.15; score 0.90.
  - sector_relative_strength_20d: raw 0.04%; pct 0.54; z -0.12; weight 0.10; score 0.54.

**Participation**
- Meaning: Volume and liquidity support: relative volume, persistence of elevated volume, volume z-score, and dollar volume.
- Formula: `0.14 * pct_rank(volume_acceleration_5d_20d) + 0.14 * pct_rank(volume_ratio_5d) + 0.10 * pct_rank(volume_trend_5d_20d) + 0.14 * pct_rank(volume_persistence_5d) + 0.14 * pct_rank(volume_persistence_10d) + 0.10 * pct_rank(volume_z_score_20d) + 0.10 * pct_rank(up_volume_ratio_10d) + 0.10 * pct_rank(price_volume_efficiency_5d) + 0.05 * pct_rank(dollar_volume)`
  - volume_acceleration_5d_20d: raw 1.18x; pct 0.72; z 0.26; weight 0.14; score 0.72.
  - volume_ratio_5d: raw 2.02x; pct 0.69; z 0.20; weight 0.14; score 0.69.
  - volume_trend_5d_20d: raw 0.84x; pct 0.38; z -0.33; weight 0.10; score 0.38.
  - volume_persistence_5d: raw 40.00%; pct 0.54; z 0.03; weight 0.14; score 0.54.
  - volume_persistence_10d: raw 30.00%; pct 0.33; z -0.48; weight 0.14; score 0.33.
  - volume_z_score_20d: raw 1.41; pct 0.49; z -0.25; weight 0.10; score 0.49.
  - up_volume_ratio_10d: raw 4.37x; pct 0.95; z 1.63; weight 0.10; score 0.95.
  - price_volume_efficiency_5d: raw 4.26%; pct 0.85; z 0.68; weight 0.10; score 0.85.
  - dollar_volume: raw $1.12B; pct 0.90; z 1.17; weight 0.05; score 0.90.

**Extension**
- Meaning: Stretch/risk control: RSI, ATR, gap size, move-vs-ATR, and position above the 20D low. Higher is less stretched.
- Formula: `0.24 * pct_rank(rsi_control) + 0.24 * (1 - pct_rank(atr_14_pct)) + 0.19 * (1 - pct_rank(stretch_vs_atr)) + 0.14 * (1 - pct_rank(distance_from_20d_low)) + 0.10 * (1 - pct_rank(abs_gap_1d)) + 0.05 * (1 - pct_rank(failed_gap_or_fade)) + 0.05 * (1 - pct_rank(distribution_pressure))`
  - rsi_control: raw 0.60; pct 0.20; z -0.63; weight 0.24; score 0.20.
  - atr_14_pct: raw 2.23%; pct 0.34; z -0.53; weight 0.24; score 0.66.
  - stretch_vs_atr: raw 3.86x; pct 0.96; z 2.08; weight 0.19; score 0.04.
  - distance_from_20d_low: raw 13.67%; pct 0.84; z 0.58; weight 0.14; score 0.16.
  - abs_gap_1d: raw 0.00; pct 0.12; z -0.60; weight 0.10; score 0.88.
  - failed_gap_or_fade: raw 0.00; pct 0.49; z -0.10; weight 0.05; score 0.51.
  - distribution_pressure: raw 0.00; pct 0.38; z -0.57; weight 0.05; score 0.62.

</details>

<details>
<summary><strong>Risk details</strong> - expand for component math</summary>

Risk fields: `score` is the bucket risk from 0 to 1, `weight` is bucket influence, and `contribution` is the weighted risk added to the final score.

**Extension Risk**
- Score 0.44; weight 0.33; contribution 0.15; severity moderate.
- Evidence: RSI 72.29, 5D return 8.6%, 10D return 10.2%, 20D low distance 13.7%
  - rsi_14: raw 72.29; risk score 0.61; range 60.00-80.00.
  - return_5d: raw 8.59%; risk score 0.38; range 0.04-0.16.
  - return_10d: raw 10.23%; risk score 0.14; range 0.08-0.24.
  - return_20d: raw -0.29%; risk score 0.00; range 0.10-0.30.
  - distance_from_20d_low: raw 13.67%; risk score 0.28; range 0.08-0.28.
  - distance_from_20d_high: raw -1.23%; risk score 0.68; range -0.08-0.02.
  - stretch_vs_atr: raw 3.86x; risk score 1.00; range 1.00-3.50.

**Volatility Risk**
- Score 0.02; weight 0.20; contribution 0.00; severity low.
- Evidence: ATR14 2.2%, gap -0.1%, 1D return 0.0%, fade/distribution False/False
  - atr_14_pct: raw 2.23%; risk score 0.05; range 0.02-0.07.
  - abs_gap_1d: raw 0.00; risk score 0.00; range 0.01-0.06.
  - abs_return_1d: raw 0.00; risk score 0.00; range 0.02-0.08.
  - failed_gap_or_fade: raw n/a; risk score n/a; range n/a-n/a.
  - distribution_pressure: raw n/a; risk score n/a; range n/a-n/a.

**Liquidity/Participation Risk**
- Score 0.26; weight 0.20; contribution 0.05; severity low.
- Evidence: tier high, dollar volume $1.1B, 5D volume 2.02x
  - liquidity_tier: raw n/a; risk score 0.00; range n/a-n/a.
  - dollar_volume: raw $1.12B; risk score 0.00; range 5000000.00-100000000.00.
  - volume_ratio_5d: raw 2.02x; risk score 0.21; range 1.50-4.00.
  - volume_persistence_10d: raw 30.00%; risk score 0.83; range 0.20-0.80.

**Trend Failure Risk**
- Score 0.00; weight 0.15; contribution 0.00; severity low.
- Evidence: close vs SMA20 7.3%, SMA 5/20 4.7%, up-day ratio 10D 80.0%, RS decoupling False
  - close_vs_sma_20: raw 7.28%; risk score 0.00; range 0.00-0.08.
  - sma_5_20_ratio: raw 4.74%; risk score 0.00; range 0.00-0.06.
  - up_day_ratio_10d: raw 80.00%; risk score 0.00; range 0.30-0.70.
  - rs_decoupling: raw n/a; risk score n/a; range n/a-n/a.

**Event Risk**
- Score 0.00; weight 0.12; contribution 0.00; severity low.
- Evidence: earnings in -32.94 days
  - upcoming_earnings_days: raw -32.94; risk score 0.00; range n/a-n/a.

</details>

**Setup diagnostics:**
- Best diagnostic setup: trend confirmation with score 0.82.
- trend confirmation: 0.82.
- momentum continuation: 0.74.
- breakout watch: 0.81.
- pullback risk: 0.25.

**Lifecycle and failure diagnostics:**
- Current phase estimate: ignition.
- Regime probabilities: continuation 0.74; mean reversion 0.28; volatility expansion 0.44.
- Phase scores: ignition 0.79; expansion 0.73; euphoria 0.64; exhaustion 0.12; reversal 0.14.
- Failure signals: poor efficiency 0.00; distribution False; fade False; RS decoupling False.
- Note: Heuristic regime probabilities; not yet calibrated to historical forward outcomes.

**Metrics:**
- **Snapshot:** US / S&P 500 / NYSE/Nasdaq; price 106.69; market cap $90.69B.
- **Scores:** rank 0.76; opportunity 0.74; risk 0.20 (low); confidence 0.77.
- **Regime:** bullish regime if conditions persist over 1d-5d; setup trend confirmation.

**Price action:**
- Returns: 1D 0.02%; 5D 8.59%; 10D 10.23%; 20D -0.29%.
- Trend quality: SMA 5/20 4.74%; close vs SMA20 7.28%; up days 5D 100.00%; up days 10D 80.00%.
- Range and volatility: 5D high -0.58%; 5D low 7.95%; 20D high -1.23%; 20D low 13.67%; close location 1D 67.71%; 5D 92.69%; 20D 90.61%; ATR14 2.23%; gap -0.07%; RSI14 72.29; fade flag False.
- Acceleration/failure: momentum acceleration 3.48%; RS momentum 8.12%; RS decoupling False; distribution pressure False.

**Benchmark relative strength:**
- Versus SPY: 1D -0.23%; 5D 6.74%; 10D 9.12%; 20D -5.55%.
- Versus QQQ: 1D -0.35%; 5D 5.26%; 10D 7.66%; 20D -10.85%.
- Versus sector peers: 5D 8.05%; 10D 9.04%; 20D 0.04%.
- Market regime: 0.91 (supportive).

**Volume and liquidity:**
- Relative volume: 5D 2.02x; 20D 1.69x; 5D/20D trend 0.84x.
- Participation evidence: volume z-score 1.41; elevated-volume persistence 5D 40.00%; 10D 30.00%; up/down volume 10D 4.37x.
- Volume quality: acceleration 1.18; price/volume efficiency 4.26%; effort/result 23.48x; distribution days 10D 1.00.
- Liquidity: tier high; dollar volume $1.12B.

**Other context:**
- Upcoming earnings days: -32.94.

**Why it screens well:**
- Trend 0.86: SMA 5/20 4.7%, close vs SMA20 7.3%, 20D close location 90.6%, market regime supportive.
- Momentum 0.85: acceleration 3.5%, 1D 0.0%, 5D close location 92.7%, price/volume efficiency 4.3%.
- Relative strength 0.88: strongest window 10D vs SPY 9.1% (pct 0.90); 5D SPY 6.7%, RS momentum 8.1%, 10D sector 9.0%.
- Participation 0.62: volume z-score 1.41, 5D persistence 40.0%, 10D persistence 30.0% (pct 0.33), volume acceleration 1.18, up/down volume 4.37x, efficiency 4.3%, liquidity tier high ($1.1B).
- Extension control 0.37: RSI 72.29, ATR14 2.2%, gap -0.1%, 20D low distance 13.7%, fade/distribution flags False/False.
- Opportunity score is 0.74; risk score is 0.20.
- Factor reason codes: TREND_CONSTRUCTIVE, MOMENTUM_POSITIVE, RELATIVE_STRENGTH_SUPPORTIVE, PARTICIPATION_EXPANDING, EXTENSION_ELEVATED, RSI_STRETCHED.

**1-day to 1-week plan:**
- Watch whether the stock continues to outperform SPY/QQQ over the next session.
- Watch whether relative volume stays supportive; fading volume weakens the setup.
- Treat loss of factor support plus fading relative volume as invalidation.

**Main risks:**
- moderate extension risk: RSI 72.29, 5D return 8.6%, 10D return 10.2%, 20D low distance 13.7%
- Risk score is 0.20 (low) on a continuous 0 to 1 scale.

**Verdict:** This is a watchlist candidate for short-term research only; the setup depends on momentum and volume staying intact. Not financial advice.

---

### RCL - Royal Caribbean Cruises Ltd.
**Setup:** RCL is a trend confirmation candidate based on the current 1-day to 1-week screen. The setup is a conditional market regime, not a standalone price forecast.

**Quick scorecard:**
- **Factor scores:** trend 0.78; momentum 0.91; relative strength 0.88; participation 0.65; extension control 0.29.
- **Read this as:** higher trend/momentum/relative strength/participation is better; higher extension control means less stretched.
- Trend 0.78: SMA 5/20 2.6%, close vs SMA20 7.0%, 20D close location 92.5%, market regime supportive.
- Momentum 0.91: acceleration 5.7%, 1D 1.2%, 5D close location 89.2%, price/volume efficiency 7.6%.
- Relative strength 0.88: strongest window 5D vs SPY 7.5% (pct n/a); 5D SPY 7.5%, RS momentum 6.8%, 10D sector 6.1%.
- Participation 0.65: volume z-score 0.88, 5D persistence 80.0%, 10D persistence 70.0% (pct 0.93), volume acceleration 0.14, up/down volume 2.14x, efficiency 7.6%, liquidity tier high ($1.2B).
- Extension control 0.29: RSI 55.31, ATR14 4.1%, gap 0.6%, 20D low distance 22.6%, fade/distribution flags False/False.

<details>
<summary><strong>Formula details</strong> - expand for component math</summary>

Component fields: `raw` is the observed value, `pct` is screened-universe percentile, `z` is standard deviations from average, `weight` is formula influence, and `score` is the component score after direction adjustment.

**Trend**
- Meaning: Price structure: longer-window return, short-vs-medium moving average alignment, close vs SMA20, and recent up-day consistency.
- Formula: `0.35 * pct_rank(sma_5_20_ratio) + 0.25 * pct_rank(close_vs_sma_20) + 0.15 * pct_rank(up_day_ratio_10d) + 0.15 * pct_rank(close_location_20d) + 0.10 * pct_rank(market_regime_score)`
  - sma_5_20_ratio: raw 2.57%; pct 0.76; z 0.41; weight 0.35; score 0.76.
  - close_vs_sma_20: raw 6.95%; pct 0.89; z 1.00; weight 0.25; score 0.89.
  - up_day_ratio_10d: raw 60.00%; pct 0.69; z 0.50; weight 0.15; score 0.69.
  - close_location_20d: raw 92.55%; pct 0.91; z 1.40; weight 0.15; score 0.91.
  - market_regime_score: raw 0.91; pct 0.50; z n/a; weight 0.10; score 0.50.

**Momentum**
- Meaning: Recent price movement across 1D, 5D, 10D, and 20D windows.
- Formula: `0.35 * pct_rank(momentum_acceleration_5d_10d) + 0.15 * pct_rank(return_1d) + 0.20 * pct_rank(close_location_5d) + 0.15 * pct_rank(rs_momentum_5d_20d) + 0.15 * pct_rank(price_volume_efficiency_5d)`
  - momentum_acceleration_5d_10d: raw 5.71%; pct 0.94; z 1.73; weight 0.35; score 0.94.
  - return_1d: raw 1.19%; pct 0.82; z 0.56; weight 0.15; score 0.82.
  - close_location_5d: raw 89.25%; pct 0.88; z 1.38; weight 0.20; score 0.88.
  - rs_momentum_5d_20d: raw 0.07; pct 0.92; z 1.42; weight 0.15; score 0.92.
  - price_volume_efficiency_5d: raw 7.57%; pct 0.92; z 1.40; weight 0.15; score 0.92.

**Relative Strength**
- Meaning: Outperformance or underperformance versus SPY and QQQ across multiple windows.
- Formula: `0.25 * pct_rank(rs_momentum_5d_20d) + 0.20 * pct_rank(rel_strength_spy_10d) + 0.15 * pct_rank(rel_strength_qqq_10d) + 0.15 * pct_rank(sector_relative_strength_5d) + 0.15 * pct_rank(sector_relative_strength_10d) + 0.10 * pct_rank(sector_relative_strength_20d)`
  - rs_momentum_5d_20d: raw 0.07; pct 0.92; z 1.42; weight 0.25; score 0.92.
  - rel_strength_spy_10d: raw 6.14%; pct 0.84; z 0.65; weight 0.20; score 0.84.
  - rel_strength_qqq_10d: raw 4.68%; pct 0.84; z 0.65; weight 0.15; score 0.84.
  - sector_relative_strength_5d: raw 8.80%; pct 0.93; z 1.43; weight 0.15; score 0.93.
  - sector_relative_strength_10d: raw 6.06%; pct 0.84; z 0.65; weight 0.15; score 0.84.
  - sector_relative_strength_20d: raw 8.24%; pct 0.83; z 0.66; weight 0.10; score 0.83.

**Participation**
- Meaning: Volume and liquidity support: relative volume, persistence of elevated volume, volume z-score, and dollar volume.
- Formula: `0.14 * pct_rank(volume_acceleration_5d_20d) + 0.14 * pct_rank(volume_ratio_5d) + 0.10 * pct_rank(volume_trend_5d_20d) + 0.14 * pct_rank(volume_persistence_5d) + 0.14 * pct_rank(volume_persistence_10d) + 0.10 * pct_rank(volume_z_score_20d) + 0.10 * pct_rank(up_volume_ratio_10d) + 0.10 * pct_rank(price_volume_efficiency_5d) + 0.05 * pct_rank(dollar_volume)`
  - volume_acceleration_5d_20d: raw 0.14x; pct 0.19; z -0.67; weight 0.14; score 0.19.
  - volume_ratio_5d: raw 1.23x; pct 0.27; z -0.55; weight 0.14; score 0.27.
  - volume_trend_5d_20d: raw 1.09x; pct 0.82; z 0.63; weight 0.10; score 0.82.
  - volume_persistence_5d: raw 80.00%; pct 0.91; z 1.54; weight 0.14; score 0.91.
  - volume_persistence_10d: raw 70.00%; pct 0.93; z 1.62; weight 0.14; score 0.93.
  - volume_z_score_20d: raw 0.88; pct 0.40; z -0.41; weight 0.10; score 0.40.
  - up_volume_ratio_10d: raw 2.14x; pct 0.80; z 0.34; weight 0.10; score 0.80.
  - price_volume_efficiency_5d: raw 7.57%; pct 0.92; z 1.40; weight 0.10; score 0.92.
  - dollar_volume: raw $1.21B; pct 0.92; z 1.34; weight 0.05; score 0.92.

**Extension**
- Meaning: Stretch/risk control: RSI, ATR, gap size, move-vs-ATR, and position above the 20D low. Higher is less stretched.
- Formula: `0.24 * pct_rank(rsi_control) + 0.24 * (1 - pct_rank(atr_14_pct)) + 0.19 * (1 - pct_rank(stretch_vs_atr)) + 0.14 * (1 - pct_rank(distance_from_20d_low)) + 0.10 * (1 - pct_rank(abs_gap_1d)) + 0.05 * (1 - pct_rank(failed_gap_or_fade)) + 0.05 * (1 - pct_rank(distribution_pressure))`
  - rsi_control: raw 1.00; pct 0.73; z 0.79; weight 0.24; score 0.73.
  - atr_14_pct: raw 4.13%; pct 0.93; z 1.50; weight 0.24; score 0.07.
  - stretch_vs_atr: raw 2.26x; pct 0.90; z 1.16; weight 0.19; score 0.10.
  - distance_from_20d_low: raw 22.63%; pct 0.93; z 1.55; weight 0.14; score 0.07.
  - abs_gap_1d: raw 0.01; pct 0.80; z 0.22; weight 0.10; score 0.20.
  - failed_gap_or_fade: raw 0.00; pct 0.49; z -0.10; weight 0.05; score 0.51.
  - distribution_pressure: raw 0.00; pct 0.38; z -0.57; weight 0.05; score 0.62.

</details>

<details>
<summary><strong>Risk details</strong> - expand for component math</summary>

Risk fields: `score` is the bucket risk from 0 to 1, `weight` is bucket influence, and `contribution` is the weighted risk added to the final score.

**Extension Risk**
- Score 0.33; weight 0.33; contribution 0.11; severity moderate.
- Evidence: RSI 55.31, 5D return 9.3%, 10D return 7.3%, 20D low distance 22.6%
  - rsi_14: raw 55.31; risk score 0.00; range 60.00-80.00.
  - return_5d: raw 9.34%; risk score 0.44; range 0.04-0.16.
  - return_10d: raw 7.25%; risk score 0.00; range 0.08-0.24.
  - return_20d: raw 7.91%; risk score 0.00; range 0.10-0.30.
  - distance_from_20d_low: raw 22.63%; risk score 0.73; range 0.08-0.28.
  - distance_from_20d_high: raw -1.46%; risk score 0.65; range -0.08-0.02.
  - stretch_vs_atr: raw 2.26x; risk score 0.50; range 1.00-3.50.

**Volatility Risk**
- Score 0.14; weight 0.20; contribution 0.03; severity low.
- Evidence: ATR14 4.1%, gap 0.6%, 1D return 1.2%, fade/distribution False/False
  - atr_14_pct: raw 4.13%; risk score 0.43; range 0.02-0.07.
  - abs_gap_1d: raw 0.01; risk score 0.00; range 0.01-0.06.
  - abs_return_1d: raw 0.01; risk score 0.00; range 0.02-0.08.
  - failed_gap_or_fade: raw n/a; risk score n/a; range n/a-n/a.
  - distribution_pressure: raw n/a; risk score n/a; range n/a-n/a.

**Liquidity/Participation Risk**
- Score 0.04; weight 0.20; contribution 0.01; severity low.
- Evidence: tier high, dollar volume $1.2B, 5D volume 1.23x
  - liquidity_tier: raw n/a; risk score 0.00; range n/a-n/a.
  - dollar_volume: raw $1.21B; risk score 0.00; range 5000000.00-100000000.00.
  - volume_ratio_5d: raw 1.23x; risk score 0.00; range 1.50-4.00.
  - volume_persistence_10d: raw 70.00%; risk score 0.17; range 0.20-0.80.

**Trend Failure Risk**
- Score 0.08; weight 0.15; contribution 0.01; severity low.
- Evidence: close vs SMA20 7.0%, SMA 5/20 2.6%, up-day ratio 10D 60.0%, RS decoupling False
  - close_vs_sma_20: raw 6.95%; risk score 0.00; range 0.00-0.08.
  - sma_5_20_ratio: raw 2.57%; risk score 0.00; range 0.00-0.06.
  - up_day_ratio_10d: raw 60.00%; risk score 0.25; range 0.30-0.70.
  - rs_decoupling: raw n/a; risk score n/a; range n/a-n/a.

**Event Risk**
- Score 0.00; weight 0.12; contribution 0.00; severity low.
- Evidence: earnings in -30.94 days
  - upcoming_earnings_days: raw -30.94; risk score 0.00; range n/a-n/a.

</details>

**Setup diagnostics:**
- Best diagnostic setup: trend confirmation with score 0.81.
- trend confirmation: 0.81.
- momentum continuation: 0.76.
- breakout watch: 0.81.
- pullback risk: 0.27.

**Lifecycle and failure diagnostics:**
- Current phase estimate: expansion.
- Regime probabilities: continuation 0.71; mean reversion 0.31; volatility expansion 0.36.
- Phase scores: ignition 0.68; expansion 0.72; euphoria 0.57; exhaustion 0.20; reversal 0.20.
- Failure signals: poor efficiency 0.00; distribution False; fade False; RS decoupling False.
- Note: Heuristic regime probabilities; not yet calibrated to historical forward outcomes.

**Metrics:**
- **Snapshot:** US / S&P 500 / NYSE/Nasdaq; price 284.63; market cap $76.34B.
- **Scores:** rank 0.75; opportunity 0.72; risk 0.16 (low); confidence 0.77.
- **Regime:** bullish regime if conditions persist over 1d-5d; setup trend confirmation.

**Price action:**
- Returns: 1D 1.19%; 5D 9.34%; 10D 7.25%; 20D 7.91%.
- Trend quality: SMA 5/20 2.57%; close vs SMA20 6.95%; up days 5D 80.00%; up days 10D 60.00%.
- Range and volatility: 5D high -1.24%; 5D low 11.62%; 20D high -1.46%; 20D low 22.63%; close location 1D 56.41%; 5D 89.25%; 20D 92.55%; ATR14 4.13%; gap 0.62%; RSI14 55.31; fade flag False.
- Acceleration/failure: momentum acceleration 5.71%; RS momentum 6.82%; RS decoupling False; distribution pressure False.

**Benchmark relative strength:**
- Versus SPY: 1D 0.94%; 5D 7.49%; 10D 6.14%; 20D 2.65%.
- Versus QQQ: 1D 0.82%; 5D 6.01%; 10D 4.68%; 20D -2.66%.
- Versus sector peers: 5D 8.80%; 10D 6.06%; 20D 8.24%.
- Market regime: 0.91 (supportive).

**Volume and liquidity:**
- Relative volume: 5D 1.23x; 20D 1.34x; 5D/20D trend 1.09x.
- Participation evidence: volume z-score 0.88; elevated-volume persistence 5D 80.00%; 10D 70.00%; up/down volume 10D 2.14x.
- Volume quality: acceleration 0.14; price/volume efficiency 7.57%; effort/result 13.20x; distribution days 10D 2.00.
- Liquidity: tier high; dollar volume $1.21B.

**Other context:**
- Upcoming earnings days: -30.94.

**Why it screens well:**
- Trend 0.78: SMA 5/20 2.6%, close vs SMA20 7.0%, 20D close location 92.5%, market regime supportive.
- Momentum 0.91: acceleration 5.7%, 1D 1.2%, 5D close location 89.2%, price/volume efficiency 7.6%.
- Relative strength 0.88: strongest window 5D vs SPY 7.5% (pct n/a); 5D SPY 7.5%, RS momentum 6.8%, 10D sector 6.1%.
- Participation 0.65: volume z-score 0.88, 5D persistence 80.0%, 10D persistence 70.0% (pct 0.93), volume acceleration 0.14, up/down volume 2.14x, efficiency 7.6%, liquidity tier high ($1.2B).
- Extension control 0.29: RSI 55.31, ATR14 4.1%, gap 0.6%, 20D low distance 22.6%, fade/distribution flags False/False.
- Opportunity score is 0.72; risk score is 0.16.
- Factor reason codes: TREND_CONSTRUCTIVE, MOMENTUM_POSITIVE, RELATIVE_STRENGTH_SUPPORTIVE, PARTICIPATION_EXPANDING, EXTENSION_ELEVATED, RSI_CONSTRUCTIVE.

**1-day to 1-week plan:**
- Watch whether the stock continues to outperform SPY/QQQ over the next session.
- Watch whether relative volume stays supportive; fading volume weakens the setup.
- Treat loss of factor support plus fading relative volume as invalidation.

**Main risks:**
- moderate extension risk: RSI 55.31, 5D return 9.3%, 10D return 7.3%, 20D low distance 22.6%
- Risk score is 0.16 (low) on a continuous 0 to 1 scale.

**Verdict:** This is a watchlist candidate for short-term research only; the setup depends on momentum and volume staying intact. Not financial advice.

---

### BBY - Best Buy Co., Inc.
**Setup:** BBY is a momentum continuation candidate based on the current 1-day to 1-week screen. The setup is a conditional market regime, not a standalone price forecast.

**Quick scorecard:**
- **Factor scores:** trend 0.94; momentum 0.99; relative strength 0.99; participation 0.72; extension control 0.11.
- **Read this as:** higher trend/momentum/relative strength/participation is better; higher extension control means less stretched.
- Trend 0.94: SMA 5/20 12.5%, close vs SMA20 28.2%, 20D close location 98.9%, market regime supportive.
- Momentum 0.99: acceleration 8.7%, 1D 4.3%, 5D close location 98.5%, price/volume efficiency 19.2%.
- Relative strength 0.99: strongest window 10D vs SPY 36.4% (pct 1.00); 5D SPY 25.6%, RS momentum 19.7%, 10D sector 36.3%.
- Participation 0.72: volume z-score 2.25, 5D persistence 100.0%, 10D persistence 70.0% (pct 0.93), volume acceleration -0.22, up/down volume 14.00x, efficiency 19.2%, liquidity tier high ($798.7M).
- Extension control 0.11: RSI 84.21, ATR14 3.8%, gap -1.0%, 20D low distance 41.5%, fade/distribution flags False/False.

<details>
<summary><strong>Formula details</strong> - expand for component math</summary>

Component fields: `raw` is the observed value, `pct` is screened-universe percentile, `z` is standard deviations from average, `weight` is formula influence, and `score` is the component score after direction adjustment.

**Trend**
- Meaning: Price structure: longer-window return, short-vs-medium moving average alignment, close vs SMA20, and recent up-day consistency.
- Formula: `0.35 * pct_rank(sma_5_20_ratio) + 0.25 * pct_rank(close_vs_sma_20) + 0.15 * pct_rank(up_day_ratio_10d) + 0.15 * pct_rank(close_location_20d) + 0.10 * pct_rank(market_regime_score)`
  - sma_5_20_ratio: raw 12.50%; pct 0.99; z 3.22; weight 0.35; score 0.99.
  - close_vs_sma_20: raw 28.18%; pct 1.00; z 4.73; weight 0.25; score 1.00.
  - up_day_ratio_10d: raw 90.00%; pct 0.99; z 2.59; weight 0.15; score 0.99.
  - close_location_20d: raw 98.92%; pct 0.98; z 1.61; weight 0.15; score 0.98.
  - market_regime_score: raw 0.91; pct 0.50; z n/a; weight 0.10; score 0.50.

**Momentum**
- Meaning: Recent price movement across 1D, 5D, 10D, and 20D windows.
- Formula: `0.35 * pct_rank(momentum_acceleration_5d_10d) + 0.15 * pct_rank(return_1d) + 0.20 * pct_rank(close_location_5d) + 0.15 * pct_rank(rs_momentum_5d_20d) + 0.15 * pct_rank(price_volume_efficiency_5d)`
  - momentum_acceleration_5d_10d: raw 8.71%; pct 0.99; z 2.62; weight 0.35; score 0.99.
  - return_1d: raw 4.29%; pct 0.96; z 2.02; weight 0.15; score 0.96.
  - close_location_5d: raw 98.53%; pct 0.98; z 1.67; weight 0.20; score 0.98.
  - rs_momentum_5d_20d: raw 0.20; pct 1.00; z 4.25; weight 0.15; score 1.00.
  - price_volume_efficiency_5d: raw 19.20%; pct 0.99; z 3.92; weight 0.15; score 0.99.

**Relative Strength**
- Meaning: Outperformance or underperformance versus SPY and QQQ across multiple windows.
- Formula: `0.25 * pct_rank(rs_momentum_5d_20d) + 0.20 * pct_rank(rel_strength_spy_10d) + 0.15 * pct_rank(rel_strength_qqq_10d) + 0.15 * pct_rank(sector_relative_strength_5d) + 0.15 * pct_rank(sector_relative_strength_10d) + 0.10 * pct_rank(sector_relative_strength_20d)`
  - rs_momentum_5d_20d: raw 0.20; pct 1.00; z 4.25; weight 0.25; score 1.00.
  - rel_strength_spy_10d: raw 36.42%; pct 1.00; z 4.76; weight 0.20; score 1.00.
  - rel_strength_qqq_10d: raw 34.95%; pct 1.00; z 4.76; weight 0.15; score 1.00.
  - sector_relative_strength_5d: raw 26.93%; pct 1.00; z 4.58; weight 0.15; score 1.00.
  - sector_relative_strength_10d: raw 36.34%; pct 1.00; z 4.76; weight 0.15; score 1.00.
  - sector_relative_strength_20d: raw 29.19%; pct 0.97; z 2.64; weight 0.10; score 0.97.

**Participation**
- Meaning: Volume and liquidity support: relative volume, persistence of elevated volume, volume z-score, and dollar volume.
- Formula: `0.14 * pct_rank(volume_acceleration_5d_20d) + 0.14 * pct_rank(volume_ratio_5d) + 0.10 * pct_rank(volume_trend_5d_20d) + 0.14 * pct_rank(volume_persistence_5d) + 0.14 * pct_rank(volume_persistence_10d) + 0.10 * pct_rank(volume_z_score_20d) + 0.10 * pct_rank(up_volume_ratio_10d) + 0.10 * pct_rank(price_volume_efficiency_5d) + 0.05 * pct_rank(dollar_volume)`
  - volume_acceleration_5d_20d: raw -0.22x; pct 0.08; z -0.99; weight 0.14; score 0.08.
  - volume_ratio_5d: raw 1.43x; pct 0.39; z -0.36; weight 0.14; score 0.39.
  - volume_trend_5d_20d: raw 1.65x; pct 0.98; z 2.76; weight 0.10; score 0.98.
  - volume_persistence_5d: raw 100.00%; pct 0.98; z 2.30; weight 0.14; score 0.98.
  - volume_persistence_10d: raw 70.00%; pct 0.93; z 1.62; weight 0.14; score 0.93.
  - volume_z_score_20d: raw 2.25; pct 0.63; z 0.01; weight 0.10; score 0.63.
  - up_volume_ratio_10d: raw 14.00x; pct 1.00; z 7.23; weight 0.10; score 1.00.
  - price_volume_efficiency_5d: raw 19.20%; pct 0.99; z 3.92; weight 0.10; score 0.99.
  - dollar_volume: raw $798,667,874; pct 0.77; z 0.55; weight 0.05; score 0.77.

**Extension**
- Meaning: Stretch/risk control: RSI, ATR, gap size, move-vs-ATR, and position above the 20D low. Higher is less stretched.
- Formula: `0.24 * pct_rank(rsi_control) + 0.24 * (1 - pct_rank(atr_14_pct)) + 0.19 * (1 - pct_rank(stretch_vs_atr)) + 0.14 * (1 - pct_rank(distance_from_20d_low)) + 0.10 * (1 - pct_rank(abs_gap_1d)) + 0.05 * (1 - pct_rank(failed_gap_or_fade)) + 0.05 * (1 - pct_rank(distribution_pressure))`
  - rsi_control: raw 0.20; pct 0.07; z -2.05; weight 0.24; score 0.07.
  - atr_14_pct: raw 3.76%; pct 0.88; z 1.10; weight 0.24; score 0.12.
  - stretch_vs_atr: raw 7.31x; pct 1.00; z 4.06; weight 0.19; score 0.00.
  - distance_from_20d_low: raw 41.47%; pct 0.99; z 3.59; weight 0.14; score 0.01.
  - abs_gap_1d: raw 0.01; pct 0.91; z 0.78; weight 0.10; score 0.09.
  - failed_gap_or_fade: raw 0.00; pct 0.49; z -0.10; weight 0.05; score 0.51.
  - distribution_pressure: raw 0.00; pct 0.38; z -0.57; weight 0.05; score 0.62.

</details>

<details>
<summary><strong>Risk details</strong> - expand for component math</summary>

Risk fields: `score` is the bucket risk from 0 to 1, `weight` is bucket influence, and `contribution` is the weighted risk added to the final score.

**Extension Risk**
- Score 0.96; weight 0.33; contribution 0.32; severity high.
- Evidence: RSI 84.21, 5D return 27.5%, 10D return 37.5%, 20D low distance 41.5%
  - rsi_14: raw 84.21; risk score 1.00; range 60.00-80.00.
  - return_5d: raw 27.47%; risk score 1.00; range 0.04-0.16.
  - return_10d: raw 37.53%; risk score 1.00; range 0.08-0.24.
  - return_20d: raw 28.86%; risk score 0.94; range 0.10-0.30.
  - distance_from_20d_low: raw 41.47%; risk score 1.00; range 0.08-0.28.
  - distance_from_20d_high: raw -0.32%; risk score 0.77; range -0.08-0.02.
  - stretch_vs_atr: raw 7.31x; risk score 1.00; range 1.00-3.50.

**Volatility Risk**
- Score 0.24; weight 0.20; contribution 0.05; severity low.
- Evidence: ATR14 3.8%, gap -1.0%, 1D return 4.3%, fade/distribution False/False
  - atr_14_pct: raw 3.76%; risk score 0.35; range 0.02-0.07.
  - abs_gap_1d: raw 0.01; risk score 0.00; range 0.01-0.06.
  - abs_return_1d: raw 0.04; risk score 0.38; range 0.02-0.08.
  - failed_gap_or_fade: raw n/a; risk score n/a; range n/a-n/a.
  - distribution_pressure: raw n/a; risk score n/a; range n/a-n/a.

**Liquidity/Participation Risk**
- Score 0.04; weight 0.20; contribution 0.01; severity low.
- Evidence: tier high, dollar volume $798.7M, 5D volume 1.43x
  - liquidity_tier: raw n/a; risk score 0.00; range n/a-n/a.
  - dollar_volume: raw $798,667,874; risk score 0.00; range 5000000.00-100000000.00.
  - volume_ratio_5d: raw 1.43x; risk score 0.00; range 1.50-4.00.
  - volume_persistence_10d: raw 70.00%; risk score 0.17; range 0.20-0.80.

**Trend Failure Risk**
- Score 0.00; weight 0.15; contribution 0.00; severity low.
- Evidence: close vs SMA20 28.2%, SMA 5/20 12.5%, up-day ratio 10D 90.0%, RS decoupling False
  - close_vs_sma_20: raw 28.18%; risk score 0.00; range 0.00-0.08.
  - sma_5_20_ratio: raw 12.50%; risk score 0.00; range 0.00-0.06.
  - up_day_ratio_10d: raw 90.00%; risk score 0.00; range 0.30-0.70.
  - rs_decoupling: raw n/a; risk score n/a; range n/a-n/a.

**Event Risk**
- Score 0.00; weight 0.12; contribution 0.00; severity low.
- Evidence: earnings in -2.94 days
  - upcoming_earnings_days: raw -2.94; risk score 0.00; range n/a-n/a.

</details>

**Setup diagnostics:**
- Best diagnostic setup: breakout watch with score 0.91.
- trend confirmation: 0.90.
- momentum continuation: 0.76.
- breakout watch: 0.91.
- pullback risk: 0.29.

**Lifecycle and failure diagnostics:**
- Current phase estimate: expansion.
- Regime probabilities: continuation 0.71; mean reversion 0.27; volatility expansion 0.41.
- Phase scores: ignition 0.67; expansion 0.75; euphoria 0.66; exhaustion 0.09; reversal 0.12.
- Failure signals: poor efficiency 0.00; distribution False; fade False; RS decoupling False.
- Note: Heuristic regime probabilities; not yet calibrated to historical forward outcomes.

**Metrics:**
- **Snapshot:** US / S&P 500 / NYSE/Nasdaq; price 77.95; market cap $16.42B.
- **Scores:** rank 0.75; opportunity 0.79; risk 0.37 (medium); confidence 0.73.
- **Regime:** bullish regime if conditions persist over 1d-5d; setup momentum continuation.

**Price action:**
- Returns: 1D 4.29%; 5D 27.47%; 10D 37.53%; 20D 28.86%.
- Trend quality: SMA 5/20 12.50%; close vs SMA20 28.18%; up days 5D 100.00%; up days 10D 90.00%.
- Range and volatility: 5D high -0.32%; 5D low 27.39%; 20D high -0.32%; 20D low 41.47%; close location 1D 95.84%; 5D 98.53%; 20D 98.92%; ATR14 3.76%; gap -0.99%; RSI14 84.21; fade flag False.
- Acceleration/failure: momentum acceleration 8.71%; RS momentum 19.72%; RS decoupling False; distribution pressure False.

**Benchmark relative strength:**
- Versus SPY: 1D 4.05%; 5D 25.62%; 10D 36.42%; 20D 23.60%.
- Versus QQQ: 1D 3.93%; 5D 24.14%; 10D 34.95%; 20D 18.30%.
- Versus sector peers: 5D 26.93%; 10D 36.34%; 20D 29.19%.
- Market regime: 0.91 (supportive).

**Volume and liquidity:**
- Relative volume: 5D 1.43x; 20D 2.36x; 5D/20D trend 1.65x.
- Participation evidence: volume z-score 2.25; elevated-volume persistence 5D 100.00%; 10D 70.00%; up/down volume 10D 14.00x.
- Volume quality: acceleration -0.22; price/volume efficiency 19.20%; effort/result 5.21x; distribution days 10D 0.00.
- Liquidity: tier high; dollar volume $798,667,874.

**Other context:**
- Upcoming earnings days: -2.94.

**Why it screens well:**
- Trend 0.94: SMA 5/20 12.5%, close vs SMA20 28.2%, 20D close location 98.9%, market regime supportive.
- Momentum 0.99: acceleration 8.7%, 1D 4.3%, 5D close location 98.5%, price/volume efficiency 19.2%.
- Relative strength 0.99: strongest window 10D vs SPY 36.4% (pct 1.00); 5D SPY 25.6%, RS momentum 19.7%, 10D sector 36.3%.
- Participation 0.72: volume z-score 2.25, 5D persistence 100.0%, 10D persistence 70.0% (pct 0.93), volume acceleration -0.22, up/down volume 14.00x, efficiency 19.2%, liquidity tier high ($798.7M).
- Extension control 0.11: RSI 84.21, ATR14 3.8%, gap -1.0%, 20D low distance 41.5%, fade/distribution flags False/False.
- Opportunity score is 0.79; risk score is 0.37.
- Factor reason codes: TREND_CONSTRUCTIVE, MOMENTUM_POSITIVE, RELATIVE_STRENGTH_SUPPORTIVE, PARTICIPATION_EXPANDING, EXTENSION_ELEVATED, RSI_STRETCHED.

**1-day to 1-week plan:**
- Watch whether the stock continues to outperform SPY/QQQ over the next session.
- Watch whether relative volume stays supportive; fading volume weakens the setup.
- Treat loss of factor support plus fading relative volume as invalidation.

**Main risks:**
- high extension risk: RSI 84.21, 5D return 27.5%, 10D return 37.5%, 20D low distance 41.5%
- Risk score is 0.37 (medium) on a continuous 0 to 1 scale.

**Verdict:** This is a watchlist candidate for short-term research only; the setup depends on momentum and volume staying intact. Not financial advice.

---

### A - Agilent Technologies, Inc.
**Setup:** A is a trend confirmation candidate based on the current 1-day to 1-week screen. The setup is a conditional market regime, not a standalone price forecast.

**Quick scorecard:**
- **Factor scores:** trend 0.89; momentum 0.90; relative strength 0.97; participation 0.71; extension control 0.14.
- **Read this as:** higher trend/momentum/relative strength/participation is better; higher extension control means less stretched.
- Trend 0.89: SMA 5/20 6.1%, close vs SMA20 16.5%, 20D close location 87.7%, market regime supportive.
- Momentum 0.90: acceleration 8.2%, 1D 0.1%, 5D close location 85.3%, price/volume efficiency 12.1%.
- Relative strength 0.97: strongest window 10D vs SPY 18.6% (pct 0.97); 5D SPY 16.2%, RS momentum 13.2%, 10D sector 18.5%.
- Participation 0.71: volume z-score 2.25, 5D persistence 80.0%, 10D persistence 60.0% (pct 0.84), volume acceleration 0.15, up/down volume 5.80x, efficiency 12.1%, liquidity tier high ($675.9M).
- Extension control 0.14: RSI 78.65, ATR14 3.5%, gap 0.6%, 20D low distance 25.1%, fade/distribution flags False/False.

<details>
<summary><strong>Formula details</strong> - expand for component math</summary>

Component fields: `raw` is the observed value, `pct` is screened-universe percentile, `z` is standard deviations from average, `weight` is formula influence, and `score` is the component score after direction adjustment.

**Trend**
- Meaning: Price structure: longer-window return, short-vs-medium moving average alignment, close vs SMA20, and recent up-day consistency.
- Formula: `0.35 * pct_rank(sma_5_20_ratio) + 0.25 * pct_rank(close_vs_sma_20) + 0.15 * pct_rank(up_day_ratio_10d) + 0.15 * pct_rank(close_location_20d) + 0.10 * pct_rank(market_regime_score)`
  - sma_5_20_ratio: raw 6.06%; pct 0.93; z 1.40; weight 0.35; score 0.93.
  - close_vs_sma_20: raw 16.52%; pct 0.98; z 2.68; weight 0.25; score 0.98.
  - up_day_ratio_10d: raw 80.00%; pct 0.96; z 1.89; weight 0.15; score 0.96.
  - close_location_20d: raw 87.68%; pct 0.87; z 1.23; weight 0.15; score 0.87.
  - market_regime_score: raw 0.91; pct 0.50; z n/a; weight 0.10; score 0.50.

**Momentum**
- Meaning: Recent price movement across 1D, 5D, 10D, and 20D windows.
- Formula: `0.35 * pct_rank(momentum_acceleration_5d_10d) + 0.15 * pct_rank(return_1d) + 0.20 * pct_rank(close_location_5d) + 0.15 * pct_rank(rs_momentum_5d_20d) + 0.15 * pct_rank(price_volume_efficiency_5d)`
  - momentum_acceleration_5d_10d: raw 8.24%; pct 0.98; z 2.48; weight 0.35; score 0.98.
  - return_1d: raw 0.11%; pct 0.60; z 0.06; weight 0.15; score 0.60.
  - close_location_5d: raw 85.31%; pct 0.84; z 1.26; weight 0.20; score 0.84.
  - rs_momentum_5d_20d: raw 0.13; pct 0.98; z 2.82; weight 0.15; score 0.98.
  - price_volume_efficiency_5d: raw 12.13%; pct 0.96; z 2.39; weight 0.15; score 0.96.

**Relative Strength**
- Meaning: Outperformance or underperformance versus SPY and QQQ across multiple windows.
- Formula: `0.25 * pct_rank(rs_momentum_5d_20d) + 0.20 * pct_rank(rel_strength_spy_10d) + 0.15 * pct_rank(rel_strength_qqq_10d) + 0.15 * pct_rank(sector_relative_strength_5d) + 0.15 * pct_rank(sector_relative_strength_10d) + 0.10 * pct_rank(sector_relative_strength_20d)`
  - rs_momentum_5d_20d: raw 0.13; pct 0.98; z 2.82; weight 0.25; score 0.98.
  - rel_strength_spy_10d: raw 18.55%; pct 0.97; z 2.34; weight 0.20; score 0.97.
  - rel_strength_qqq_10d: raw 17.09%; pct 0.97; z 2.34; weight 0.15; score 0.97.
  - sector_relative_strength_5d: raw 17.53%; pct 0.98; z 2.94; weight 0.15; score 0.98.
  - sector_relative_strength_10d: raw 18.47%; pct 0.97; z 2.34; weight 0.15; score 0.97.
  - sector_relative_strength_20d: raw 17.62%; pct 0.93; z 1.55; weight 0.10; score 0.93.

**Participation**
- Meaning: Volume and liquidity support: relative volume, persistence of elevated volume, volume z-score, and dollar volume.
- Formula: `0.14 * pct_rank(volume_acceleration_5d_20d) + 0.14 * pct_rank(volume_ratio_5d) + 0.10 * pct_rank(volume_trend_5d_20d) + 0.14 * pct_rank(volume_persistence_5d) + 0.14 * pct_rank(volume_persistence_10d) + 0.10 * pct_rank(volume_z_score_20d) + 0.10 * pct_rank(up_volume_ratio_10d) + 0.10 * pct_rank(price_volume_efficiency_5d) + 0.05 * pct_rank(dollar_volume)`
  - volume_acceleration_5d_20d: raw 0.15x; pct 0.20; z -0.66; weight 0.14; score 0.20.
  - volume_ratio_5d: raw 1.49x; pct 0.43; z -0.31; weight 0.14; score 0.43.
  - volume_trend_5d_20d: raw 1.34x; pct 0.94; z 1.60; weight 0.10; score 0.94.
  - volume_persistence_5d: raw 80.00%; pct 0.91; z 1.54; weight 0.14; score 0.91.
  - volume_persistence_10d: raw 60.00%; pct 0.84; z 1.09; weight 0.14; score 0.84.
  - volume_z_score_20d: raw 2.25; pct 0.63; z 0.01; weight 0.10; score 0.63.
  - up_volume_ratio_10d: raw 5.80x; pct 0.97; z 2.46; weight 0.10; score 0.97.
  - price_volume_efficiency_5d: raw 12.13%; pct 0.96; z 2.39; weight 0.10; score 0.96.
  - dollar_volume: raw $675,860,998; pct 0.71; z 0.31; weight 0.05; score 0.71.

**Extension**
- Meaning: Stretch/risk control: RSI, ATR, gap size, move-vs-ATR, and position above the 20D low. Higher is less stretched.
- Formula: `0.24 * pct_rank(rsi_control) + 0.24 * (1 - pct_rank(atr_14_pct)) + 0.19 * (1 - pct_rank(stretch_vs_atr)) + 0.14 * (1 - pct_rank(distance_from_20d_low)) + 0.10 * (1 - pct_rank(abs_gap_1d)) + 0.05 * (1 - pct_rank(failed_gap_or_fade)) + 0.05 * (1 - pct_rank(distribution_pressure))`
  - rsi_control: raw 0.20; pct 0.07; z -2.05; weight 0.24; score 0.07.
  - atr_14_pct: raw 3.49%; pct 0.84; z 0.81; weight 0.24; score 0.16.
  - stretch_vs_atr: raw 5.18x; pct 0.99; z 2.84; weight 0.19; score 0.01.
  - distance_from_20d_low: raw 25.09%; pct 0.94; z 1.82; weight 0.14; score 0.06.
  - abs_gap_1d: raw 0.01; pct 0.81; z 0.26; weight 0.10; score 0.19.
  - failed_gap_or_fade: raw 0.00; pct 0.49; z -0.10; weight 0.05; score 0.51.
  - distribution_pressure: raw 0.00; pct 0.38; z -0.57; weight 0.05; score 0.62.

</details>

<details>
<summary><strong>Risk details</strong> - expand for component math</summary>

Risk fields: `score` is the bucket risk from 0 to 1, `weight` is bucket influence, and `contribution` is the weighted risk added to the final score.

**Extension Risk**
- Score 0.77; weight 0.33; contribution 0.25; severity high.
- Evidence: RSI 78.65, 5D return 18.1%, 10D return 19.7%, 20D low distance 25.1%
  - rsi_14: raw 78.65; risk score 0.93; range 60.00-80.00.
  - return_5d: raw 18.07%; risk score 1.00; range 0.04-0.16.
  - return_10d: raw 19.66%; risk score 0.73; range 0.08-0.24.
  - return_20d: raw 17.29%; risk score 0.36; range 0.10-0.30.
  - distance_from_20d_low: raw 25.09%; risk score 0.85; range 0.08-0.28.
  - distance_from_20d_high: raw -2.74%; risk score 0.53; range -0.08-0.02.
  - stretch_vs_atr: raw 5.18x; risk score 1.00; range 1.00-3.50.

**Volatility Risk**
- Score 0.10; weight 0.20; contribution 0.02; severity low.
- Evidence: ATR14 3.5%, gap 0.6%, 1D return 0.1%, fade/distribution False/False
  - atr_14_pct: raw 3.49%; risk score 0.30; range 0.02-0.07.
  - abs_gap_1d: raw 0.01; risk score 0.00; range 0.01-0.06.
  - abs_return_1d: raw 0.00; risk score 0.00; range 0.02-0.08.
  - failed_gap_or_fade: raw n/a; risk score n/a; range n/a-n/a.
  - distribution_pressure: raw n/a; risk score n/a; range n/a-n/a.

**Liquidity/Participation Risk**
- Score 0.08; weight 0.20; contribution 0.02; severity low.
- Evidence: tier high, dollar volume $675.9M, 5D volume 1.49x
  - liquidity_tier: raw n/a; risk score 0.00; range n/a-n/a.
  - dollar_volume: raw $675,860,998; risk score 0.00; range 5000000.00-100000000.00.
  - volume_ratio_5d: raw 1.49x; risk score 0.00; range 1.50-4.00.
  - volume_persistence_10d: raw 60.00%; risk score 0.33; range 0.20-0.80.

**Trend Failure Risk**
- Score 0.00; weight 0.15; contribution 0.00; severity low.
- Evidence: close vs SMA20 16.5%, SMA 5/20 6.1%, up-day ratio 10D 80.0%, RS decoupling False
  - close_vs_sma_20: raw 16.52%; risk score 0.00; range 0.00-0.08.
  - sma_5_20_ratio: raw 6.06%; risk score 0.00; range 0.00-0.06.
  - up_day_ratio_10d: raw 80.00%; risk score 0.00; range 0.30-0.70.
  - rs_decoupling: raw n/a; risk score n/a; range n/a-n/a.

**Event Risk**
- Score 0.00; weight 0.12; contribution 0.00; severity low.
- Evidence: earnings in -3.62 days
  - upcoming_earnings_days: raw -3.62; risk score 0.00; range n/a-n/a.

</details>

**Setup diagnostics:**
- Best diagnostic setup: trend confirmation with score 0.86.
- trend confirmation: 0.86.
- momentum continuation: 0.74.
- breakout watch: 0.86.
- pullback risk: 0.30.

**Lifecycle and failure diagnostics:**
- Current phase estimate: expansion.
- Regime probabilities: continuation 0.72; mean reversion 0.30; volatility expansion 0.41.
- Phase scores: ignition 0.72; expansion 0.72; euphoria 0.65; exhaustion 0.15; reversal 0.16.
- Failure signals: poor efficiency 0.00; distribution False; fade False; RS decoupling False.
- Note: Heuristic regime probabilities; not yet calibrated to historical forward outcomes.

**Metrics:**
- **Snapshot:** US / S&P 500 / NYSE/Nasdaq; price 135.53; market cap $38.25B.
- **Scores:** rank 0.75; opportunity 0.76; risk 0.29 (medium); confidence 0.74.
- **Regime:** bullish regime if conditions persist over 1d-5d; setup trend confirmation.

**Price action:**
- Returns: 1D 0.11%; 5D 18.07%; 10D 19.66%; 20D 17.29%.
- Trend quality: SMA 5/20 6.06%; close vs SMA20 16.52%; up days 5D 100.00%; up days 10D 80.00%.
- Range and volatility: 5D high -2.74%; 5D low 19.58%; 20D high -2.74%; 20D low 25.09%; close location 1D 51.46%; 5D 85.31%; 20D 87.68%; ATR14 3.49%; gap 0.64%; RSI14 78.65; fade flag False.
- Acceleration/failure: momentum acceleration 8.24%; RS momentum 13.21%; RS decoupling False; distribution pressure False.

**Benchmark relative strength:**
- Versus SPY: 1D -0.14%; 5D 16.22%; 10D 18.55%; 20D 12.03%.
- Versus QQQ: 1D -0.26%; 5D 14.74%; 10D 17.09%; 20D 6.72%.
- Versus sector peers: 5D 17.53%; 10D 18.47%; 20D 17.62%.
- Market regime: 0.91 (supportive).

**Volume and liquidity:**
- Relative volume: 5D 1.49x; 20D 2.00x; 5D/20D trend 1.34x.
- Participation evidence: volume z-score 2.25; elevated-volume persistence 5D 80.00%; 10D 60.00%; up/down volume 10D 5.80x.
- Volume quality: acceleration 0.15; price/volume efficiency 12.13%; effort/result 8.24x; distribution days 10D 1.00.
- Liquidity: tier high; dollar volume $675,860,998.

**Other context:**
- Upcoming earnings days: -3.62.

**Why it screens well:**
- Trend 0.89: SMA 5/20 6.1%, close vs SMA20 16.5%, 20D close location 87.7%, market regime supportive.
- Momentum 0.90: acceleration 8.2%, 1D 0.1%, 5D close location 85.3%, price/volume efficiency 12.1%.
- Relative strength 0.97: strongest window 10D vs SPY 18.6% (pct 0.97); 5D SPY 16.2%, RS momentum 13.2%, 10D sector 18.5%.
- Participation 0.71: volume z-score 2.25, 5D persistence 80.0%, 10D persistence 60.0% (pct 0.84), volume acceleration 0.15, up/down volume 5.80x, efficiency 12.1%, liquidity tier high ($675.9M).
- Extension control 0.14: RSI 78.65, ATR14 3.5%, gap 0.6%, 20D low distance 25.1%, fade/distribution flags False/False.
- Opportunity score is 0.76; risk score is 0.29.
- Factor reason codes: TREND_CONSTRUCTIVE, MOMENTUM_POSITIVE, RELATIVE_STRENGTH_SUPPORTIVE, PARTICIPATION_EXPANDING, EXTENSION_ELEVATED, RSI_STRETCHED.

**1-day to 1-week plan:**
- Watch whether the stock continues to outperform SPY/QQQ over the next session.
- Watch whether relative volume stays supportive; fading volume weakens the setup.
- Treat loss of factor support plus fading relative volume as invalidation.

**Main risks:**
- high extension risk: RSI 78.65, 5D return 18.1%, 10D return 19.7%, 20D low distance 25.1%
- Risk score is 0.29 (medium) on a continuous 0 to 1 scale.

**Verdict:** This is a watchlist candidate for short-term research only; the setup depends on momentum and volume staying intact. Not financial advice.

---
