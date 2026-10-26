# Results memo — Test (b): adjusted maximum likelihood Fay–Herriot variances

**Date:** 2026-10-26. **Design:** DESIGN_NOTE_STRENGTHENING_2026-10-26.md,
test (b), executed as written (script `strengthening/code/s2b_aml.py`;
records in `strengthening/results/test_b_aml.json`). Estimators as
published: Li and Lahiri (2010), adjustment factor A applied to the
likelihood; Yoshimori and Lahiri (2014), adjustment
arctan[tr(I − B*)]^(1/m) applied to the likelihood. Both references
verified before coding (J. Multivariate Anal. 101(4):882–892,
doi:10.1016/j.jmva.2009.10.009; and 124:281–294,
doi:10.1016/j.jmva.2013.10.012).

## Method check (implementation validation)

On a small simulated Fay–Herriot problem (m = 30 areas, true
A = 0.02, 200 replications), profile ML returns the boundary
estimate A = 0 in 23 percent of replications; the Li–Lahiri and
Yoshimori–Lahiri adjusted estimators return zero in 0 percent.
The implementations reproduce the papers' central property.

## Panel b1 (Tier 1 swap) — criteria formally met, effect negligible

Holding the shipped construction fixed and replacing only
sigma2_u (24 draws, sampled-area coverage against the DGP truth):

| | Shipped | ML | Li–Lahiri | Yoshimori–Lahiri |
|---|---|---|---|---|
| Steamers coverage | 0.885 | 0.886 | 0.889 | 0.886 |
| Steamers mean A | 0.302 | 0.307 | 0.311 | 0.307 |
| Trio coverage | 0.889 | 0.889 | 0.890 | 0.889 |
| Trio mean A | 0.349 | 0.343 | 0.348 | 0.343 |

No estimator, including plain ML, returns a boundary zero in any
of the 48 draw-product cells. Criteria C-b1 (strict positivity)
and C-b2 (coverage at least as close to 95 percent as the shipped
plug-in) are therefore met for both AML estimators, but by margins
of 0.001 to 0.004 of coverage. The honest reading: with 447 areas,
the boundary pathology the AML literature addresses does not
occur in this design, and the plug-in's sampled-area shortfall
(0.885 / 0.889 against 0.95) is not a boundary-estimate problem.
Swapping the variance estimator leaves the intervals essentially
where they were, which rules out one candidate explanation for
the under-coverage and points back to the channel the paper
already names: psi inherits the weakly identified size from the
count-based joint fit.

## Panel b2 (textbook refit) — no improvement either

The classical area-level refit (regression coefficients profiled
by GLS, intervals from the g1 term only) covers 0.862 to 0.871
across ML, REML, and both AML variants on both products, slightly
below the shipped construction. The AML adjustments move coverage
by at most 0.002 over their unadjusted counterparts here too.

## Panel bT (Tier 2 behaviour) — outcome-dependent, mostly unfavourable

Held-out interval behaviour against the observed log rates, draw
means (share of draws in which the estimator is closest to 0.95 in
parentheses):

| Evaluation | Shipped | ML | Li–Lahiri | Yoshimori–Lahiri |
|---|---|---|---|---|
| ZBP 2022 establishments | 0.903 (0.67) | 0.901 (0.00) | 0.903 (0.33) | 0.901 (0.00) |
| SOI returns | 0.868 (1.00) | 0.638 (0.00) | 0.695 (0.00) | 0.638 (0.00) |
| SOI business returns | 0.947 (0.54) | 0.935 (0.33) | 0.936 (0.12) | 0.935 (0.00) |
| Temporal transfer | 0.917 (0.54) | 0.916 (0.08) | 0.917 (0.38) | 0.916 (0.00) |
| ZBP electronic shopping (new) | 0.296 (0.00) | 0.635 (0.00) | 0.654 (1.00) | 0.635 (0.00) |

On the four existing evaluations the shipped construction is the
closest to nominal most often; the area-level estimators are far
smaller than the shipped sigma2_u on the SOI outcomes and their
intervals under-cover badly there. The single exception is the
new electronic-shopping outcome, where the shipped joint fit's
sigma2_u collapses (mean 0.028) and every likelihood-based
area-level variance is much larger; Li–Lahiri is closest to
nominal in all 24 draws, though at 0.654 it remains far from 0.95
against that sparse target.

## What this licenses in the manuscript

A short passage in the Fay–Herriot section and the limitations:
the plug-in was stress-tested against the boundary-estimate
literature (Li and Lahiri 2010; Yoshimori and Lahiri 2014) in
three constructions, and the under-coverage is not repaired by
any of them, because in this design the pathology they treat
(zero or boundary variance estimates at small m) does not arise.
What is new relative to that literature is stated plainly: their
guarantees concern the area-level model with known sampling
variances and a GLS-profiled regression; the paper's construction
estimates psi from a count-based joint fit, and the failure sits
in that psi channel (and, on one sparse real outcome, in a
collapsed sigma2_u), neither of which an adjustment to the
area-level likelihood reaches.
