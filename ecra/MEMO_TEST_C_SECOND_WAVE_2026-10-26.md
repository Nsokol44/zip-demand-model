# Results memo — Test (c): a simulated second wave

**Date:** 2026-10-26. **Design:** DESIGN_NOTE_STRENGTHENING_2026-10-26.md,
test (c), executed as written (script
`strengthening/code/s2c_wave.py`; per-draw records in
`strengthening/results/test_c_wave.json`). 24 draws, both products.
Self-check passed on draw 0: the injected-parameter construction
reproduces the shipped `fay_herriot` fit's sigma2_u, psi, and sample
estimates exactly, so wave-1-only numbers are the shipped ones.

## Verdict (pre-stated rule): the claim is SUPPORTED, for both products

The paper's claim (Sections 5.4, 7, 8) is that a second test wave
would identify the (size, sigma2_u) split, because repeated counts
per area separate count noise, which is independent across waves,
from the shared area effect. All three pre-stated components moved
the right way on the draw means, for both products:

| Component | Steamers | Trio |
|---|---|---|
| M1 size recovery, mean \|log(size-hat / 6.0)\|, wave 1 only | 0.848 | 1.082 |
| M1 same, pooled two-wave fit | **0.073** | **0.093** |
| M2 ridge sharpness (mean log-lik drop at size fixed to 0.5x / 2x), wave 1 only | 2.9 | 1.9 |
| M2 same, pooled | **28.3** | **24.6** |
| M3 wave-2 sampled-area coverage, wave-1 split | 0.889 | 0.885 |
| M3 same, pooled split | **0.941** | **0.942** |

In words: with one wave, the fitted size is off by a factor of
about e^0.85 ≈ 2.3 (steamers) to e^1.08 ≈ 2.9 (trio) in log terms,
and the likelihood ridge is nearly flat (a twofold miss in size
costs under 3 log-likelihood points). Pooling a second wave over
the shared area effect cuts the size error by an order of
magnitude, sharpens the ridge roughly tenfold, and moves the
coverage consequence to 0.94, within about a point of nominal.

## What this licenses in the manuscript

The limitation language can be upgraded from conjecture to a
tested statement: the second-wave design identifies the split in
this DGP, at this sampling fraction and frame, by the mechanism
the paper names. Two honest bounds stay attached. First, the test
is a simulation inside the paper's own DGP (the wave-2 counts are
drawn from the same true rates with the same size), so it shows
the design identifies the split when the model is right; it does
not show a real second wave would be so clean. Second, pooled
coverage reaches 0.941 / 0.942, close to but still below 0.95:
identifying the split removes most, not all, of the sampled-area
shortfall.
