# ZIP Demand Model — spatial econometrics + GeoAI under extreme sparse sampling

Code for the manuscript **"Going blind at 8 percent: the behavior of
spatial econometrics and GeoAI under extreme sparse sampling"**
(submitted to *Geographical Analysis*). The paper is a validation /
pathology study: it takes a three-layer ZIP/ZCTA demand-estimation
pipeline — spatial econometrics with a Fay–Herriot small-area layer,
a GeoAI (gradient-boosting) layer, and a game-theoretic decision
layer — and stress-tests how each part behaves when it is fitted to
only ~8% of areas and graded against the truth everywhere else.

## The honest part (read first)

**There is no real ZIP-level outcome data in Tier 1.** The Tier 1
pipeline validates itself by *simulation recovery*: it simulates a
known true demand surface (`config.DGP`), draws a Phase 0-style
sample (~8% of ZCTAs) from it, fits everything to the sample alone,
and grades the recovery against the truth on all ZCTAs. Every Tier 1
output is stamped accordingly (`data_basis = simulated_sample`). The
models are the deliverable; the numbers demonstrate the machinery,
not the market.

**Tier 2 is the empirical counterpart.** The same machinery
(Fay–Herriot vs. GeoAI) is benchmarked on *observed* economic mass —
Census ZIP Code Business Patterns (2022 and 2019) and IRS SOI ZIP
Code data (TY2022) — as a machinery benchmark, not a market
validation. Tier 2 data are free public downloads; `fetch_data.py`
retrieves them (they are not redistributed here).

## Layout

- **Tier 1 (repo root)** — the pipeline:
  1. `layer1_econometrics.py` — market-potential allocation; OLS /
     spatial lag / spatial error / spatial Durbin models (ML,
     hand-implemented with numpy/scipy); Moran's I; Fay–Herriot
     small-area estimates with 95% intervals.
  2. `layer2_geoai.py` — gradient-boosting demand and uptake models
     with quantile intervals, leakage-safe spatial features
     (neighbor covariates and neighbor *model predictions* — never
     neighbor outcomes), permutation importance, k-means clustering
     with a geographic-coherence check.
  3. `layer3_game.py` — Huff-model contest against an aggregate
     incumbent, Monte Carlo competitor responses, payoff bands and
     decision rules.
  Supporting: `common.py`, `config.py` (all parameters + the single
  seed), `data_fetch.py`, `figures.py`, `report.py`, `tests/`.
- **`strengthening/`** — the 2026-10 strengthening analyses behind
  the *Geographical Analysis* submission:
  - `fetch_data.py` — one-time download of the Tier 2 data (Census
    ZBP 2022 + 2019; IRS SOI TY2022).
  - `benchmark.py` — Tier 2 benchmark (FH vs. GeoAI on observed
    economic mass, incl. the 2019→2022 temporal transfer).
  - `tier2_draws.py` — the Tier 2 comparison rerun over 24 sample
    draws (the paper's transportability check).
  - `diagnostics_full.py` + `lm_tests.py` — full-data Moran's I and
    robust LM lag/error diagnostics (the corrected v3 diagnostics:
    genuine full-data tests, n ≈ 5,500 areas).
  - `roughness.py` — the surface-roughness stress test (tested; the
    roughness explanation was NOT supported — reported as an
    untested hypothesis in the paper).
  - `calibration.py` — replicate calibration of the Tier 1 design
    (seeds 20261013 + 1000·r, R = 24, B = 25).
  - `figures_strengthening.py`, `figures_v3.py` — the paper's
    figures (v3 set; Fig. 6 panel labels and Fig. 7 legend fixed in
    v4.1).
  - `results/` — saved outputs, including per-unit predictions
    (`benchmark_predictions.csv`, one row per graded ZCTA).
  - `Design_note_2026-10-18.md` — the design note stating the
    strengthening questions in advance (2026-10-18).

## Run it

```bash
pip install -r requirements.txt

# Tier 1 (simulation recovery; deterministic — config.SEED is the
# single randomness source)
python data_fetch.py     # ONE time: downloads + caches data/ (network)
python run_all.py        # simulation-recovery mode (cached data only)
python run_all.py --real # once data/real_outcomes.csv exists
python -m pytest tests/ -q

# Tier 2 (empirical benchmark)
pip install -r strengthening/requirements.txt
cd strengthening
python fetch_data.py          # once: downloads the free Tier 2 data
python run_strengthening.py   # benchmark + calibration + figures
python run_v3.py              # full v3 pass: full-data diagnostics,
                              # 24-draw Tier 2, roughness, v3 figures
```

## Feeding Tier 1 real data

Replace the simulated sample with a CSV at `data/real_outcomes.csv`,
one row per tested ZCTA per product, columns exactly as specified in
`data_fetch.py` / `config.py`.
