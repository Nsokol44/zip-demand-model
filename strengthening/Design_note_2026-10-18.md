# Strengthening analyses — design and pre-stated questions

Written 2026-10-18 **before any strengthening analysis was run** (the only
results in existence at this point are the canonical pipeline's, in
`~/workspace/zip-demand-model/results/model_metrics.json`). Nick's directive
of 2026-10-18: rectify every fixable editor/referee concern; add freely
available real data as a second validation tier; keep the simulation study
in full; write an explicit comparison between the tiers into the paper.

## The two-tier validation design

- **Tier 1 — simulation recovery (existing, unchanged).** Known ground
  truth over 5,576 real ZCTA geographies (Southeast + NYC metro, ACS 2023
  covariates): bias, coefficient and parameter recovery, interval coverage
  against truth, failure modes. Canonical numbers are the shipped ones
  (seed 20261013); they are not re-run or altered.
- **Tier 2 — empirical benchmark (new).** The same architecture (Layer 1
  spatial-econometric suite + Fay–Herriot stage, Layer 2 gradient boosting
  with identical leakage controls and GBM parameters), fit on a sparse
  "observed" subset of ZCTAs and graded **out-of-sample against observed
  outcomes** in the held-out remainder. There is no ground truth in Tier 2:
  only relative out-of-sample performance can be reported — no recovery,
  bias, or calibration claims. Tier 2 is an empirical benchmark of the
  machinery on observed outcomes. It is **not** a market validation of the
  planned storefront demand test: the benchmark outcomes are public
  economic-activity counts, not purchases of the slate products.

## Tier 2 data (all free, public, no key)

1. **ZIP Code Business Patterns (ZBP), U.S. Census Bureau** — total
   establishments per ZIP, 2022 (primary outcome: log establishments per
   household, +0.5 correction, matching the pipeline's rate convention)
   and 2019 (secondary temporal-transfer check, pre-planned below).
2. **IRS Statistics of Income (SOI) ZIP Code Data, tax year 2022** —
   count of individual income-tax returns per household (secondary
   outcome; same rate construction). If a clean, documented count of
   returns with business/professional net income exists in the file
   layout, it is reported as an additional outcome; otherwise returns
   filed stands alone.
3. Covariates, geography, spatial weights: the pipeline's existing
   ACS 2023 frame and weights, unchanged.

ZIP codes in ZBP/SOI are merged to study ZCTAs on the 5-digit code (the
usual convention; ZBP ZIPs that lack a study-ZCTA row and study ZCTAs
that lack an outcome row are counted and reported, and ZCTAs without an
outcome are excluded from fitting and grading).

## Tier 2 protocol (pre-stated)

- **Observed subset:** exactly the ZCTAs the simulation designates as
  sampled for the demo product (steamers) in the canonical run
  (`results/observed_sample.csv`), so the two tiers observe the same
  areas. Areas whose benchmark outcome is missing drop out of fitting
  and are counted.
- **Estimators:** pipeline code, unchanged (`layer1_econometrics`,
  `layer2_geoai` feature construction and GBM parameters). Model choice
  by AIC, as in Tier 1. The Fay–Herriot stage runs on the count outcome
  with household exposure, exactly as in Tier 1.
- **Uptake target:** Tier 2 has no session/add-to-cart analogue in these
  sources, so the GeoAI uptake model is **not** assessed in Tier 2. This
  is stated in the paper; the uptake result remains Tier-1-only evidence.
- **Pre-stated metrics** (held-out ~92% only): RMSE and MAE on the
  log-rate scale; Spearman rank correlation of predictions vs. observed
  outcomes; top-decile overlap of predictions vs. observed outcomes;
  Layer-1-vs-Layer-2 agreement (Pearson, Spearman, top-decile overlap);
  Fay–Herriot nominal-95% interval coverage **against observed held-out
  log rates**, reported with the standing caveat that observed rates
  carry their own measurement noise, so this is interval *behaviour* on
  real data, not true coverage.
- **Temporal-transfer check (pre-planned secondary):** fit the same
  protocol on ZBP 2019 outcomes (same observed subset), predict all
  ZCTAs, and grade against ZBP 2022 observed outcomes. Reported with the
  same metrics; no tuning is done between the cross-sectional and
  temporal runs.
- **Diagnostics (for concordance question (c)):** Moran's I (seeded
  permutation, pipeline function) and Anselin–Bera LM error / LM lag
  tests (plus robust forms) on the Tier 2 sample's OLS residuals, and the
  Layer 1 AIC model choice on real data.

## Concern 2 — Fay–Herriot interval calibration (simulation study)

Across R replicate DGP draws (both products; replicate seeds
20261013 + 1000·r, documented in the run script), each replicate refits
the pipeline exactly as shipped and records nominal-95% coverage against
its own truth. The remedy assessed is **parametric-bootstrap calibration
of the interval half-width**, in the spirit of Prasad–Rao bootstrap MSE
estimation: from each replicate's fitted Fay–Herriot model (fitted model
predictions, fitted NegBin size, fitted area variance), B bootstrap
worlds are drawn for the sampled areas; the Fay–Herriot stage is re-run
in each; the half-width multiplier needed for the bootstrap intervals to
cover the bootstrap latent rates at 95% is computed per replicate as the
95th percentile of |latent − estimate| / half-width pooled over
bootstrap worlds and areas; that multiplier is then applied to the
replicate's real intervals and coverage against the DGP truth is
re-measured. Reported: coverage before vs. after, per product and
pooled; the distribution of multipliers. No remedy parameter is tuned
against the DGP truth — the multiplier is estimated entirely inside the
bootstrap world.

## Concern 3 — diagnostic power (integrated into the same replicates)

In each calibration replicate, Moran's I (permutation) and the LM error /
LM lag tests (asymptotic) are computed on the OLS residuals of the
simulated sample, and rejection rates at 5% are reported per product,
alongside the AIC model choices. This measures whether the classical LM
specification search would have detected the spatial process in the
realizations where Moran's I did not. The same diagnostics on Tier 2
real data feed concordance question (c).

## Pre-stated concordance questions (Tier 1 vs. Tier 2)

Recorded before any Tier 2 or calibration run:

- **(a) Layer rankings.** Tier 1 found Layer 1 (post-shrinkage) beats the
  GeoAI layer on point prediction (recovery RMSE 0.512/0.529 vs.
  0.606/0.665) while the layers agree on rankings (top-decile overlap
  86–87%), and GeoAI recovers uptake near-exactly (Tier-1-only; Tier 2
  cannot test uptake). Question: on observed outcomes, does Layer 1
  again beat Layer 2 on out-of-sample point prediction, and does the
  layers' ranking agreement stay in the same range?
- **(b) Interval behaviour.** Tier 1 found product-dependent Fay–Herriot
  mis-coverage traced to the weakly identified (NegBin size, σ²u) split
  (steamers 83.7% all-area / trio 97.4% all-area, 82.8% sampled).
  Question: does nominal-95% interval behaviour against observed
  held-out rates on real data echo under-coverage, over-coverage, or
  neither — and does the fitted split on real data land in the same
  unstable pattern (implausible size estimates)?
- **(c) Diagnostic failure modes.** Tier 1 found Moran's I on OLS
  residuals can miss a strong spatial error process at an 8% sampling
  fraction (steamers: I = 0.062, p = 0.541 under ρ = 0.55) while AIC
  still prefers a spatial model. Question: on real data, do the
  diagnostics and the AIC choice tell the same story or different ones,
  and do the LM tests detect spatial structure in the realizations
  (simulation) and the sample (real data) where Moran's I does not?

Agreement and disagreement are both reportable results. Disagreement
diagnoses which simulation assumptions fail to transport to observed
data; that diagnosis is itself a finding and will be written as one.

## Dataset exclusion (recorded 2026-10-18)

HUD–USPS vacancy / no-stat data were considered as a candidate
outcome source and EXCLUDED before any use: HUD's aggregated USPS
vacancy data are released at census-tract level only, under
registered HUD User access with a USPS sublicense and stated-purpose
restrictions — neither ZIP-level nor freely reproducible, so building
Tier 2 on them would break the one-command reproducibility rule. No
HUD vacancy data were downloaded or used at any point in this build.
Tier 2 rests solely on (i) Census ZIP Code Business Patterns totals
(2022, 2019) and (ii) IRS Statistics of Income ZIP Code Data, tax
year 2022 — both public, no registration. SOI is framed throughout
as observed economic mass at ZIP level, not observed product demand.
(The public HUD ZIP Crosswalk was not needed; the ZIP→ZCTA identity
join on the 5-digit code sufficed for both sources.)
