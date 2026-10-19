"""
roughness.py — A4 + A5 (2026-10-18 review).

A5: Figure 5's caption claimed the observed surface is "visibly
rougher" than the simulated one, but the maps plot different
quantities on pooled classes, so the visual contrast is mostly
level. This script measures roughness instead of asserting it:
for each surface — Tier 1 DGP truths (steamers, trio), the three
observed 2022 log-rate surfaces, and a rough-DGP truth (below) —
it reports Moran's I of the surface itself and an empirical
semivariogram (binned, from 2M seeded random pairs), summarised by
the short-lag semivariance share gamma(0-15 km) / sill and a
practical range.

A4: the v2 text stated as a result that "the ordering is a
property of the surface". Test: rerun the Tier 1 architecture
(benchmark.fit_architecture, unmodified estimators) on (i) the
shipped smooth DGP and (ii) a ROUGH variant that adds an iid
local component ell ~ N(0, sd(u)) to the latent surface — half
the latent spatial variance at the single-ZCTA scale — over 8
draws each (seeds config.SEED + 1000*r), grading every layer
against the known truth. If the GeoAI layer's Tier 1 deficit
shrinks or reverses on the rough DGP while roughness statistics
place the real surfaces at the rough end, the surface hypothesis
earns its wording; otherwise it is demoted to a hypothesis in
the text.

Writes ../results/roughness.json.
"""

import json
import os
import sys
import time

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy import sparse
from scipy.sparse import linalg as spla

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
REPO = os.path.abspath(os.path.join(HERE, ".."))  # repo root (Tier 1 pipeline)
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

import common          # noqa: E402
import config          # noqa: E402
import layer1_econometrics as layer1   # noqa: E402
import benchmark as bm                 # noqa: E402

BINS_KM = np.array([0, 15, 30, 60, 120, 240, 400], dtype=float)


def projected_coords(df):
    tr = Transformer.from_crs(4326, 5070, always_xy=True)
    x, y = tr.transform(df["lon"].to_numpy(float),
                        df["lat"].to_numpy(float))
    return np.column_stack([x, y]) / 1000.0  # km


REGIONS = None  # set in main(); pairs are drawn WITHIN a region
# only — the study frame is two clusters ~1,300 km apart (Southeast
# + NYC metro), and cross-region pairs would confound the
# semivariogram with the between-region level contrast.


def semivariogram(values, coords, rng, n_pairs=2_000_000):
    idx = np.where(~np.isnan(values))[0]
    v = values[idx]
    c = coords[idx]
    reg = REGIONS[idx]
    i = rng.integers(0, len(idx), n_pairs)
    j = rng.integers(0, len(idx), n_pairs)
    keep = (i != j) & (reg[i] == reg[j])
    i, j = i[keep], j[keep]
    d = np.sqrt(((c[i] - c[j]) ** 2).sum(axis=1))
    keep = d <= 400
    d, i, j = d[keep], i[keep], j[keep]
    sq = 0.5 * (v[i] - v[j]) ** 2
    b = np.digitize(d, BINS_KM) - 1
    gam, cnt, ctr = [], [], []
    for k in range(len(BINS_KM) - 1):
        m = b == k
        gam.append(float(sq[m].mean()) if m.sum() else None)
        cnt.append(int(m.sum()))
        ctr.append(float(d[m].mean()) if m.sum() else None)
    var = float(np.var(v))
    plateau = np.nanmean([g for g in gam[-2:] if g is not None])
    short_lag_ratio = (gam[0] / var if gam[0] is not None
                       else None)
    rng90 = None
    for g, c_ in zip(gam, ctr):
        if g is not None and g >= 0.9 * plateau:
            rng90 = c_
            break
    return {"variance": var, "bin_centres_km": ctr,
            "gamma": gam, "pairs_per_bin": cnt,
            "short_lag_share": (gam[0] / plateau
                                if gam[0] is not None else None),
            "short_lag_gamma_over_variance": short_lag_ratio,
            "practical_range_km": rng90}


def surface_stats(values, W, coords, rng):
    has = ~np.isnan(values)
    W_sub = common.weights_for_subset(W, has)
    mi, mi_p = common.morans_i(values[has], W_sub, rng)
    return {"n": int(has.sum()), "moran_i_surface": float(mi),
            "moran_p": float(mi_p),
            "semivariogram": semivariogram(values, coords, rng)}


def simulate_truth_rough(df, Z, W, product, rng):
    """Shipped DGP + iid local component with sd matched to the
    smooth SAR component's sd (documented variant for A4)."""
    dgp = config.DGP
    Z_dgp = np.clip(Z, -config.DGP_FEATURE_CLIP,
                    config.DGP_FEATURE_CLIP)
    beta = np.array([dgp["beta"][product][f]
                     for f in common.FEATURES])
    eta = dgp["intercept"][product] + Z_dgp @ beta
    n = len(df)
    eps = rng.normal(0.0, dgp["sigma"], n)
    A = sparse.eye(n, format="csc") - dgp["rho"] * W.tocsc()
    u = spla.spsolve(A, eps)
    ell = rng.normal(0.0, float(np.std(u)), n)
    true_log_rate = eta + u + ell
    households = df["households"].to_numpy(float)
    true_mu = households * np.exp(true_log_rate)
    sampled = np.zeros(n, dtype=bool)
    income = pd.Series(df["median_hh_income"].to_numpy(float))
    income = income.fillna(
        income.groupby(df["region"].to_numpy())
        .transform("median")).to_numpy()
    for region in config.REGIONS:
        m = (df["region"] == region).to_numpy()
        if m.sum() == 0:
            continue
        pct = pd.Series(income[m]).rank(pct=True).to_numpy()
        terc = np.minimum((pct * 3).astype(int), 2)
        idx = np.where(m)[0]
        for t in range(3):
            cell = idx[terc == t]
            if len(cell) == 0:
                continue
            take = max(1, int(round(config.SAMPLE_FRACTION
                                    * len(cell))))
            sampled[rng.choice(cell, size=take,
                               replace=False)] = True
    sidx = np.where(sampled)[0]
    lam = households[sidx] * dgp["test_session_rate"]
    sessions = rng.poisson(lam)
    ubeta = np.array([dgp["uptake_beta"][f]
                      for f in common.FEATURES])
    true_uptake = common.sigmoid(dgp["uptake_intercept"]
                                 + Z_dgp @ ubeta)
    _atc = rng.binomial(sessions, true_uptake[sidx])
    size = dgp["nb_size"]
    p = size / (size + true_mu[sidx])
    orders = np.zeros(n, dtype=float)
    orders[sidx] = rng.negative_binomial(size, p)
    return true_log_rate, sampled, orders


def grade_vs_truth(fit, truth, sampled):
    out = {}
    for name, pred in (("ols", fit["pred_ols"]),
                       ("best_spatial", fit["pred_best"]),
                       ("fay_herriot", fit["fh_est"]),
                       ("geoai", fit["pred_gbm"])):
        out[name] = {
            "rmse_all": float(np.sqrt(np.mean((pred - truth) ** 2))),
            "rmse_unsampled": float(np.sqrt(np.mean(
                (pred[~sampled] - truth[~sampled]) ** 2))),
        }
    return out


def main():
    t0 = time.time()
    df = common.load_features()
    df = common.add_model_features(df)
    Z, _ = common.standardize(df)
    W = common.build_weights(df)
    households = df["households"].to_numpy(float)
    zctas = df["zcta"].to_numpy()
    coords = projected_coords(df)
    global REGIONS
    REGIONS = df["region"].to_numpy()
    rng_stats = np.random.default_rng(config.SEED)

    truth = pd.read_csv(os.path.join(REPO, "results",
                                     "grading_truth.csv"),
                        dtype={"zcta": str}).set_index("zcta")
    zbp22 = bm.align_counts(bm.load_zbp(2022), zctas)
    soi_n1_s, soi_bus_s = bm.load_soi22()
    soi_n1 = bm.align_counts(soi_n1_s, zctas)
    soi_bus = bm.align_counts(soi_bus_s, zctas)

    surfaces = {
        "sim_steamers_truth":
            truth["true_log_rate_steamers"]
            .reindex(zctas).to_numpy(float),
        "sim_trio_truth":
            truth["true_log_rate_trio"]
            .reindex(zctas).to_numpy(float),
        "obs_zbp22_log_rate": np.log((zbp22 + 0.5) / households),
        "obs_soi_returns_log_rate":
            np.log((soi_n1 + 0.5) / households),
        "obs_soi_business_log_rate":
            np.log((soi_bus + 0.5) / households),
    }
    # canonical-seed rough truth for the stats table
    rng_r = np.random.default_rng(config.SEED)
    rough_truth, _m, _o = simulate_truth_rough(
        df, Z, W, "steamers", rng_r)
    surfaces["sim_rough_variant_truth"] = rough_truth

    stats_out = {}
    for label, vals in surfaces.items():
        stats_out[label] = surface_stats(vals, W, coords, rng_stats)
        s = stats_out[label]
        print(f"{label}: Moran I={s['moran_i_surface']:.3f} "
              f"short-lag share="
              f"{s['semivariogram']['short_lag_share']:.3f} "
              f"range={s['semivariogram']['practical_range_km']}",
              flush=True)

    # ---- A4: ordering on smooth vs rough DGP, 8 draws each ------
    R = 8
    dgp_out = {"smooth": [], "rough": []}
    for r in range(R):
        seed = config.SEED + 1000 * r
        rng = np.random.default_rng(seed)
        _t, oc = layer1.simulate_truth(df, Z, W, "steamers", rng)
        counts = oc["orders_annualized"].to_numpy(float)
        mask = oc["sampled"].to_numpy(bool)
        truth_s = _t["true_log_rate"]
        fit = bm.fit_architecture(df, Z, W, counts, mask,
                                  np.random.default_rng(seed))
        dgp_out["smooth"].append(grade_vs_truth(fit, truth_s, mask))

        rng = np.random.default_rng(seed)
        truth_r, mask_r, orders_r = simulate_truth_rough(
            df, Z, W, "steamers", rng)
        fit = bm.fit_architecture(df, Z, W, orders_r, mask_r,
                                  np.random.default_rng(seed))
        dgp_out["rough"].append(grade_vs_truth(fit, truth_r, mask_r))
        gs, gr = dgp_out["smooth"][-1], dgp_out["rough"][-1]
        print(f"draw {r}: smooth FH={gs['fay_herriot']['rmse_all']:.3f}"
              f" GeoAI={gs['geoai']['rmse_all']:.3f} | rough FH="
              f"{gr['fay_herriot']['rmse_all']:.3f} GeoAI="
              f"{gr['geoai']['rmse_all']:.3f} ({time.time()-t0:.0f}s)",
              flush=True)

    def agg(rows, layer, key):
        v = np.array([row[layer][key] for row in rows])
        return {"mean": float(v.mean()), "sd": float(v.std())}
    summary = {}
    for variant, rows in dgp_out.items():
        summary[variant] = {
            layer: {key: agg(rows, layer, key)
                    for key in ("rmse_all", "rmse_unsampled")}
            for layer in ("ols", "best_spatial", "fay_herriot",
                          "geoai")}
        summary[variant]["geoai_beats_fh_share_all"] = float(np.mean(
            [row["geoai"]["rmse_all"] < row["fay_herriot"]["rmse_all"]
             for row in rows]))
    out = {"surfaces": stats_out, "dgp_ordering": summary,
           "dgp_draws": dgp_out, "R_dgp_draws": R}
    path = os.path.join(ROOT, "results", "roughness.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"wrote {path} in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
