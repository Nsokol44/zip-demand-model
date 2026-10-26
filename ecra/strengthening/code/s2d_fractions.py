"""
STRENGTHENING TEST (d) -- Tier 1 calibration protocol at 4% and 16%
sampling (design note 2026-10-26). Reuses calibration.one_replicate
verbatim (24 replicates, seeds SEED+1000r, B=25 bootstrap worlds);
only config.SAMPLE_FRACTION changes. The 8% numbers of record are
the shipped calibration results; they are not recomputed here.

Run:  python s2d_fractions.py            (both fractions)
      python s2d_fractions.py 0.04       (one fraction)
Outputs: ../results/test_d_frac{pct}.json (per-replicate records +
pooled aggregates in calibration.py's format).
"""
import sys, os, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STR = os.path.join(HERE, "..", "..", "..", "..", "strengthening-2026-10-18", "code")
REPO = os.path.expanduser("~/workspace/zip-demand-model")
for p in (STR, REPO):
    sys.path.insert(0, p)

import common, config  # noqa: E402
import calibration as cal  # noqa: E402

OUT = os.path.join(HERE, "..", "results")
os.makedirs(OUT, exist_ok=True)


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


def agg(records, path):
    vals = [r[path] for r in records if r.get(path) is not None]
    if not vals:
        return None
    v = np.asarray(vals, float)
    return {"mean": float(v.mean()), "sd": float(v.std()),
            "min": float(v.min()), "max": float(v.max())}


AGG_PATHS = (
    "steamers_fh_cov_raw_sampled", "steamers_fh_cov_raw_all",
    "steamers_fh_cov_cal_sampled", "steamers_fh_cov_cal_all",
    "trio_fh_cov_raw_sampled", "trio_fh_cov_raw_all",
    "trio_fh_cov_cal_sampled", "trio_fh_cov_cal_all",
    "steamers_mult", "trio_mult",
    "steamers_rmse_fh", "steamers_rmse_geoai",
    "trio_rmse_fh", "trio_rmse_geoai",
    "moran_reject_share", "lm_error_reject_share",
)


def run_fraction(frac):
    config.SAMPLE_FRACTION = frac
    df = common.load_features(); df = common.add_model_features(df)
    Z, _ = common.standardize(df)
    W = common.build_weights(df)
    households = df["households"].to_numpy(float)
    records = []
    t0 = time.time()
    for r in range(cal.R_REPLICATES):
        records.append(cal.one_replicate(r, df, Z, W, households))
        print(f"frac={frac} rep {r} done ({time.time()-t0:.0f}s)",
              flush=True)
    out = {"sampling_fraction": frac, "R_replicates": cal.R_REPLICATES,
           "B_worlds": cal.B_WORLDS, "master_seed": config.SEED,
           "pooled": {p: agg(records, p) for p in AGG_PATHS},
           "records": records}
    pct = int(round(frac * 100))
    path = os.path.join(OUT, f"test_d_frac{pct}.json")
    with open(path, "w") as fh:
        json.dump(strict(out), fh, indent=1, allow_nan=False)
    print("wrote", path, flush=True)


if __name__ == "__main__":
    fracs = [float(a) for a in sys.argv[1:]] or [0.04, 0.16]
    for f in fracs:
        run_fraction(f)
