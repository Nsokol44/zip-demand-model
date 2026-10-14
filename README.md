# ZIP Demand Model — spatial econometrics + GeoAI + game theory

A three-layer model of product demand by ZCTA, built as the Phase 2
analysis machinery for the Wizemode Shops Phase 0 slate:

1. **Layer 1 — spatial econometrics.** Market-potential allocation,
   OLS / spatial lag / spatial error / spatial Durbin models (ML,
   hand-implemented with numpy/scipy — spreg is not installed here),
   Moran's I diagnostics, and a Fay–Herriot small-area layer giving
   every ZCTA an estimate with a 95% interval.
2. **Layer 2 — GeoAI estimation.** Gradient-boosting demand and
   funnel-uptake models with quantile intervals, leakage-safe spatial
   features (neighbor covariates and neighbor *model predictions* —
   never neighbor outcomes), permutation importance, and k-means
   ZIP clusters with a geographic-coherence check.
3. **Layer 3 — geospatial game theory.** A Huff-model contest against
   an aggregate incumbent for the top-25 ZIPs per region, Monte Carlo
   over three competitor response strategies, payoff bands, win rates,
   and printed decision rules — plus one narrated showcase
   play-through.

## The honest part (read first)

**There is no real ZIP-level outcome data yet.** Phase 0 will
generate it. Until then the pipeline validates itself by
*simulation recovery*: it simulates a known true demand surface
(`config.DGP`), draws a Phase 0-style sample (~8% of ZCTAs) from it,
fits everything to the sample alone, and grades the recovery against
the truth on all ZCTAs. Every output is stamped accordingly
(`data_basis = simulated_sample`). The models are the deliverable;
the numbers demonstrate the machinery, not the market.

## Run it

```bash
python data_fetch.py     # ONE time: downloads + caches data/ (network)
python run_all.py        # simulation-recovery mode (cached data only)
python run_all.py --real # once data/real_outcomes.csv exists
python -m pytest tests/ -q
```

`run_all.py` is deterministic: `config.SEED` is the single
randomness source and the call order is fixed, so reruns reproduce
`results/` byte-identically (the determinism test in tests/ pins the
simulator's output hash).

## Feeding it real data

Replace the simulated sample with a CSV at `data/real_outcomes.csv`,
one row per tested ZCTA per product, columns exactly:

`zcta, product, sessions, add_to_carts, orders, exposure_days`

`product` is `steamers` or `trio`; orders are annualized by
`exposure_days` inside the pipeline. Then `python run_all.py --real`
— every estimator, figure, and output regenerates; DGP/recovery
content drops out and `data_basis` becomes `real_outcomes`.

## Data sources & vintages

- **ACS 5-year 2023** ZCTA-level estimates from the Census Bureau's
  official table-based summary files on www2.census.gov (the Census
  API requires a key; same workaround as
  `~/workspace/video-factory/pipeline/receptivity.py`). Tables:
  B01002, B01003, B19001, B19013, B25001, B25003, B25004, B25010,
  B25024. ZCTA rows carry summary level 860 (GEO_ID `860Z200US…`).
- **2023 ZCTA Gazetteer** — centroids + land area.
- **Cartographic boundaries** — states/counties 2023 500k (region
  assignment), ZCTA polygons 2020 500k (maps). ZCTAs are a
  2020-vintage geography. Region assignment is centroid-in-polygon
  with a nearest-polygon fallback (counts printed by data_fetch).
- Study set: ZCTAs with population ≥ 500 and households ≥ 200 —
  5,057 Southeast (TN NC SC GA FL AL VA KY) + 519 NYC metro (five
  boroughs + Nassau, Suffolk, Westchester, Hudson, Bergen, Essex).

## Feature dictionary (data/features.csv)

| column | source | meaning |
|---|---|---|
| population | B01003_E001 | total population |
| households | B25003_E001 | occupied housing units |
| median_hh_income | B19013_E001 | median household income |
| share_income_100k | B19001 | share of HHs with income ≥ $100k |
| renter_share | B25003 | renter-occupied / occupied |
| seasonal_share | B25004_E006 / B25001 | seasonal-vacant share |
| pct_single_family | B25024 | 1-unit structures / all structures |
| pct_large_building | B25024 | 20+-unit structures / all |
| avg_hh_size | B25010_E001 | average household size |
| median_age | B01002_E001 | median age |
| pop_density | derived | population / land sq mi (gazetteer) |

Model features add `log_income` and `log_density` (see
`common.FEATURES`). Missing ACS cells (54 ZCTAs lack a median income)
are median-imputed within region and counted in the run log.

## Outputs

- `results/zip_scores.csv` — one row per ZCTA: cluster, potential
  spend, Layer 1 estimate + interval, Layer 2 prediction + interval,
  uptake score, game-theory columns (shortlist only).
- `results/RESULTS.md` — methods, DGP truth, model comparison,
  recovery metrics, cluster summaries, showcase play-through, and
  the real-vs-simulated accounting.
- `results/figures/` — NYC + Southeast choropleths, showcase payoff
  distribution, Layer 1 vs Layer 2 agreement scatter.
- Audit artifacts: `results/observed_sample.csv`,
  `results/grading_truth.csv` (simulation mode only),
  `results/cluster_summaries.csv`, `results/game_shortlist.csv`,
  `results/model_metrics.json`.

## Known simplifications

- Spatial ML models are fit on the sample's own kNN graph (k=6);
  in-population prediction for SAR/SDM uses the full-graph reduced
  form. Coefficient covariances for SAR/SDM are the standard
  transformed-OLS approximation, not the full ML Hessian.
- Layer 3's incumbent is an ACS-covariate proxy index, not POI data;
  response probabilities are a parameterized logistic assumption.
- The Fay–Herriot sampling variances come from a joint ML fit
  (NegBin size + lognormal area-effect variance, Gauss–Hermite
  quadrature) on the sample counts — never from the DGP's true size,
  and not from plug-in moments (which confound the two variance
  components; see layer1_econometrics.fay_herriot).
