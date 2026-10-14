"""
layer2_geoai.py — LAYER 2: GeoAI estimation.

Gradient-boosting demand and uptake models trained on the SAME
observed sample Layer 1 uses, then predicted for every ZCTA.

Leakage discipline (important): features are the ACS covariates plus
spatial features that exist for every ZIP at prediction time —
neighbor means of COVARIATES (W @ Z) and neighbor means of the Layer 1
MODEL's predictions (W @ fitted values). Neighbor OUTCOMES are never
used: for unsampled ZIPs they do not exist in reality, and using them
in-sample would fabricate accuracy.

Uptake = the funnel propensity P(session -> add-to-cart), observed in
the sample as add_to_carts / sessions, modeled with a
session-weighted boosting regressor; reported as a [0,1] score with
quantile intervals.

Clusters: k-means on standardized covariates per region (~12-20),
with a geographic-coherence statistic (share of each ZIP's kNN
neighbors assigned to the same cluster).
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance

import common
import config
import layer1_econometrics as layer1


def _crossfit_predictions(df, Z, W, outcomes, sampled, rng):
    """Out-of-fold Layer 1 predictions for the sampled rows (2-fold).

    The Layer 2 spatial feature is W @ (Layer 1 predictions). If the
    full-sample Layer 1 fit supplied the training rows' features,
    each training row's own outcome would leak into its features
    through that fit. Cross-fitting removes the leak: a sampled row's
    feature prediction comes from a Layer 1 model that never saw it.
    Unsampled rows keep the full-sample model's predictions.
    """
    full_pred = None
    cross = np.zeros(len(df))
    sidx = np.where(sampled)[0]
    perm = rng.permutation(len(sidx))
    folds = [sidx[perm[: len(perm) // 2]], sidx[perm[len(perm) // 2:]]]
    for fold in folds:
        oc = outcomes.copy()
        keep = sampled.copy()
        keep[fold] = False
        oc["sampled"] = keep
        fits, best, _sample = layer1.fit_all_models(df, Z, oc, W)
        pred = layer1.predict_all(best, fits[best], df, Z, W)
        cross[fold] = pred[fold]
    return cross[sampled]

GBM_PARAMS = dict(max_iter=400, learning_rate=0.06, max_depth=6,
                  min_samples_leaf=20, l2_regularization=1.0)


def _spatial_features(Z, W, model_pred_log_rate):
    WX = np.asarray(W @ Z)
    Wpred = np.asarray(W @ model_pred_log_rate).ravel()
    return np.column_stack([Z, WX, Wpred])


def _feature_names(model_pred_name="W_model_pred"):
    base = list(common.FEATURES)
    return base + [f"W_{f}" for f in base] + [model_pred_name]


def _fit_quantiles(X, y, rng, weights=None):
    point = HistGradientBoostingRegressor(
        random_state=config.SEED, **GBM_PARAMS).fit(
            X, y, sample_weight=weights)
    qs = {}
    for alpha in (0.05, 0.95):
        m = HistGradientBoostingRegressor(
            loss="quantile", quantile=alpha, random_state=config.SEED,
            **GBM_PARAMS).fit(X, y, sample_weight=weights)
        qs[alpha] = m
    return point, qs


def run_layer2(df, Z, W, layer1, rng):
    outcomes = layer1["outcomes"]
    households = df["households"].to_numpy(float)
    out = {"products": {}}

    for product in config.PRODUCTS:
        oc = outcomes[product]
        sampled = oc["sampled"].to_numpy()
        l1 = layer1["products"][product]
        feature_pred = l1["model_pred_log_rate"].copy()
        feature_pred[sampled] = _crossfit_predictions(
            df, Z, W, oc, sampled, rng)
        X_all = _spatial_features(Z, W, feature_pred)
        names = _feature_names()

        orders = oc["orders_annualized"].to_numpy(float)
        y_demand = np.log((orders + 0.5) / households)
        sessions = oc["sessions"].to_numpy(float)
        atc_rate = np.where(sessions > 0,
                            oc["add_to_carts"].to_numpy(float) /
                            np.maximum(sessions, 1), np.nan)

        Xs, ys = X_all[sampled], y_demand[sampled]
        # seeded split for HONEST validation: the validation model is
        # fit on the 75% partition ONLY and scored on the held-out
        # 25%; the production models below are then refit on the
        # full sample. (Fitting on all rows and "validating" on a
        # subset of them would report in-sample fit as validation.)
        perm = rng.permutation(len(Xs))
        cut = int(0.75 * len(Xs))
        tr, va = perm[:cut], perm[cut:]
        val_model = HistGradientBoostingRegressor(
            random_state=config.SEED, **GBM_PARAMS).fit(Xs[tr], ys[tr])
        val_pred = val_model.predict(Xs[va])
        val_rmse = float(np.sqrt(np.mean((val_pred - ys[va]) ** 2)))
        imp = permutation_importance(val_model, Xs[va], ys[va],
                                     n_repeats=5,
                                     random_state=config.SEED)
        importance = sorted(
            ({"feature": names[j],
              "importance": float(imp.importances_mean[j])}
             for j in range(len(names))),
            key=lambda d: -d["importance"])

        point, qs = _fit_quantiles(Xs, ys, rng)
        pred = point.predict(X_all)
        lo = qs[0.05].predict(X_all)
        hi = qs[0.95].predict(X_all)

        # uptake model (session-weighted)
        ok = sampled & (sessions > 0)
        up_point, up_qs = _fit_quantiles(
            X_all[ok], np.clip(atc_rate[ok], 0.001, 0.999), rng,
            weights=sessions[ok])
        uptake = np.clip(up_point.predict(X_all), 0.0, 1.0)
        uptake_lo = np.clip(up_qs[0.05].predict(X_all), 0.0, 1.0)
        uptake_hi = np.clip(up_qs[0.95].predict(X_all), 0.0, 1.0)

        truth = layer1["truth"][product]
        fh_est = l1["fh"]["est_log_rate"]
        agreement = {
            "pearson_vs_layer1": float(np.corrcoef(pred, fh_est)[0, 1]),
            "spearman_vs_layer1": float(
                pd.Series(pred).corr(pd.Series(fh_est),
                                     method="spearman")),
            "top_decile_overlap": float(
                np.mean(np.isin(
                    np.where(pred >= np.quantile(pred, 0.9))[0],
                    np.where(fh_est >= np.quantile(fh_est, 0.9))[0]))),
            "rmse_vs_truth": (float(np.sqrt(np.mean(
                (pred - truth["true_log_rate"]) ** 2)))
                if truth is not None else None),
            "uptake_rmse_vs_truth": (float(np.sqrt(np.mean(
                (uptake - truth["true_uptake"]) ** 2)))
                if truth is not None else None),
            "val_rmse_sample_holdout": val_rmse,
        }
        out["products"][product] = {
            "pred_log_rate": pred, "pred_lo": lo, "pred_hi": hi,
            "uptake": uptake, "uptake_lo": uptake_lo,
            "uptake_hi": uptake_hi,
            "importance": importance, "agreement": agreement,
            "feature_names": names,
        }

    out["clusters"] = build_clusters(df, Z, W, out, layer1)
    return out


def build_clusters(df, Z, W, layer2, layer1):
    """K-means clusters per region on standardized covariates."""
    demo = layer2["products"][config.DEMO_PRODUCT]
    trio = layer2["products"][config.SECOND_PRODUCT]
    cluster_id = np.full(len(df), -1, dtype=int)
    summaries = []
    for region in config.REGIONS:
        m = (df["region"] == region).to_numpy()
        idx = np.where(m)[0]
        k = int(np.clip(round(len(idx) / 300), 12, 20))
        km = KMeans(n_clusters=k, n_init=10, random_state=config.SEED)
        labels = km.fit_predict(Z[m])
        cluster_id[idx] = labels
        label_of = dict(zip(idx.tolist(), labels.tolist()))
        # geographic coherence: share of each ZIP's kNN neighbors
        # carrying the same cluster label (CSR row access, no dense W)
        coh = []
        for i in idx.tolist():
            nbrs = W.indices[W.indptr[i]:W.indptr[i + 1]]
            same = [label_of[j] == label_of[i] for j in nbrs
                    if j in label_of]
            if same:
                coh.append(np.mean(same))
        for c in range(k):
            sel = idx[labels == c]
            summaries.append({
                "region": region, "cluster_id": int(c),
                "n_zctas": int(len(sel)),
                "households": int(df["households"].to_numpy()[sel].sum()),
                "mean_pred_orders_per_hh_yr": float(np.mean(np.exp(
                    demo["pred_log_rate"][sel]))),
                "expected_orders_yr": float(np.sum(
                    np.exp(demo["pred_log_rate"][sel]) *
                    df["households"].to_numpy()[sel])),
                "mean_uptake": float(np.mean(demo["uptake"][sel])),
                "mean_pred_orders_trio": float(np.mean(np.exp(
                    trio["pred_log_rate"][sel]))),
                "mean_renter_share": float(
                    df["renter_share"].to_numpy()[sel].mean()),
                "mean_median_income": float(np.nanmean(
                    df["median_hh_income"].to_numpy()[sel])),
                "coherence": float(np.mean(coh)) if coh else np.nan,
            })
    return {"cluster_id": cluster_id, "summaries": summaries}
