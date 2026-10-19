"""
diagnostics_full.py — V2 AUDIT FIX (2026-10-18 review).

The v2 manuscript (Sections 5.8/5.9) described the Tier 2 Moran/LM
diagnostics as computed "on the full-data OLS residuals" / "fitted
to all 5,576 areas". Audit of benchmark.py shows they were in fact
computed on the OBSERVED-SAMPLE OLS residuals (the 447-area sample
graph; n_fit = 436-441 depending on outcome), because
layer1.fit_all_models fits on the sample only. The values in
benchmark_results.json (e.g. Moran I = 0.213, permutation p = 0.034
for SOI business returns) are sample diagnostics mislabelled as
full-data ones.

This script computes the diagnostics the manuscript claimed:
OLS of the observed log rate on the pipeline covariates fitted to
EVERY ZCTA with an observed outcome (n ~ 5,500), residuals over the
full frame, Moran's I (pipeline permutation function, 999 perms) and
Anselin-Bera LM tests on the full weights graph.

Writes ../results/diagnostics_full.json.
"""

import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
REPO = os.path.abspath(os.path.join(HERE, ".."))  # repo root (Tier 1 pipeline)
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

import common          # noqa: E402
import config          # noqa: E402
from lm_tests import lm_tests          # noqa: E402
import benchmark as bm                 # noqa: E402


def full_diagnostics(df, Z, W, counts, label):
    has = ~np.isnan(counts)
    households = df["households"].to_numpy(float)
    y = np.log((counts[has] + 0.5) / households[has])
    X = np.column_stack([np.ones(has.sum()), Z[has]])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    W_sub = common.weights_for_subset(W, has)
    rng = np.random.default_rng(config.SEED)
    mi, mi_p = common.morans_i(resid, W_sub, rng)
    t0 = time.time()
    lm = lm_tests(X, y, W_sub.toarray())
    return {
        "label": label, "n": int(has.sum()),
        "moran_i": float(mi), "moran_p": float(mi_p),
        "moran_permutations": 999,
        "lm": lm, "lm_seconds": time.time() - t0,
    }


def main():
    df = common.load_features()
    df = common.add_model_features(df)
    Z, _ = common.standardize(df)
    W = common.build_weights(df)
    zctas = df["zcta"].to_numpy()

    zbp22 = bm.align_counts(bm.load_zbp(2022), zctas)
    soi_n1_s, soi_bus_s = bm.load_soi22()
    soi_n1 = bm.align_counts(soi_n1_s, zctas)
    soi_bus = bm.align_counts(soi_bus_s, zctas)

    out = {"design": "OLS on all ZCTAs with observed outcome; "
                     "residuals over the full frame; pipeline "
                     "Moran permutation (999) and LM tests on the "
                     "full weights graph.",
           "outcomes": {}}
    for label, counts in (("zbp22_establishments", zbp22),
                          ("soi22_returns", soi_n1),
                          ("soi22_business_returns", soi_bus)):
        r = full_diagnostics(df, Z, W, counts, label)
        out["outcomes"][label] = r
        print(f"{label}: n={r['n']} Moran I={r['moran_i']:.3f} "
              f"p={r['moran_p']:.3f} LMerr p="
              f"{r['lm']['lm_error_p']:.2e} LMlag p="
              f"{r['lm']['lm_lag_p']:.3f}", flush=True)
    path = os.path.join(ROOT, "results", "diagnostics_full.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=2)
    print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
