"""
tier2_draws.py — A3 (2026-10-18 review): Tier 2 uncertainty.

The v2 Tier 2 benchmark rests on ONE 8% sample (the canonical
steamers sample). Because the real outcomes are fixed, the
benchmark can be rerun across the same 24 sample draws the Tier 1
calibration study used: replicate r's sample is the steamers mask
drawn by layer1.simulate_truth under seed config.SEED + 1000*r
(steamers is the first product in the pipeline's replicate loop;
replicate 0 reproduces the canonical 447-area mask exactly —
verified). For each draw, the full Tier 2 protocol (benchmark.py,
unmodified) is fitted on the draw's sample and graded on the
held-out remainder, for all three 2022 outcomes plus the
2019 -> 2022 temporal transfer.

Writes ../results/tier2_draws.json (per-draw records + summaries).
Checkpointed per draw to ../results/tier2_draws_partial.json.
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
import layer1_econometrics as layer1   # noqa: E402
import benchmark as bm                 # noqa: E402

R_DRAWS = 24
LAYERS = ("ols", "best_spatial", "fay_herriot", "geoai")


def replicate_mask(df, Z, W, r):
    rng = np.random.default_rng(config.SEED + 1000 * r)
    _truth, oc = layer1.simulate_truth(df, Z, W, "steamers", rng)
    return oc["sampled"].to_numpy(bool)


def main():
    t0 = time.time()
    df = common.load_features()
    df = common.add_model_features(df)
    Z, _ = common.standardize(df)
    W = common.build_weights(df)
    households = df["households"].to_numpy(float)
    zctas = df["zcta"].to_numpy()

    zbp22 = bm.align_counts(bm.load_zbp(2022), zctas)
    zbp19 = bm.align_counts(bm.load_zbp(2019), zctas)
    soi_n1_s, soi_bus_s = bm.load_soi22()
    soi_n1 = bm.align_counts(soi_n1_s, zctas)
    soi_bus = bm.align_counts(soi_bus_s, zctas)

    ckpt = os.path.join(ROOT, "results", "tier2_draws_partial.json")
    records = []
    if os.path.exists(ckpt):
        records = json.load(open(ckpt))
    done = {rec["draw"] for rec in records}

    evals = (("zbp22_establishments", zbp22, zbp22),
             ("soi22_returns", soi_n1, soi_n1),
             ("soi22_business_returns", soi_bus, soi_bus),
             ("temporal_transfer_zbp19_to_zbp22", zbp19, zbp22))

    for r in range(R_DRAWS):
        if r in done:
            continue
        mask = replicate_mask(df, Z, W, r)
        rec = {"draw": r, "seed": config.SEED + 1000 * r,
               "n_sampled": int(mask.sum()), "outcomes": {}}
        for label, fit_counts, grade_counts in evals:
            rng = np.random.default_rng(config.SEED + 1000 * r)
            fit = bm.fit_architecture(df, Z, W, fit_counts, mask, rng)
            ev, _ = bm.evaluate(fit, grade_counts, mask, households)
            rec["outcomes"][label] = {
                "n_graded": ev["n_graded"],
                "best_model": fit["best_model"],
                "rmse": {k: ev[k]["rmse"] for k in LAYERS},
                "spearman": {k: ev[k]["spearman"] for k in LAYERS},
                "top_decile_overlap":
                    {k: ev[k]["top_decile_overlap"] for k in LAYERS},
                "fh_coverage":
                    ev["fh_interval_behaviour"]
                    ["coverage_vs_observed_nominal95"],
                "agreement_fh_geoai_top_decile":
                    ev["agreement_fh_vs_geoai"]["top_decile_overlap"],
            }
        records.append(rec)
        records.sort(key=lambda d: d["draw"])
        with open(ckpt, "w") as fh:
            json.dump(records, fh)
        z = rec["outcomes"]["zbp22_establishments"]
        print(f"draw {r:2d}: n={rec['n_sampled']} ZBP rmse FH="
              f"{z['rmse']['fay_herriot']:.3f} GeoAI="
              f"{z['rmse']['geoai']:.3f} cov={z['fh_coverage']:.3f} "
              f"({time.time() - t0:.0f}s)", flush=True)

    summary = {}
    for label, _f, _g in evals:
        rows = [rec["outcomes"][label] for rec in records]
        def agg(get):
            v = np.array([get(row) for row in rows], dtype=float)
            return {"mean": float(v.mean()), "sd": float(v.std()),
                    "min": float(v.min()), "max": float(v.max())}
        summary[label] = {
            "rmse": {k: agg(lambda row, k=k: row["rmse"][k])
                     for k in LAYERS},
            "spearman": {k: agg(lambda row, k=k: row["spearman"][k])
                         for k in LAYERS},
            "top_decile_overlap":
                {k: agg(lambda row, k=k: row["top_decile_overlap"][k])
                 for k in LAYERS},
            "fh_coverage": agg(lambda row: row["fh_coverage"]),
            "geoai_beats_fh_share":
                float(np.mean([row["rmse"]["geoai"]
                                < row["rmse"]["fay_herriot"]
                                for row in rows])),
            "geoai_margin_vs_fh":
                agg(lambda row: row["rmse"]["fay_herriot"]
                    - row["rmse"]["geoai"]),
            "agreement_fh_geoai_top_decile":
                agg(lambda row: row["agreement_fh_geoai_top_decile"]),
            "best_model_share": {
                m: float(np.mean([row["best_model"] == m
                                  for row in rows]))
                for m in ("OLS", "SAR", "SEM", "SDM")},
        }
    out = {"R_draws": R_DRAWS, "summary": summary, "records": records}
    path = os.path.join(ROOT, "results", "tier2_draws.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"wrote {path} in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
