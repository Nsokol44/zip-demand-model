# Memo — Test A: Tier 2 on an observed e-commerce outcome (ZBP electronic shopping)

Date: 2026-10-26. Design: `ecra/DESIGN_NOTE_STRENGTHENING_2026-10-26.md` (Test A, stated before
any run). Code: `ecra/strengthening/code/s2a_econ.py`, `s2a_bayes.py`. Results:
`ecra/strengthening/results/test_a_econ.json`, `test_a_predictions.csv`, `test_a_bayes.json`.
Feasibility: `ecra/ZBP_FEASIBILITY_2026-10-26.md` (verdict: feasible with caveats; the outcome is
constructible only from the NAICS-2017-vintage ZBP files the study already archives).

## The outcome

Electronic-shopping and mail-order-house establishments (NAICS 454110) per household, ZBP 2022
detail file (`zbp22detail.zip`, Census CBP 2022 directory, downloaded 2026-10-26; 2,108,262 data
rows). Frame: the study's 5,576 ZCTAs. 14,620 establishments in total; 1,712 ZCTAs (30.7%) have at
least one; **68.0% of ZCTAs record zero** (3,790 of 5,576). This is the Tier 2 benchmark's first fully OBSERVED
e-commerce outcome. It measures establishment presence only, never sales or transactions, and the
manuscript says so wherever the outcome is reported. Loader caveat (from the feasibility scout,
implemented in `loaders.zbp22_eshop`): a ZCTA with no 454110 row in the detail file is an observed
zero, not missing; ZCTAs absent from ZBP 2022 entirely are NaN (74 of them, outside the graded
set). Graded (held-out, covariates known) ZCTAs per draw: mean 5,061, range 5,057–5,067.

## Econometric arm (24 draws, seeds 20261013 + 1000r) — complete

Held-out RMSE on the log-rate scale, draw means ± sd:

| Estimator | RMSE | Spearman | Top-decile overlap |
|---|---|---|---|
| OLS | 1.010 ± 0.008 | 0.281 ± 0.018 | 0.273 ± 0.020 |
| Best spatial (AIC; SEM 67%, SAR 33%) | 1.012 ± 0.013 | 0.280 ± 0.018 | 0.272 ± 0.020 |
| Fay–Herriot | 1.012 ± 0.013 | 0.280 ± 0.018 | 0.272 ± 0.020 |
| GeoAI | **0.944 ± 0.009** | **0.501 ± 0.013** | **0.306 ± 0.021** |

The Fay–Herriot point estimates equal the selected spatial model's predictions on held-out areas
by construction; the arms differ only through sampled areas and intervals. Fay–Herriot interval
behaviour against the noisy observed target: 0.296 ± 0.065 (the collapse analysed in Test B).
Fitted σ²u averages 0.028 (range 0.020–0.168); mean shrinkage weight γ = 0.023; NB size-hat mean
0.431.

**Q1 (pre-stated): does the GeoAI-below-Fay–Herriot RMSE ordering of the other four Tier 2
evaluations repeat on the observed e-commerce outcome?** YES. GeoAI's held-out RMSE is below
Fay–Herriot's in **24 of 24 draws** (share 1.0); mean paired margin **0.068 ± 0.012** (smallest
0.047), the widest margin of any Tier 2 evaluation. On ranking quality the gap is also the widest
in the benchmark (Spearman 0.501 vs 0.280; top-decile overlap 0.306 vs 0.272). FH–GeoAI top-decile
agreement falls to 0.298 ± 0.046, against 0.50–0.52 on the other real outcomes and 0.86–0.87 in
Tier 1. The Tier 1 ordering again does not transport, and on this outcome the reversal is
unanimous across draws.

## Bayesian arm (24 draws) — complete

`s2a_bayes.py` (the shipped `FitBayes` protocol: BYM2-type prior under the top-300 eigenvector
approximation, MCMC, convergence gates with one 2,000-tuning re-run, graded on the same 24 draws)
was run for draws 0–9 on the project VM and for draws 10–23 on the author's machine under the
identical shipped protocol (4,000 posterior draws per fit; gates at maximum split R-hat ≤ 1.01
and bulk ESS ≥ 400 on the gated parameters). The returned files were verified before integration:
every record in `test_a_bayes.json` matches its per-draw fit file and grading file exactly, for
all 24 draws and all nine reported fields, and the per-draw fits carry the same protocol markers
(`n_draws` 4000, `prior_variant` primary, the same field parameterisation). Fit files, grading
files, and predictions for draws 10–23 are integrated alongside the stored draws 0–9 in
`ijec-adaptation/results/`, with sizes and SHA-256 hashes in
`results/INTEGRATION_MANIFEST_BAYES_2026-10-26.json`. Full verdict computations are in
`results/test_a_bayes_verdicts.json`.

Held-out performance on the log-rate scale, draw means ± sd (sd as stored, ddof = 0):

| Metric | Bayesian layer | Fay–Herriot (same draws) | GeoAI (same draws) |
|---|---|---|---|
| RMSE | **1.969 ± 0.206** (range 1.671–2.416) | 1.012 ± 0.013 | 0.944 ± 0.009 |
| Spearman | −0.033 ± 0.017 | 0.280 ± 0.018 | 0.501 ± 0.013 |
| Top-decile overlap | 0.226 ± 0.016 | 0.272 ± 0.020 | 0.306 ± 0.021 |
| Interval behaviour vs observed | 0.495 ± 0.065 | 0.296 ± 0.065 | — |
| Mean interval width | 2.829 ± 0.655 | 0.841 ± 0.192 | — |

Convergence gates pass in **6 of 24** fits (draws 0, 2, 17, 18, 19, 22), a better rate than the
Tier 1 products (1 of 24 and 0 of 24) but still a minority.

**Q2 (pre-stated): does the Bayesian layer's held-out RMSE fall inside the econometric near-tie
band of 1.010–1.012?** NO, decisively. The layer is worse than Fay–Herriot in **24 of 24 draws**
(mean paired difference **+0.956 ± 0.201**, smallest +0.640) and worse than GeoAI in 24 of 24
draws (+1.024 on average). Even its best draw (1.671) sits far above the band. Its rankings carry
no signal on this outcome (Spearman −0.033, against 0.280 for Fay–Herriot and 0.501 for GeoAI).
The Tier 1 recovery advantage does not transport to the observed e-commerce outcome; on this
surface the Bayesian layer is the worst estimator tested, by a wide margin.

**Q3 (pre-stated): what is its interval behaviour against Fay–Herriot's 0.296?** Higher in
**24 of 24 draws** (0.495 ± 0.065; mean paired difference **+0.199 ± 0.058**), but bought with
width: mean width 2.829 against Fay–Herriot's 0.841, a per-draw width ratio averaging 3.40
(range 2.13–4.81). Against the noisy observed target, 0.495 remains far from the nominal 0.95.
The interval verdict mirrors Tier 1's C1 failure in a new key: coverage improves only by widening,
not by calibration.

## What this changes in the paper

The Tier 2 benchmark becomes five evaluations, four of them proxies and one a genuinely observed
e-commerce outcome; the "ordering does not transport" finding now rests on observed e-commerce
geography, not only on business and tax counts. C3 (Bayesian transport), which requires at least
three Tier 2 evaluations, remains not assessable: the Bayesian layer has been run on one of five.
On that one evaluation the transport test fails outright (Q2), so the manuscript's limitations
paragraph is no longer "transport untested" but "transport tested once, and it failed"; the
abstract, Section 8, Appendix A, and the cover letter were all updated to the completed result
on 2026-10-26.
