"""
STRENGTHENING TEST (a), Bayesian arm -- the Bayesian layer of
Section 6 fitted to the new Tier 2 outcome (ZBP 2022 NAICS 454110
establishments) on the same 24 draws and masks as the econometric
arm (design note 2026-10-26). Mirrors run_bayes_experiments'
stage_tier2 exactly: checkpointed fits (tag
tier2_r{r}_zbp22_eshop), eigen-truncated ICAR top-300, shipped
priors, grading on held-out ZCTAs against the observed log rate.

Engineering rule (BAYES_DESIGN.md, restated in the design note):
draw 0 is timed; if its fit exceeds 15 minutes the run stops and
reports the blocker.

Run with the adaptation venv:
  ijec-adaptation/code/.venv/bin/python s2a_bayes.py
Outputs: fits + grading JSONs in ijec-adaptation/results/fits
(checkpoint convention of record), predictions in
ijec-adaptation/results/predictions, and
../results/test_a_bayes.json (collected grading summary).
"""
import sys, os, json, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ADAPT = os.path.join(HERE, "..", "..", "..")
CODE = os.path.join(ADAPT, "code")
STR = os.path.normpath(os.path.join(ADAPT, "..", "strengthening-2026-10-18", "code"))
for p in (CODE, STR):
    sys.path.insert(0, p)

import run_bayes_experiments as rbe  # noqa: E402
import bayes_core as bc  # noqa: E402
import benchmark as bm  # noqa: E402
sys.path.insert(0, HERE)
from s2a_econ import load_eshop_counts  # noqa: E402

OUT = os.path.join(HERE, "..", "results")
os.makedirs(OUT, exist_ok=True)
EV = "zbp22_eshop"


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
    counts = load_eshop_counts(rbe._ZCTA)
    has_all = ~np.isnan(counts)
    counts_f = np.where(np.isnan(counts), 0.0, counts)
    obs = np.log((counts + 0.5) / rbe._HH)
    gradings = []
    for r in range(24):
        mask = rbe.tier2_mask(r)
        fit_mask = mask & has_all
        tag = f"tier2_r{r}_{EV}"
        t0 = time.time()
        summ = rbe.do_bayes_fit(tag, counts_f, fit_mask, bc.rep_seed(r))
        if summ is None:
            summ = json.load(open(os.path.join(rbe.FITS, f"{tag}.json")))
        runtime = float(summ.get("runtime_sec", time.time() - t0))
        if r == 0 and runtime > 900:
            msg = (f"BLOCKER: draw 0 Bayes fit took {runtime:.0f}s "
                   f"(> 15 min rule). Stopping per design note.")
            print(msg, flush=True)
            with open(os.path.join(OUT, "test_a_bayes_BLOCKER.txt"),
                      "w") as fh:
                fh.write(msg + "\n")
            return
        arr = rbe.load_fit_arrays(tag)
        gm = (~mask) & has_all
        est, lo, hi = arr["theta_mean"], arr["theta_lo"], arr["theta_hi"]
        g = bm.grade(est[gm], obs[gm])
        g.update({
            "n_graded": int(gm.sum()),
            "interval_behaviour_vs_observed": float(np.mean(
                (obs[gm] >= lo[gm]) & (obs[gm] <= hi[gm]))),
            "mean_width": float(np.mean(hi[gm] - lo[gm])),
        })
        sp = os.path.join(rbe.FITS, f"{tag}_grading.json")
        if not os.path.exists(sp):
            bc.strict_json_dump({"replicate": r, "evaluation": EV,
                                 "grading_heldout": g}, sp)
        rbe.write_predictions_csv(tag, rbe._ZCTA, obs,
                                  [("bayes", est, lo, hi)])
        gradings.append({"draw": r, "runtime_sec": runtime,
                         "converged": bool(summ.get("converged", False)),
                         **g})
        print(f"[bayes eshop] r{r}: rmse={g['rmse']:.3f} "
              f"beh={g['interval_behaviour_vs_observed']:.3f} "
              f"runtime={runtime:.0f}s", flush=True)
    def agg(k):
        v = np.array([g[k] for g in gradings], float)
        return {"mean": float(v.mean()), "sd": float(v.std())}
    out = {"evaluation": EV,
           "summary": {"rmse": agg("rmse"), "mae": agg("mae"),
                       "spearman": agg("spearman"),
                       "interval_behaviour":
                           agg("interval_behaviour_vs_observed"),
                       "mean_width": agg("mean_width"),
                       "converged_share": float(np.mean(
                           [g["converged"] for g in gradings]))},
           "records": gradings}
    path = os.path.join(OUT, "test_a_bayes.json")
    with open(path, "w") as fh:
        json.dump(strict(out), fh, indent=1, allow_nan=False)
    print("wrote", path, flush=True)


if __name__ == "__main__":
    main()
