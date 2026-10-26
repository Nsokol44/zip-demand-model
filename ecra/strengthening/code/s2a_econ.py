"""
STRENGTHENING TEST (a), econometric arm -- the fifth Tier 2 outcome
(design note 2026-10-26): ZBP 2022 NAICS 454110 (electronic shopping
and mail-order houses) establishment counts per household, graded on
the identical Tier 2 protocol as the four existing evaluations
(benchmark.fit_architecture / benchmark.evaluate, unmodified; the
same 24 sample draws; steamers mask per draw, replicate 0 = the
canonical 447-area sample).

Outcome construction: a study ZCTA with no 454110 row in the ZBP
2022 detail file has an observed count of zero (no establishment
recorded); the outcome-present mask is presence in the ZBP 2022
totals file, exactly as for the totals outcome.

Run:  python s2a_econ.py
Outputs: ../results/test_a_econ.json,
         ../results/test_a_predictions.csv (per-draw layer
         estimates + Fay-Herriot intervals for this outcome)
"""
import sys, os, json, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
STR = os.path.join(HERE, "..", "..", "..", "..", "strengthening-2026-10-18", "code")
REPO = os.path.expanduser("~/workspace/zip-demand-model")
for p in (STR, REPO):
    sys.path.insert(0, p)

import common, config  # noqa: E402
import layer1_econometrics as layer1  # noqa: E402
import benchmark as bm  # noqa: E402

OUT = os.path.join(HERE, "..", "results")
os.makedirs(OUT, exist_ok=True)
R_DRAWS = 24
LAYERS = ("ols", "best_spatial", "fay_herriot", "geoai")
DETAIL_ZIP = os.path.join(REPO, "data", "zbp22detail.zip")


def load_eshop_counts(zctas):
    """NAICS 454110 establishment counts aligned to the frame.
    Returns counts (NaN where the ZCTA is absent from ZBP 2022
    totals, i.e. no ZBP record at all; 0 where ZBP-covered with no
    electronic-shopping establishment)."""
    parts = []
    for chunk in pd.read_csv(DETAIL_ZIP, compression="zip",
                             usecols=["zip", "naics", "est"],
                             dtype={"zip": str, "naics": str},
                             chunksize=400_000):
        sub = chunk[chunk["naics"] == "454110"]
        if len(sub):
            parts.append(sub[["zip", "est"]])
    det = pd.concat(parts)
    det["est"] = pd.to_numeric(det["est"], errors="raise")
    by_zip = det.groupby(det["zip"].str.zfill(5))["est"].sum()
    totals = bm.load_zbp(2022)                      # presence mask
    present = totals.reindex(pd.Index(zctas).astype(str).str.zfill(5))
    counts = by_zip.reindex(present.index).to_numpy(float)
    counts = np.where(np.isnan(counts), 0.0, counts)
    counts = np.where(np.isnan(present.to_numpy(float)), np.nan, counts)
    return counts


def replicate_mask(df, Z, W, r):
    rng = np.random.default_rng(config.SEED + 1000 * r)
    _truth, oc = layer1.simulate_truth(df, Z, W, "steamers", rng)
    return oc["sampled"].to_numpy(bool)


def strict(o):
    if isinstance(o, dict):
        return {k: strict(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [strict(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def main():
    t0 = time.time()
    df = common.load_features(); df = common.add_model_features(df)
    Z, _ = common.standardize(df)
    W = common.build_weights(df)
    households = df["households"].to_numpy(float)
    zctas = df["zcta"].to_numpy()
    counts = load_eshop_counts(zctas)
    print(f"eshop outcome: present={int((~np.isnan(counts)).sum())} "
          f"nonzero={int((counts > 0).sum())} "
          f"zero_share={float(np.mean(counts == 0)):.3f}", flush=True)

    ckpt = os.path.join(OUT, "test_a_econ_partial.json")
    records = []
    pred_frames = []
    if os.path.exists(ckpt):
        records = json.load(open(ckpt))
    done = {rec["draw"] for rec in records}

    for r in range(R_DRAWS):
        if r in done:
            continue
        mask = replicate_mask(df, Z, W, r)
        rng = np.random.default_rng(config.SEED + 1000 * r)
        fit = bm.fit_architecture(df, Z, W, counts, mask, rng)
        ev, _ = bm.evaluate(fit, counts, mask, households)
        rec = {"draw": r, "seed": config.SEED + 1000 * r,
               "n_sampled": int(mask.sum()),
               "n_graded": ev["n_graded"],
               "best_model": fit["best_model"],
               "nb_size_hat": fit["nb_size_hat"],
               "sigma2_u": fit["sigma2_u"],
               "gamma_mean": fit["gamma_mean"],
               "rmse": {k: ev[k]["rmse"] for k in LAYERS},
               "spearman": {k: ev[k]["spearman"] for k in LAYERS},
               "top_decile_overlap":
                   {k: ev[k]["top_decile_overlap"] for k in LAYERS},
               "fh_coverage":
                   ev["fh_interval_behaviour"]
                     ["coverage_vs_observed_nominal95"],
               "fh_mean_width":
                   ev["fh_interval_behaviour"]["mean_width_log"],
               "agreement_fh_geoai_top_decile":
                   ev["agreement_fh_vs_geoai"]["top_decile_overlap"]}
        records.append(rec)
        records.sort(key=lambda d: d["draw"])
        with open(ckpt, "w") as fh:
            json.dump(strict(records), fh, allow_nan=False)
        pred_frames.append(pd.DataFrame({
            "draw": r, "zcta": zctas,
            "in_sample": mask,
            "has_outcome": ~np.isnan(counts),
            "counts": counts,
            "obs_log_rate": np.log((np.where(np.isnan(counts), 0.0,
                                             counts) + 0.5) / households),
            "ols": fit["pred_ols"], "best_spatial": fit["pred_best"],
            "fay_herriot": fit["fh_est"], "fh_lo": fit["fh_lo"],
            "fh_hi": fit["fh_hi"], "geoai": fit["pred_gbm"]}))
        print(f"draw {r:2d}: FH rmse={rec['rmse']['fay_herriot']:.3f} "
              f"GeoAI={rec['rmse']['geoai']:.3f} "
              f"cov={rec['fh_coverage']:.3f} "
              f"({time.time()-t0:.0f}s)", flush=True)
    if pred_frames:
        pf = os.path.join(OUT, "test_a_predictions_new.csv")
        pd.concat(pred_frames).to_csv(pf, index=False)
        if os.path.exists(os.path.join(OUT, "test_a_predictions.csv")):
            old = pd.read_csv(os.path.join(OUT, "test_a_predictions.csv"))
            new = pd.read_csv(pf)
            pd.concat([old, new]).drop_duplicates(
                subset=["draw", "zcta"]).to_csv(
                os.path.join(OUT, "test_a_predictions.csv"), index=False)
            os.remove(pf)
        else:
            os.rename(pf, os.path.join(OUT, "test_a_predictions.csv"))

    def agg(get):
        v = np.array([get(row) for row in records], dtype=float)
        return {"mean": float(v.mean()), "sd": float(v.std()),
                "min": float(v.min()), "max": float(v.max())}
    summary = {
        "rmse": {k: agg(lambda row, k=k: row["rmse"][k]) for k in LAYERS},
        "spearman": {k: agg(lambda row, k=k: row["spearman"][k])
                     for k in LAYERS},
        "top_decile_overlap":
            {k: agg(lambda row, k=k: row["top_decile_overlap"][k])
             for k in LAYERS},
        "fh_coverage": agg(lambda row: row["fh_coverage"]),
        "fh_mean_width": agg(lambda row: row["fh_mean_width"]),
        "geoai_beats_fh_share":
            float(np.mean([row["rmse"]["geoai"] < row["rmse"]["fay_herriot"]
                           for row in records])),
        "geoai_margin_vs_fh":
            agg(lambda row: row["rmse"]["fay_herriot"]
                - row["rmse"]["geoai"]),
        "agreement_fh_geoai_top_decile":
            agg(lambda row: row["agreement_fh_geoai_top_decile"]),
        "best_model_share": {
            m: float(np.mean([row["best_model"] == m for row in records]))
            for m in ("OLS", "SAR", "SEM", "SDM")},
        "nb_size_hat": agg(lambda row: row["nb_size_hat"]),
        "sigma2_u": agg(lambda row: row["sigma2_u"]),
    }
    out = {"outcome": "zbp22_eshop_naics454110", "R_draws": R_DRAWS,
           "summary": summary, "records": records}
    path = os.path.join(OUT, "test_a_econ.json")
    with open(path, "w") as fh:
        json.dump(strict(out), fh, indent=1, allow_nan=False)
    print("wrote", path, flush=True)


if __name__ == "__main__":
    main()
