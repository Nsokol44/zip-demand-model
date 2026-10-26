# Design note — ECRA strengthening program (written before any run)

**Date:** 2026-10-26. **Status:** This note is written before any of the
runs below are executed. Seeds, draw counts, estimators, and success
criteria are fixed here, ex ante. Any deviation discovered necessary
during implementation is appended to the deviation log at the end of
this note, with its reason, before the affected results are used.

**Program.** Per the approved strengthening plan (Nick, 2026-10-26):
(a) a fifth Tier 2 outcome — ZBP electronic-shopping establishments —
run through the identical Tier 2 protocol plus the Bayesian layer,
closing the "Tier 2 Bayesian fits not run" gap for this outcome;
(b) adjusted-maximum-likelihood Fay–Herriot variance estimators
against the shipped plug-in; (c) a simulated second wave testing the
paper's claim that a second wave would identify the (size, sigma2_u)
split; (d) Tier 1 rerun at 4 percent and 16 percent sampling.

---

## Phase 0 verdict (feasibility of the new outcome) — FEASIBLE

Verified 2026-10-26 against the study's own ZBP 2022 detail file
(`zbp22detail.zip`, Census Bureau, County Business Patterns datasets
page, downloaded 2026-10-26 into the replication data directory; the
study previously held only the ZBP totals files):

- **Code.** NAICS 454110 (electronic shopping and mail-order houses)
  is present. ZBP 2022 is published on the 2017 NAICS vintage, so no
  NAICS-2022 successor code is needed; NAICS 449210 does not appear
  in the file. 5,914 ZIP rows nationally carry the code.
- **Coverage.** Of the 5,576 study ZCTAs, 1,712 (30.7 percent) have at
  least one electronic-shopping establishment; the study frame holds
  14,620 such establishments in total (median 6 among ZCTAs with any,
  maximum 102). Mapped to counties, 266 of 577 study counties (46.1
  percent) contain at least one.
- **Sparsity, stated plainly.** 69.3 percent of study ZCTAs record
  zero electronic-shopping establishments. The outcome is a small
  non-negative integer count, not a continuous rate; its zero share
  and discreteness are properties of the measure and are reported as
  such wherever the outcome is used.
- **Suppression.** The establishment total (`est`) is published for
  every 454110 row (no suppressed or non-numeric values in 5,914
  rows). Employment-size-class cells are suppressed ("N") in 21.0
  percent of rows; the benchmark uses only the establishment total,
  so that suppression does not touch the outcome.
- **Denominator.** Establishments per household uses the same ACS
  2023 household counts, over the same 5,576 ZCTAs, as the three
  existing Tier 2 outcomes, and is graded on the same log-rate scale.

**Framing (endorsed by Nick, 2026-10-26, verbatim):** "As long as
it's got real data and changes the paper from just simulation to
credible result we are in a better position." The outcome's role is
therefore fixed as follows. It is the paper's first fully OBSERVED
e-commerce outcome: observed Census counts of electronic-shopping
establishments per household. It is graded on the identical Tier 2
protocol as the four existing evaluations. It is NOT seller sales,
not transactions, and not demand for any product, and no text
produced under this program may describe it as such. Its sparsity is
not softened in the write-up, and what the measure proves is not
inflated: it benchmarks the estimation machinery on the observed
geography of electronic-shopping presence, nothing more.

---

## Test (a) — the new outcome through Tier 2 and the Bayesian layer

**Outcome.** `zbp22_eshop`: NAICS 454110 establishment counts from
ZBP 2022 detail, aligned to the 5,576 study ZCTAs. A ZCTA with no
454110 row has an observed count of zero (the code is absent because
no establishment is recorded, not because the value is missing);
the outcome-present mask is presence in the ZBP 2022 totals file,
exactly as for the totals outcome.

**Econometric arm.** The Tier 2 benchmark of record
(`benchmark.fit_architecture` / `benchmark.evaluate`, unmodified),
replicated over the same 24 sample draws as the existing Tier 2
outcomes (draw r mask from `layer1.simulate_truth` under seed
20261013 + 1000*r, steamers mask; replicate 0 reproduces the
canonical 447-area sample). Layers graded: OLS, best spatial model
(AIC), Fay–Herriot, GeoAI. Metrics identical to Table 7: held-out
RMSE (log-rate scale), Spearman, top-decile overlap, Fay–Herriot
interval behaviour against the observed log rate, layer agreement.

**Bayesian arm.** The Bayesian layer of Section 6 fitted to this
outcome on the same 24 draws and masks, by the shipped machinery
(`run_bayes_experiments.do_bayes_fit`, eigen-truncated ICAR top-300,
priors of BAYES_DESIGN.md unchanged, replicate seed 20261013 +
1000*r), graded on held-out ZCTAs against the observed log rate with
the Section 6 Tier 2 grading (RMSE, interval behaviour, mean width).
Engineering rule inherited from BAYES_DESIGN.md: draw 0 is timed
first; if a fit exceeds 15 minutes, the run stops and the blocker is
reported rather than silently redesigning the layer.

**Pre-stated questions (no pass/fail gate; reported as measured).**
(Q1) Does the GeoAI-versus-Fay–Herriot paired ordering found on the
other real outcomes repeat on this one (share of 24 draws in which
GeoAI's held-out RMSE is lower)? (Q2) Where does the Bayesian
layer's held-out RMSE sit relative to the econometric layers'
near-tie band on this outcome (the criterion C3 comparison, applied
to this evaluation)? (Q3) What is the Fay–Herriot and Bayesian
interval behaviour against this sparse, discrete target?

## Test (b) — adjusted-maximum-likelihood Fay–Herriot variances

**Question.** Section 5.4's under-coverage traces to the weakly
identified (size, sigma2_u) split and to where the shipped variance
construction lands on that ridge. Li and Lahiri (2010) and
Yoshimori and Lahiri (2014) propose adjusted maximum likelihood
(AML) estimators of the Fay–Herriot area variance built to avoid
the boundary pathology (sigma-hat2_u = 0) of ML-type estimators.
This test asks whether an AML variance estimator, swapped into the
shipped construction, changes the interval behaviour.

**Pre-coding verification step.** Before any AML code is written,
the adjustment terms are taken from the papers themselves and the
bibliographic details of both papers are verified for the
reference list. The implementation is checked against any worked
example or simulation table in the papers that can be reproduced.

**Design (b1, estimator swap, primary).** For each of the 24 Tier 1
draws and both products, take the shipped stage's own inputs on the
sampled areas: direct estimates y_i (log rate), model predictions
from the best spatial model, sampling variances psi_i from the
shipped joint fit, and the shipped parameter-uncertainty term.
Hold every element fixed and replace only sigma2_u, estimated from
the residuals e_i = y_i - pred_i with psi_i treated as known, by:
(i) the shipped value (baseline); (ii) profile maximum likelihood;
(iii) the Li and Lahiri (2010) AML estimator; (iv) the Yoshimori
and Lahiri (2014) AML estimator. Intervals are then rebuilt in the
shipped form (gamma_i = sigma2_u/(sigma2_u + psi_i);
var = gamma_i * psi_i + the shipped parameter-uncertainty term;
nominal 95 percent) and graded against the DGP truth on sampled
areas, exactly as Section 5.4 grades the shipped intervals.

**Design (b2, textbook refit, secondary).** The classical
area-level Fay–Herriot model refit on the sampled areas with
regression coefficients profiled by GLS (design matrix [1, Z],
psi_i known), sigma2_u by ML, REML, and both AML estimators,
EBLUP intervals from the g1 term only. Reported as a robustness
panel, because the AML positivity theory is stated for this model.

**Pre-stated criteria.** An AML estimator is said to address the
boundary pathology in this design if (C-b1) its sigma-hat2_u is
strictly positive in all 24 draws for both products (Tier 1, b1),
and (C-b2) its mean sampled-area coverage is at least as close to
95 percent as the shipped plug-in's, for both products. Both
criteria, and every estimator's numbers, are reported whether or
not they are met. The same swap is then applied to the Tier 2
evaluations (the four existing outcomes and, under test (a), the
new one): per draw, held-out interval behaviour per estimator,
reported as draw means with the share of draws in which each
estimator's behaviour is closest to 95 percent. No criterion is
attached to the Tier 2 panel; it is behaviour against noisy targets.

## Test (c) — a simulated second wave

**Claim under test.** Sections 5.4, 7, and 8 state that a second
test wave (or split-window replication) would identify the
(size, sigma2_u) split directly, because repeated counts per area
separate count noise, which is independent across waves, from the
shared area effect. This test simulates exactly that design.

**Construction.** For each of the 24 draws and both products: the
draw's true surface and sampled areas are the shipped ones. Wave 1
counts are the shipped counts. Wave 2 counts are fresh
Negative Binomial draws at the same sampled areas from the same
true rates (mean = households x true rate, size = 6.0), drawn from
a dedicated random stream seeded 20261013 + 1000*r + 7,000,000.
Three fits of the shipped joint model (Negative Binomial size and
lognormal area effect, Gauss–Hermite quadrature, three starts) are
compared: wave 1 only (the shipped fit); wave 2 only; and pooled,
in which the likelihood integrates the SAME area effect v_i over
both waves' counts (the identifying structure the claim rests on).

**Measurements.** (M1) Size recovery: |log(size-hat / 6.0)|, mean
across draws, pooled versus wave 1 only. (M2) Ridge sharpness: the
drop in maximised log-likelihood when size is fixed at 0.5x and at
2x the fitted value (tau free), averaged; a larger drop is a
sharper split. (M3) Coverage consequence: nominal 95 percent
Fay–Herriot intervals for the sampled areas built from the pooled
split and graded on the wave 2 counts against the truth, versus
intervals built from the wave-1 split graded on the same wave 2
counts.

**Pre-stated verdict rule.** The claim is SUPPORTED if all three
move the right way on the draw means, for both products: size
recovery improves (M1 falls), the ridge sharpens (M2 rises), and
wave-2 sampled-area coverage under the pooled split is closer to
95 percent than under the wave-1 split (M3). If any component
fails for either product, the verdict is NOT SUPPORTED AS STATED,
and the manuscript language is revised to match whichever
components held. All components are reported regardless.

## Test (d) — Tier 1 at 4 percent and 16 percent sampling

**Design.** The Tier 1 calibration protocol of record
(`calibration.py`: 24 replicates, seeds 20261013 + 1000*r, both
products, parametric-bootstrap calibration with 25 worlds per
replicate, Moran and LM diagnostics, AIC model choice) rerun
verbatim with the sampling fraction set to 0.04 and to 0.16. The
8 percent numbers of record are the shipped calibration results;
no re-run of 8 percent is needed or permitted to substitute for
them.

**Pre-stated reporting.** For each fraction: raw and calibrated
coverage on sampled and all areas, the bootstrap multiplier,
diagnostic rejection rates, Fay–Herriot and GeoAI-comparable RMSEs
as the protocol produces them, tabulated beside the 8 percent
values. No pass/fail criterion attaches; the question answered is
how the three Section 5 pathologies scale with the sampling
fraction, including whether the Bayesian protocol fractions
limitation in Section 8 (the Bayesian layer at 4 and 16 percent
was designed but not run) is narrowed for the econometric core.
(The Bayesian layer itself is not rerun at the new fractions under
this program; the limitation is narrowed, not closed, and the
manuscript will say so.)

---

## Global rules

- **Seeds.** Master seed 20261013 throughout. Replicate seeds
  20261013 + 1000*r (r = 0..23). Wave-2 stream offset +7,000,000.
  Bootstrap worlds spawned from the replicate seed exactly as in
  `calibration.py`.
- **Outputs.** Per-draw records for every test, saved as written;
  summaries as strict JSON (NaN serialised as null); every run
  one-command rerunnable and deterministic; run logs retained.
- **Results memos.** One memo per test (a)–(d), filed in this
  package, reporting the pre-stated questions and criteria first
  and any additional observation second, labelled as such.
- **Sequencing.** Tests may run in any order, but no manuscript
  text is edited under this note; manuscript integration is a
  separate phase gated on the all-writing checker audit.
- **Claims discipline.** The new outcome is described only as
  observed Census counts of electronic-shopping establishments
  per household. The AML and second-wave verdicts are reported
  under the criteria above, met or not.

## Deviation log

- D1 (2026-10-26, Test D): the `pooled` block of `test_d_frac4.json` (and of
  `test_d_frac16.json` when written) is null. `s2d_fractions.py` aggregated
  with flat key names that do not match the nested record structure returned
  by `calibration.one_replicate`. The per-replicate records are complete;
  all pooled statistics in Memo D and in the manuscript were computed post
  hoc from those records. No compute was redone and no number comes from
  the null block.
- D2 (2026-10-26, Test D): the calibration protocol's replicate function
  returns no RMSEs, so Test D reports coverage, calibration multipliers,
  diagnostic rejection rates, size-hat, and sigma2_u by fraction, and no
  RMSE-by-fraction. Stated in Memo D and in the manuscript's Section 5.4
  passage.
- D3 (2026-10-26, Test A reporting): the observed-zero share of the
  electronic-shopping outcome is 68.0% of the frame (3,790 of 5,576 ZCTAs;
  1,712 with at least one establishment; 74 with no ZBP record at all,
  graded as missing). An early drafting figure of 69.3%, which counted the
  74 no-record ZCTAs as zeros, appeared in draft Sections 4.6, 5.7, and 8
  and in Memo A; all instances were corrected to 68.0% on 2026-10-26
  against the loader's own counts (`run_a_econ.log`: present=5502,
  nonzero=1712, zero_share=0.680).
