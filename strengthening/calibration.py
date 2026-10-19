"""
calibration.py — CONCERN 2 + CONCERN 3 study, inside the Tier 1
simulation framework (pre-stated in ../ANALYSIS_NOTES.md).

For R replicate DGP draws (replicate r uses seed 20261013 + 1000*r;
both products; the pipeline is refit exactly as shipped via
layer1.run_layer1):

  * Nominal-95% Fay-Herriot coverage against the replicate's own truth
    (sampled areas and all areas) — the mis-coverage distribution, not
    just the canonical realization.
  * REMEDY: parametric-bootstrap calibration of the interval half-width
    (Prasad-Rao spirit). From the replicate's FITTED model (model
    predictions, fitted NegBin size, fitted area variance) B bootstrap
    worlds are drawn for the sampled areas; the Fay-Herriot stage is
    re-run in each; the multiplier m_r is the 95th percentile of
    |latent - estimate| / nominal-half-width pooled over worlds and
    areas. m_r is applied to the replicate's intervals and coverage
    against the DGP truth is re-measured. Nothing is tuned against the
    truth: m_r is estimated entirely inside the bootstrap world.
  * DIAGNOSTICS: Moran's I (pipeline permutation) plus Anselin-Bera LM
    error/lag and robust forms on the replicate's OLS residuals —
    rejection rates at 5%, and the AIC model choice.

Outputs ../results/calibration_results.json with per-replicate records
and pooled summaries.
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
from lm_tests import lm_tests          # noqa: E402

R_REPLICATES = 24
B_WORLDS = 25


def cov_diag_for(fit, df, Z):
    X_all = np.column_stack([np.ones(len(df)), Z])
    cov = fit["cov"][:X_all.shape[1], :X_all.shape[1]]
    return np.clip(np.einsum("ij,jk,ik->i", X_all, cov, X_all), 0.0, 2.0)


def one_replicate(r, df, Z, W, households):
    seed = config.SEED + 1000 * r
    rng = np.random.default_rng(seed)
    res = layer1.run_layer1(df, Z, W, rng)
    spawn = np.random.SeedSequence(seed).spawn(B_WORLDS)
    rec = {"replicate": r, "seed": seed, "products": {}}
    for product in config.PRODUCTS:
        pr = res["products"][product]
        oc = res["outcomes"][product]
        truth = res["truth"][product]["true_log_rate"]
        sampled = oc["sampled"].to_numpy()
        fh = pr["fh"]
        est, lo, hi = fh["est_log_rate"], fh["lo"], fh["hi"]
        half = (hi - lo) / 2.0
        cov_s = float(np.mean((truth[sampled] >= lo[sampled])
                              & (truth[sampled] <= hi[sampled])))
        cov_a = float(np.mean((truth >= lo) & (truth <= hi)))

        # --- bootstrap calibration ----------------------------------
        pred_s = pr["model_pred_log_rate"][sampled]
        hh_s = households[sampled]
        size_hat, su = fh["nb_size_hat"], fh["sigma2_u"]
        cd_s = cov_diag_for(pr["fits"][pr["best"]], df, Z)[sampled]
        mu_s = np.exp(pred_s) * hh_s
        ratios, boot_cov = [], []
        for b in range(B_WORLDS):
            rb = np.random.default_rng(spawn[b])
            v = rb.normal(-0.5 * su, np.sqrt(su), size=sampled.sum())
            theta_star = pred_s + v
            mu_star = hh_s * np.exp(theta_star)
            p = size_hat / (size_hat + mu_star)
            counts_b = rb.negative_binomial(size_hat, p)
            y_b = np.log((counts_b + 0.5) / hh_s)
            fh_b = layer1.fay_herriot(pred_s, y_b, counts_b.astype(float),
                                      hh_s, cov_diag_sample=cd_s)
            est_b = fh_b["est_sample"]
            half_b = 1.96 * np.sqrt(np.clip(fh_b["var_sample"],
                                            1e-6, None))
            ratios.append(np.abs(theta_star - est_b) / half_b)
            boot_cov.append(float(np.mean(
                (theta_star >= est_b - half_b)
                & (theta_star <= est_b + half_b))))
        ratios = np.concatenate(ratios)
        m_r = float(np.quantile(ratios, 0.95))
        lo_c, hi_c = est - m_r * half, est + m_r * half
        cov_s_cal = float(np.mean((truth[sampled] >= lo_c[sampled])
                                  & (truth[sampled] <= hi_c[sampled])))
        cov_a_cal = float(np.mean((truth >= lo_c) & (truth <= hi_c)))

        # --- diagnostics ---------------------------------------------
        y_all = np.log((oc["orders_annualized"].to_numpy(float) + 0.5)
                       / households)
        Xs = np.column_stack([np.ones(sampled.sum()), Z[sampled]])
        W_s = common.weights_for_subset(W, sampled)
        lm = lm_tests(Xs, y_all[sampled], W_s.toarray())

        rec["products"][product] = {
            "best_model": pr["best"],
            "size_hat": size_hat, "sigma2_u": su,
            "coverage_sampled": cov_s, "coverage_all": cov_a,
            "multiplier": m_r,
            "coverage_sampled_calibrated": cov_s_cal,
            "coverage_all_calibrated": cov_a_cal,
            "bootstrap_world_nominal_coverage": float(np.mean(boot_cov)),
            "moran_i": pr["moran_i"], "moran_p": pr["moran_p"],
            "lm": lm,
        }
    return rec


def main():
    t0 = time.time()
    df = common.load_features()
    df = common.add_model_features(df)
    Z, _ = common.standardize(df)
    W = common.build_weights(df)
    households = df["households"].to_numpy(float)

    ckpt = os.path.join(ROOT, "results",
                        "calibration_records_partial.json")
    records = []
    if os.path.exists(ckpt):
        records = json.load(open(ckpt))
    done = {rec["replicate"] for rec in records}
    for r in range(R_REPLICATES):
        if r in done:
            continue
        rec = one_replicate(r, df, Z, W, households)
        records.append(rec)
        records.sort(key=lambda d: d["replicate"])
        with open(ckpt, "w") as fh:
            json.dump(records, fh)
        s = rec["products"]["steamers"]
        print(f"rep {r:2d}: steamers cov {s['coverage_sampled']:.3f} -> "
              f"{s['coverage_sampled_calibrated']:.3f} (m="
              f"{s['multiplier']:.2f}), best={s['best_model']}",
              flush=True)

    summary = {}
    for product in config.PRODUCTS:
        rows = [rec["products"][product] for rec in records]
        def agg(key):
            v = np.array([row[key] for row in rows], dtype=float)
            return {"mean": float(v.mean()), "sd": float(v.std()),
                    "min": float(v.min()), "max": float(v.max())}
        rej = {}
        for name in ("moran", "lm_error", "lm_lag", "robust_lm_error",
                     "robust_lm_lag"):
            if name == "moran":
                ps = [row["moran_p"] for row in rows]
            else:
                ps = [row["lm"][name + "_p"] for row in rows]
            rej[name] = float(np.mean(np.array(ps) < 0.05))
        # joint: Moran misses (p>=.05) but LM error catches (p<.05)
        joint = float(np.mean([
            (row["moran_p"] >= 0.05) and (row["lm"]["lm_error_p"] < 0.05)
            for row in rows]))
        summary[product] = {
            "coverage_sampled": agg("coverage_sampled"),
            "coverage_sampled_calibrated":
                agg("coverage_sampled_calibrated"),
            "coverage_all": agg("coverage_all"),
            "coverage_all_calibrated": agg("coverage_all_calibrated"),
            "multiplier": agg("multiplier"),
            "bootstrap_world_nominal_coverage":
                agg("bootstrap_world_nominal_coverage"),
            "size_hat": agg("size_hat"), "sigma2_u": agg("sigma2_u"),
            "rejection_rates_5pct": rej,
            "moran_miss_lm_error_catch_rate": joint,
            "best_model_share": {
                m: float(np.mean([row["best_model"] == m for row in rows]))
                for m in ("SAR", "SEM", "SDM")},
        }
    out = {"R_replicates": R_REPLICATES, "B_worlds": B_WORLDS,
           "summary": summary, "records": records}
    path = os.path.join(ROOT, "results", "calibration_results.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"wrote {path} in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
