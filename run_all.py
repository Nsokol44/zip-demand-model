#!/usr/bin/env python3
"""
run_all.py — the one command that reproduces everything:

    python run_all.py            # simulation-recovery mode
    python run_all.py --real     # use data/real_outcomes.csv instead

Reads ONLY the cached files in data/ (run data_fetch.py once first).
Writes results/zip_scores.csv, results/RESULTS.md, results/figures/*,
plus audit artifacts (simulated outcomes, grading truth, cluster
summaries, model metrics JSON). Fully deterministic: config.SEED is
the single randomness source; rerunning produces identical outputs.
"""

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
import config
import figures
import layer1_econometrics as layer1
import layer2_geoai as layer2
import layer3_game as layer3
import report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true",
                    help="use data/real_outcomes.csv (Phase 0 data) "
                         "instead of the simulated sample")
    args = ap.parse_args()
    t0 = time.time()
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    real_path = None
    if args.real:
        real_path = os.path.join(config.DATA_DIR, "real_outcomes.csv")
        if not os.path.exists(real_path):
            raise SystemExit(f"--real given but {real_path} not found")

    print("[1/6] features + weights", flush=True)
    df = common.load_features()
    df = common.add_model_features(df)
    print(f"      imputations: {df.attrs['imputations']}", flush=True)
    Z, _stats = common.standardize(df)
    W = common.build_weights(df)
    common.save_weights(W, os.path.join(config.DATA_DIR, "weights.npz"))
    print(f"      {len(df):,} ZCTAs, W {W.shape}, "
          f"nnz {W.nnz:,}", flush=True)

    rng = np.random.default_rng(config.SEED)

    print("[2/6] layer 1: spatial econometrics", flush=True)
    l1 = layer1.run_layer1(df, Z, W, rng, real_path=real_path)
    for p, r in l1["products"].items():
        print(f"      {p}: best={r['best']}, Moran I="
              f"{r['moran_i']:.3f} (p={r['moran_p']:.3f}), "
              f"coverage={r['coverage']}", flush=True)

    print("[3/6] layer 2: GeoAI estimation + clusters", flush=True)
    l2 = layer2.run_layer2(df, Z, W, l1, rng)

    print("[4/6] layer 3: game-theory play-through", flush=True)
    l3 = layer3.run_layer3(df, Z, l1, l2, rng)

    print("[5/6] outputs", flush=True)
    demo = config.DEMO_PRODUCT
    second = config.SECOND_PRODUCT
    d1, d2 = l1["products"][demo], l1["products"][second]
    g1, g2 = l2["products"][demo], l2["products"][second]
    hh = df["households"].to_numpy(float)
    sl = l3["shortlist"].set_index("zcta")

    scores = pd.DataFrame({
        "region": df["region"], "zcta": df["zcta"],
        "state": df["state"], "county_fips": df["county_fips"],
        "population": df["population"], "households": df["households"],
        "cluster_id": l2["clusters"]["cluster_id"],
        "data_basis": ("real_outcomes" if real_path
                       else "simulated_sample"),
        "in_sample": l1["outcomes"][demo]["sampled"],
        "potential_spend_demo": d1["potential_spend"],
        "potential_spend_second": d2["potential_spend"],
        "econ_est_rate": np.exp(d1["fh"]["est_log_rate"]),
        "econ_est_lo": np.exp(d1["fh"]["lo"]),
        "econ_est_hi": np.exp(d1["fh"]["hi"]),
        "econ_est_orders_yr": np.exp(d1["fh"]["est_log_rate"]) * hh,
        "geoai_pred_rate": np.exp(g1["pred_log_rate"]),
        "geoai_pred_lo": np.exp(g1["pred_lo"]),
        "geoai_pred_hi": np.exp(g1["pred_hi"]),
        "geoai_pred_rate_second": np.exp(g2["pred_log_rate"]),
        "uptake_score": g1["uptake"],
        "uptake_lo": g1["uptake_lo"],
        "uptake_hi": g1["uptake_hi"],
    })
    for col, src in (("gt_share_p50", "share_p50"),
                     ("gt_contribution_p50", "contribution_p50"),
                     ("gt_win_rate", "win_rate"),
                     ("gt_decision", "decision")):
        scores[col] = scores["zcta"].map(sl[src]) if src in sl else np.nan
    scores = scores.sort_values(["region", "zcta"])
    scores_path = os.path.join(config.RESULTS_DIR, "zip_scores.csv")
    scores.to_csv(scores_path, index=False)
    print(f"      wrote {scores_path} ({len(scores):,} rows)", flush=True)

    # audit artifacts
    oc_all = pd.concat([l1["outcomes"][p] for p in config.PRODUCTS],
                       ignore_index=True)
    oc_all.to_csv(os.path.join(config.RESULTS_DIR,
                               "observed_sample.csv"), index=False)
    if not real_path:
        truth_rows = {"zcta": df["zcta"]}
        for p in config.PRODUCTS:
            t = l1["truth"][p]
            truth_rows[f"true_log_rate_{p}"] = t["true_log_rate"]
            truth_rows[f"true_uptake_{p}"] = t["true_uptake"]
        pd.DataFrame(truth_rows).to_csv(
            os.path.join(config.RESULTS_DIR, "grading_truth.csv"),
            index=False)
    pd.DataFrame(l2["clusters"]["summaries"]).to_csv(
        os.path.join(config.RESULTS_DIR, "cluster_summaries.csv"),
        index=False)
    l3["shortlist"].drop(columns=["_row_index"]).to_csv(
        os.path.join(config.RESULTS_DIR, "game_shortlist.csv"),
        index=False)
    metrics = {}
    for p in config.PRODUCTS:
        r = l1["products"][p]
        metrics[p] = {
            "best_model": r["best"], "moran_i": r["moran_i"],
            "moran_p": r["moran_p"],
            "rmse_log_ols": r["rmse_log_ols"],
            "rmse_log_best_model": r["rmse_log_best_model"],
            "rmse_log_fh": r["rmse_log_fh"],
            "coverage": r["coverage"],
            "coverage_sampled": r["coverage_sampled"],
            "geoai": l2["products"][p]["agreement"],
        }
    with open(os.path.join(config.RESULTS_DIR, "model_metrics.json"),
              "w") as fh:
        json.dump(metrics, fh, indent=2)

    print("[6/6] figures + RESULTS.md", flush=True)
    figures.make_figures(df, l2, l3)
    figures.agreement_scatter(df, l1, l2)
    report.write_results_md(
        os.path.join(config.RESULTS_DIR, "RESULTS.md"),
        {"df": df, "layer1": l1, "layer2": l2, "layer3": l3})

    print(f"done in {time.time() - t0:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
