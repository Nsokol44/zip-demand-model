"""
benchmark.py — TIER 2: empirical benchmark of the ZIP-demand
architecture on observed, freely available outcomes.

Design (pre-stated in ../ANALYSIS_NOTES.md before this was run):
the pipeline's Layer 1 (spatial suite + Fay-Herriot stage) and Layer 2
(gradient boosting, identical leakage controls and parameters) are fit
on exactly the ZCTAs the canonical simulation designates as its
observed sample (447 of 5,576, demo-product mask), and graded
out-of-sample against observed outcomes on the remaining ZCTAs.
Outcomes are public economic-activity counts — NOT purchases of the
slate products; this is an empirical benchmark of the machinery, not a
market validation.

Outcomes (all counts per ZCTA, merged on the 5-digit code):
  zbp22      ZIP Code Business Patterns 2022, total establishments
  soi22_n1   IRS SOI tax year 2022, number of returns (agi_stub = 1)
  soi22_bus  IRS SOI tax year 2022, N00900 = number of returns with
             business or professional net income (less loss)
  zbp19->22  temporal transfer: fit on ZBP 2019, grade on ZBP 2022

Pipeline modules are imported from the replication repo UNMODIFIED.
"""

import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import sparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
REPO = os.path.abspath(os.path.join(HERE, ".."))  # repo root (Tier 1 pipeline)
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

import common          # noqa: E402  (pipeline)
import config          # noqa: E402  (pipeline)
import layer1_econometrics as layer1   # noqa: E402
import layer2_geoai as layer2          # noqa: E402
from lm_tests import lm_tests          # noqa: E402


# ---------------------------------------------------------------- data

def load_zbp(year):
    path = os.path.join(ROOT, "data", f"zbp{str(year)[-2:]}totals.zip")
    df = pd.read_csv(path, compression="zip", dtype={"zip": str},
                     encoding="latin-1")
    df["zip"] = df["zip"].str.zfill(5)
    return df.set_index("zip")["est"].astype(float)


def load_soi22():
    path = os.path.join(ROOT, "data", "22zpallagi.csv")
    out = {}
    for chunk in pd.read_csv(
            path, usecols=["zipcode", "agi_stub", "N1", "N00900"],
            dtype={"zipcode": str}, chunksize=400_000,
            encoding="latin-1"):
        tot = chunk[(chunk["agi_stub"] == 1)
                    & (~chunk["zipcode"].isin(["0", "00000", "99999"]))]
        out.setdefault("n1", []).append(
            tot.set_index(tot["zipcode"].str.zfill(5))["N1"])
        out.setdefault("bus", []).append(
            tot.set_index(tot["zipcode"].str.zfill(5))["N00900"])
    return (pd.concat(out["n1"]).astype(float),
            pd.concat(out["bus"]).astype(float))


def align_counts(series, zctas):
    """Counts aligned to the study frame; NaN where the source has no
    row for the ZCTA's code."""
    return series.reindex(zctas).to_numpy(dtype=float)


# ------------------------------------------------------------- metrics

def top_decile_overlap(pred, obs):
    k = max(1, int(round(0.10 * len(pred))))
    top_p = set(np.argsort(pred)[-k:].tolist())
    top_o = set(np.argsort(obs)[-k:].tolist())
    return len(top_p & top_o) / k


def grade(pred, obs):
    err = pred - obs
    return {
        "rmse": float(np.sqrt(np.mean(err ** 2))),
        "mae": float(np.mean(np.abs(err))),
        "spearman": float(pd.Series(pred).corr(pd.Series(obs),
                                               method="spearman")),
        "top_decile_overlap": float(top_decile_overlap(pred, obs)),
    }


# ------------------------------------------------------------- fitting

def make_outcomes(df, counts, fit_mask):
    return pd.DataFrame({
        "zcta": df["zcta"].to_numpy(), "product": "bench",
        "sampled": fit_mask,
        "sessions": 0, "add_to_carts": 0,
        "orders": np.where(np.isnan(counts), 0.0, counts),
        "exposure_days": np.where(fit_mask, 365, 0),
        "orders_annualized": np.where(np.isnan(counts), 0.0, counts),
    })


def fit_architecture(df, Z, W, counts, sample_mask, rng):
    """Fit Layer 1 + Fay-Herriot + Layer 2 on counts[sample_mask].
    Returns predictions/intervals for every ZCTA plus fit metadata."""
    has = ~np.isnan(counts)
    fit_mask = sample_mask & has
    oc = make_outcomes(df, counts, fit_mask)
    households = df["households"].to_numpy(float)

    fits, best, sample = layer1.fit_all_models(df, Z, oc, W)
    pred_ols = layer1.predict_all("OLS", fits["OLS"], df, Z, W)
    pred_best = layer1.predict_all(best, fits[best], df, Z, W)

    X_all = np.column_stack([np.ones(len(df)), Z])
    cov = fits[best]["cov"][:X_all.shape[1], :X_all.shape[1]]
    cov_diag = np.clip(
        np.einsum("ij,jk,ik->i", X_all, cov, X_all), 0.0, 2.0)
    orders_s = counts[fit_mask]
    fh = layer1.fay_herriot(
        pred_best[fit_mask], sample["y"], orders_s,
        households[fit_mask], cov_diag_sample=cov_diag[fit_mask])
    est = pred_best.copy()
    var = fh["sigma2_u"] + cov_diag
    est[fit_mask] = fh["est_sample"]
    var[fit_mask] = fh["var_sample"]
    half = 1.96 * np.sqrt(np.clip(var, 1e-6, None))

    # Layer 2: cross-fitted Layer 1 predictions as the spatial feature,
    # identical spatial features and GBM parameters as the pipeline.
    feature_pred = pred_best.copy()
    feature_pred[fit_mask] = layer2._crossfit_predictions(
        df, Z, W, oc, fit_mask, rng)
    Xfeat = layer2._spatial_features(Z, W, feature_pred)
    y_all = np.log((np.where(np.isnan(counts), 0.0, counts) + 0.5)
                   / households)
    from sklearn.ensemble import HistGradientBoostingRegressor
    Xs, ys = Xfeat[fit_mask], y_all[fit_mask]
    perm = rng.permutation(len(Xs))
    cut = int(0.75 * len(Xs))
    tr, va = perm[:cut], perm[cut:]
    val_model = HistGradientBoostingRegressor(
        random_state=config.SEED, **layer2.GBM_PARAMS).fit(
            Xs[tr], ys[tr])
    val_rmse = float(np.sqrt(np.mean(
        (val_model.predict(Xs[va]) - ys[va]) ** 2)))
    gbm = HistGradientBoostingRegressor(
        random_state=config.SEED, **layer2.GBM_PARAMS).fit(Xs, ys)
    pred_gbm = gbm.predict(Xfeat)

    # diagnostics on the observed-sample OLS residuals
    mi, mi_p = common.morans_i(fits["OLS"]["resid"], sample["W"], rng)
    lm = lm_tests(sample["X"], sample["y"],
                  sample["W_dense"])

    return {
        "fit_mask": fit_mask, "best_model": best,
        "aic": {k: float(v["aic"]) for k, v in fits.items()},
        "pred_ols": pred_ols, "pred_best": pred_best,
        "fh_est": est, "fh_lo": est - half, "fh_hi": est + half,
        "pred_gbm": pred_gbm, "gbm_val_rmse_sample_holdout": val_rmse,
        "nb_size_hat": fh["nb_size_hat"],
        "sigma2_u": fh["sigma2_u"],
        "gamma_mean": float(fh["gamma"].mean()),
        "moran_i": float(mi), "moran_p": float(mi_p), "lm": lm,
    }


def evaluate(fit, counts, sample_mask, households):
    """Grade against observed log rates on ZCTAs NOT in the canonical
    observed subset (and with an observed outcome)."""
    obs_rate = np.log((counts + 0.5) / households)
    grade_mask = (~sample_mask) & (~np.isnan(counts))
    o = obs_rate[grade_mask]
    res = {"n_graded": int(grade_mask.sum())}
    for name, pred in (("ols", fit["pred_ols"]),
                       ("best_spatial", fit["pred_best"]),
                       ("fay_herriot", fit["fh_est"]),
                       ("geoai", fit["pred_gbm"])):
        res[name] = grade(pred[grade_mask], o)
    fh_o = fit["fh_est"][grade_mask]
    res["agreement_fh_vs_geoai"] = {
        "pearson": float(np.corrcoef(fh_o, fit["pred_gbm"][grade_mask])[0, 1]),
        "spearman": float(pd.Series(fh_o).corr(
            pd.Series(fit["pred_gbm"][grade_mask]), method="spearman")),
        "top_decile_overlap": float(top_decile_overlap(
            fit["pred_gbm"][grade_mask], fh_o)),
    }
    inside = ((o >= fit["fh_lo"][grade_mask])
              & (o <= fit["fh_hi"][grade_mask]))
    res["fh_interval_behaviour"] = {
        "coverage_vs_observed_nominal95": float(inside.mean()),
        "mean_width_log": float(np.mean(
            fit["fh_hi"][grade_mask] - fit["fh_lo"][grade_mask])),
    }
    return res, grade_mask


def main():
    rng_master = np.random.default_rng(config.SEED)
    df = common.load_features()
    df = common.add_model_features(df)
    Z, _ = common.standardize(df)
    W = common.build_weights(df)
    households = df["households"].to_numpy(float)
    zctas = df["zcta"].to_numpy()

    obs = pd.read_csv(os.path.join(REPO, "results",
                                   "observed_sample.csv"),
                      dtype={"zcta": str})
    sm = obs[obs["product"] == "steamers"].set_index("zcta")["sampled"]
    sample_mask = sm.reindex(zctas).fillna(False).to_numpy(bool)

    zbp22 = align_counts(load_zbp(2022), zctas)
    zbp19 = align_counts(load_zbp(2019), zctas)
    soi_n1_s, soi_bus_s = load_soi22()
    soi_n1 = align_counts(soi_n1_s, zctas)
    soi_bus = align_counts(soi_bus_s, zctas)

    results = {"sample_size_canonical": int(sample_mask.sum()),
               "n_zctas": int(len(df)), "outcomes": {}}
    pred_store = {"zcta": zctas, "region": df["region"].to_numpy(),
                  "in_canonical_sample": sample_mask}

    for label, counts in (("zbp22_establishments", zbp22),
                          ("soi22_returns", soi_n1),
                          ("soi22_business_returns", soi_bus)):
        rng = np.random.default_rng(config.SEED)
        fit = fit_architecture(df, Z, W, counts, sample_mask, rng)
        ev, _gm = evaluate(fit, counts, sample_mask, households)
        ev.update({
            "n_with_outcome": int((~np.isnan(counts)).sum()),
            "n_fit": int(fit["fit_mask"].sum()),
            "n_zero_counts": int((counts == 0).sum()),
            "best_model": fit["best_model"], "aic": fit["aic"],
            "nb_size_hat": fit["nb_size_hat"],
            "sigma2_u": fit["sigma2_u"],
            "gamma_mean": fit["gamma_mean"],
            "gbm_val_rmse_sample_holdout":
                fit["gbm_val_rmse_sample_holdout"],
            "moran_i": fit["moran_i"], "moran_p": fit["moran_p"],
            "lm": fit["lm"],
        })
        results["outcomes"][label] = ev
        if label == "zbp22_establishments":
            pred_store["obs_log_rate_zbp22"] = np.log(
                (counts + 0.5) / households)
            pred_store["fh_est_zbp22"] = fit["fh_est"]
            pred_store["fh_lo_zbp22"] = fit["fh_lo"]
            pred_store["fh_hi_zbp22"] = fit["fh_hi"]
            pred_store["geoai_pred_zbp22"] = fit["pred_gbm"]
        print(f"{label}: fit={ev['n_fit']} graded={ev['n_graded']} "
              f"best={ev['best_model']} size={ev['nb_size_hat']:.2f} "
              f"FH rmse={ev['fay_herriot']['rmse']:.3f} "
              f"GBM rmse={ev['geoai']['rmse']:.3f}", flush=True)

    # temporal transfer: fit ZBP 2019, grade on ZBP 2022
    rng = np.random.default_rng(config.SEED)
    fit19 = fit_architecture(df, Z, W, zbp19, sample_mask, rng)
    ev_t, _ = evaluate(fit19, zbp22, sample_mask, households)
    ev_t.update({"fit_outcome": "zbp19_establishments",
                 "grade_outcome": "zbp22_establishments",
                 "best_model": fit19["best_model"],
                 "nb_size_hat": fit19["nb_size_hat"],
                 "sigma2_u": fit19["sigma2_u"]})
    results["temporal_transfer_zbp19_to_zbp22"] = ev_t
    print(f"temporal 19->22: FH rmse={ev_t['fay_herriot']['rmse']:.3f} "
          f"GBM rmse={ev_t['geoai']['rmse']:.3f}", flush=True)

    out_json = os.path.join(ROOT, "results", "benchmark_results.json")
    with open(out_json, "w") as fh:
        json.dump(results, fh, indent=2)
    pd.DataFrame(pred_store).to_csv(
        os.path.join(ROOT, "results", "benchmark_predictions.csv"),
        index=False)
    print(f"wrote {out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
