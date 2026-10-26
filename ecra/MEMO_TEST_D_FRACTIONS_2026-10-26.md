# Memo — Test D: Tier 1 at 4 percent and 16 percent sampling

Date: 2026-10-26. Design: `ecra/DESIGN_NOTE_STRENGTHENING_2026-10-26.md` (Test (d), stated before
the runs; no pass/fail criterion attaches — the pre-stated question is how the three Section 5
pathologies scale with the sampling fraction). Code: `ecra/strengthening/code/s2d_fractions.py`
(the shipped calibration protocol rerun verbatim, fraction set by argument). Results:
`ecra/strengthening/results/test_d_frac4.json`, `test_d_frac16.json` (24 replicate records each);
8 percent values of record from `strengthening-2026-10-18/results/calibration_results.json`.

## Results (draw means over 24 replicates; pooled values computed from the records — see deviations)

| Fraction | Product | Raw sampled | Cal. sampled | Raw all | Cal. all | Multiplier | Size-hat | σ²u | Moran rej. | LM-error rej. |
|---|---|---|---|---|---|---|---|---|---|---|
| 4% (223 areas) | steamers | 0.885 | 0.909 | 0.946 | 0.966 | 1.110 | 24.2 | 0.322 | 0.083 | 0.083 |
| 4% | trio | 0.897 | 0.917 | 0.936 | 0.959 | 1.117 | 20.2 | 0.313 | 0.167 | 0.167 |
| 8% (447 areas) | steamers | 0.885 | 0.914 | 0.931 | 0.953 | 1.119 | 14.8 | 0.302 | 0.167 | 0.167 |
| 8% | trio | 0.876 | 0.900 | 0.960 | 0.975 | 1.107 | 24.7 | 0.356 | 0.375 | 0.417 |
| 16% (892 areas) | steamers | 0.916 | 0.948 | 0.945 | 0.968 | 1.146 | 9.7 | 0.300 | 0.458 | 0.500 |
| 16% | trio | 0.910 | 0.938 | 0.956 | 0.974 | 1.127 | 13.6 | 0.336 | 0.458 | 0.458 |

Bootstrap-world nominal coverage is flat across fractions (0.917–0.928), as at 8 percent: the
calibration machinery's own worlds under-cover at every fraction, which is the internal evidence
that the multiplier corrects an interval that is miss-centered for the realized draws, not merely
narrow.

## Reading (answering the pre-stated question)

1. **Interval pathology.** Raw sampled-area coverage is flat from 4 to 8 percent and improves at
   16 percent, but remains roughly four points short of the 95 percent nominal level even at
   twice the design fraction. Bootstrap calibration adds two to three points at every fraction
   and comes closest to nominal only at 16 percent (0.948 steamers). The pathology attenuates
   with sample size; it does not vanish, and the 8 percent design point is not a knife edge.
2. **Variance-split identification.** The fitted size-hat moves monotonically toward the truth
   of 6 as the fraction grows for steamers (24.2 → 14.8 → 9.7) and from 8 to 16 percent for trio
   (24.7 → 13.6; the 4 percent trio value, 20.2, sits below its 8 percent value), but remains
   1.6–2.3 times the truth at 16 percent. σ²u is essentially flat (0.30–0.36). Identification
   improves with the fraction exactly as the ridge account predicts, and slowly.
3. **Diagnostic blindness.** Moran rejection rises with the fraction (steamers 8% → 17% → 46%
   of draws; trio 17% → 38% → 46%), and LM-error tracks it. Even at 16 percent sampling the
   standard diagnostics miss a ρ = 0.55 process in over half of draws.
4. **Section 8 limitation.** The econometric core's fraction limitation is narrowed: the
   protocol has now been run at 4 and 16 percent as well as 8. The Bayesian layer was NOT
   rerun at the new fractions under this program, and the prior-sensitivity grid and the seven
   unrun temporal replicates remain unrun; the manuscript's limitation says exactly this.

## Deviations (also logged in the design note)

- D1: the `pooled` blocks of both new JSON files are null (aggregation key mismatch in
  `s2d_fractions.py`). Every pooled number above was computed post hoc from the complete
  per-replicate records; no compute was redone.
- D2: the protocol's replicate function returns no RMSEs, so no RMSE-by-fraction is reported,
  here or in the manuscript.
