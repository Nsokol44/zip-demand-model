"""
STRENGTHENING TEST (b) -- adjusted maximum likelihood Fay-Herriot
variance estimators (design note 2026-10-26).

Estimators of the area variance A (= sigma2_u), psi_i known:
  ML      profile maximum likelihood
  REML    residual maximum likelihood (textbook refit only)
  LL      Li & Lahiri (2010): maximise L(A) * A
  YL      Yoshimori & Lahiri (2014): maximise L(A) *
          arctan( sum_i A/(A+psi_i) )^(1/m)
(verified from the papers: Li & Lahiri, J. Multivariate Anal.
101(4):882-892, adjustment factor A applied to the profile or
residual likelihood; Yoshimori & Lahiri, J. Multivariate Anal.
124:281-294, adjustment arctan[tr(I - B*)]^(1/m) with
B* = diag(psi_i/(A+psi_i)), applied to the residual likelihood --
the profile variants are included alongside.)

Panels:
  b1  Tier 1 estimator swap: shipped construction held fixed
      (predictions, psi, parameter-uncertainty term); only A
      varies. Graded against the DGP truth on sampled areas,
      24 draws x both products. Criteria C-b1 (strictly positive
      in all draws) and C-b2 (mean coverage at least as close to
      95% as the shipped plug-in), per the design note.
  b2  Textbook refit: beta profiled by GLS on [1, Z]; ML, REML,
      LL and YL on both likelihoods; EBLUP intervals from the
      g1 term only.
  bT  Tier 2 panel: all five outcomes (four existing + the new
      electronic-shopping outcome) x 24 draws; held-out interval
      behaviour per estimator under the b1 swap construction.

A method check on a small simulated Fay-Herriot example (m = 30,
true A small) precedes the panels and is recorded in the output:
ML/REML are expected to hit the zero boundary in some
replications; LL and YL must never do so.

Run:  python s2b_aml.py [b1|b2|bt|all]
Outputs: ../results/test_b_aml.json (accumulates per panel)
"""
import sys, os, json, time
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

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
Z95 = 1.959964
LOG_A_GRID = (np.log(1e-8), np.log(50.0))


# ------------------------------------------------------------ likelihoods
def _profile_terms(A, e, psi):
    V = A + psi
    return -0.5 * float(np.sum(np.log(V) + e * e / V))


def _reml_extra(A, X, psi):
    V = A + psi
    XtViX = (X / V[:, None]).T @ X
    sign, logdet = np.linalg.slogdet(XtViX)
    return -0.5 * float(logdet)


def _gls_resid(A, y, X, psi):
    V = A + psi
    XtViX = (X / V[:, None]).T @ X
    beta = np.linalg.solve(XtViX, (X / V[:, None]).T @ y)
    return y - X @ beta, beta


def _adj_log(A, psi, kind):
    if kind == "ll":
        return float(np.log(A))
    if kind == "yl":
        m = len(psi)
        s = float(np.sum(A / (A + psi)))
        return float(np.log(np.arctan(s)) / m)
    return 0.0


def estimate_A(e, psi, X=None, y=None, likelihood="profile"):
    """All estimators for one (e, psi) problem. Returns dict of A
    values; ML/REML boundary hits recorded as 0.0."""
    def neg(logA, adj):
        A = float(np.exp(logA))
        if X is None:
            base = _profile_terms(A, e, psi)
        else:
            ee, _b = _gls_resid(A, y, X, psi)
            base = _profile_terms(A, ee, psi)
            if likelihood == "reml":
                base += _reml_extra(A, X, psi)
        return -(base + _adj_log(A, psi, adj))

    out = {}
    for name, adj in (("ml_or_reml", "none"), ("ll", "ll"),
                      ("yl", "yl")):
        res = minimize_scalar(neg, bounds=LOG_A_GRID, args=(adj,),
                              method="bounded",
                              options={"xatol": 1e-6})
        A_hat = float(np.exp(res.x))
        out[name] = 0.0 if A_hat <= 1e-7 else A_hat
    return out


def coverage_of(est, var, target):
    half = Z95 * np.sqrt(np.clip(var, 1e-12, None))
    return float(np.mean((target >= est - half)
                         & (target <= est + half)))


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


def method_check():
    rng = np.random.default_rng(20261026)
    reps, m = 200, 30
    psi = rng.gamma(2.0, 0.05, size=m) + 0.01
    hits = {"ml": 0, "ll": 0, "yl": 0}
    for _ in range(reps):
        A_true = 0.02
        theta = rng.normal(0, np.sqrt(A_true), size=m)
        y = theta + rng.normal(0, np.sqrt(psi))
        X = np.ones((m, 1))
        e = y - y.mean()
        est = estimate_A(e, psi)
        if est["ml_or_reml"] == 0.0:
            hits["ml"] += 1
        if est["ll"] == 0.0:
            hits["ll"] += 1
        if est["yl"] == 0.0:
            hits["yl"] += 1
    return {"reps": reps, "m": m, "true_A": 0.02,
            "boundary_zero_share": {k: v / reps for k, v in hits.items()}}


# ------------------------------------------------------------ shared setup
def setup():
    df = common.load_features(); df = common.add_model_features(df)
    Z, _ = common.standardize(df)
    W = common.build_weights(df)
    return df, Z, W


def cov_diag_for(fits_best, df, Z):
    X_all = np.column_stack([np.ones(len(df)), Z])
    cov = fits_best["cov"][:X_all.shape[1], :X_all.shape[1]]
    return np.clip(np.einsum("ij,jk,ik->i", X_all, cov, X_all), 0.0, 2.0)


# ------------------------------------------------------------ panel b1 + b2
def panel_tier1():
    df, Z, W = setup()
    households = df["households"].to_numpy(float)
    X_all = np.column_stack([np.ones(len(df)), Z])
    b1, b2 = [], []
    t0 = time.time()
    for r in range(24):
        rng = np.random.default_rng(config.SEED + 1000 * r)
        for product in config.PRODUCTS:
            truth, outcomes = layer1.simulate_truth(df, Z, W, product, rng)
            fits, best, sample = layer1.fit_all_models(df, Z, outcomes, W)
            sampled = sample["mask"]
            pred_best = layer1.predict_all(best, fits[best], df, Z, W)
            cov_diag = cov_diag_for(fits[best], df, Z)
            orders_s = outcomes.loc[sampled, "orders"].to_numpy(float)
            hh_s = households[sampled]
            y_s = sample["y"]
            pred_s = pred_best[sampled]
            cov_s = cov_diag[sampled]
            fh = layer1.fay_herriot(pred_s, y_s, orders_s, hh_s, cov_s)
            psi = fh["psi"]
            e = y_s - pred_s
            truth_s = truth["true_log_rate"][sampled]
            ests = estimate_A(e, psi)
            row = {"draw": r, "product": product,
                   "A_shipped": fh["sigma2_u"],
                   "A_ml": ests["ml_or_reml"], "A_ll": ests["ll"],
                   "A_yl": ests["yl"], "coverage": {}, "width": {}}
            for name, A in (("shipped", fh["sigma2_u"]),
                            ("ml", ests["ml_or_reml"]),
                            ("ll", ests["ll"]), ("yl", ests["yl"])):
                gamma = A / (A + psi)
                est = gamma * y_s + (1 - gamma) * pred_s
                var = gamma * psi + cov_s
                row["coverage"][name] = coverage_of(est, var, truth_s)
                row["width"][name] = float(np.mean(2 * Z95 * np.sqrt(var)))
            assert abs(row["coverage"]["shipped"]
                       - float(np.mean(
                           (truth_s >= fh["est_sample"]
                            - Z95 * np.sqrt(fh["var_sample"]))
                           & (truth_s <= fh["est_sample"]
                              + Z95 * np.sqrt(fh["var_sample"]))))) < 1e-9
            b1.append(row)
            # b2 textbook refit
            X_s = X_all[sampled]
            ests_p = estimate_A(None, psi, X=X_s, y=y_s,
                                likelihood="profile")
            ests_r = estimate_A(None, psi, X=X_s, y=y_s,
                                likelihood="reml")
            row2 = {"draw": r, "product": product, "A": {
                        "ml": ests_p["ml_or_reml"],
                        "ll_p": ests_p["ll"], "yl_p": ests_p["yl"],
                        "reml": ests_r["ml_or_reml"],
                        "ll_r": ests_r["ll"], "yl_r": ests_r["yl"]},
                    "coverage": {}, "width": {}}
            pairs = (("ml", ests_p["ml_or_reml"], "profile"),
                     ("ll_p", ests_p["ll"], "profile"),
                     ("yl_p", ests_p["yl"], "profile"),
                     ("reml", ests_r["ml_or_reml"], "reml"),
                     ("ll_r", ests_r["ll"], "reml"),
                     ("yl_r", ests_r["yl"], "reml"))
            for name, A, _lk in pairs:
                _e2, beta = _gls_resid(max(A, 1e-10), y_s, X_s, psi)
                gamma = A / (A + psi)
                est = gamma * y_s + (1 - gamma) * (X_s @ beta)
                var = gamma * psi
                row2["coverage"][name] = coverage_of(est, var, truth_s)
                row2["width"][name] = float(np.mean(
                    2 * Z95 * np.sqrt(np.clip(var, 1e-12, None))))
            b2.append(row2)
            print(f"b1/b2 draw {r} {product}: A ship="
                  f"{fh['sigma2_u']:.3f} ml={ests['ml_or_reml']:.3f} "
                  f"ll={ests['ll']:.3f} yl={ests['yl']:.3f} cov ship="
                  f"{row['coverage']['shipped']:.3f} ll="
                  f"{row['coverage']['ll']:.3f} ({time.time()-t0:.0f}s)",
                  flush=True)
    return b1, b2


def summarise_tier1(b1, b2):
    out = {}
    for product in config.PRODUCTS:
        rows = [x for x in b1 if x["product"] == product]
        s = {}
        for name in ("shipped", "ml", "ll", "yl"):
            covs = np.array([x["coverage"][name] for x in rows])
            s[name] = {"coverage_mean": float(covs.mean()),
                       "coverage_sd": float(covs.std()),
                       "A_mean": float(np.mean(
                           [x["A_" + ("shipped" if name == "shipped"
                                      else name)] for x in rows])),
                       "A_zero_share": float(np.mean(
                           [x["A_" + ("shipped" if name == "shipped"
                                      else name)] <= 0 for x in rows]))}
        s["c_b1_all_positive_ll"] = bool(
            all(x["A_ll"] > 0 for x in rows))
        s["c_b1_all_positive_yl"] = bool(
            all(x["A_yl"] > 0 for x in rows))
        for nm in ("ll", "yl"):
            s[f"c_b2_{nm}"] = bool(
                abs(s[nm]["coverage_mean"] - 0.95)
                <= abs(s["shipped"]["coverage_mean"] - 0.95))
        out[product] = {"b1": s}
        rows2 = [x for x in b2 if x["product"] == product]
        s2 = {}
        for name in ("ml", "ll_p", "yl_p", "reml", "ll_r", "yl_r"):
            covs = np.array([x["coverage"][name] for x in rows2])
            s2[name] = {"coverage_mean": float(covs.mean()),
                        "A_zero_share": float(np.mean(
                            [x["A"][name] <= 0 for x in rows2]))}
        out[product]["b2"] = s2
    return out


# ------------------------------------------------------------ panel bT
def load_eshop_counts(zctas):
    sys.path.insert(0, HERE)
    from s2a_econ import load_eshop_counts as _f
    return _f(zctas)


def panel_tier2():
    df, Z, W = setup()
    households = df["households"].to_numpy(float)
    zctas = df["zcta"].to_numpy()
    zbp22 = bm.align_counts(bm.load_zbp(2022), zctas)
    zbp19 = bm.align_counts(bm.load_zbp(2019), zctas)
    n1s, buss = bm.load_soi22()
    soi = bm.align_counts(n1s, zctas)
    bus = bm.align_counts(buss, zctas)
    eshop = load_eshop_counts(zctas)
    evals = (("zbp22_establishments", zbp22, zbp22),
             ("soi22_returns", soi, soi),
             ("soi22_business_returns", bus, bus),
             ("temporal_transfer_zbp19_to_zbp22", zbp19, zbp22),
             ("zbp22_eshop", eshop, eshop))
    rows = []
    t0 = time.time()
    for r in range(24):
        rng_m = np.random.default_rng(config.SEED + 1000 * r)
        _t, oc0 = layer1.simulate_truth(df, Z, W, "steamers", rng_m)
        mask = oc0["sampled"].to_numpy(bool)
        for label, fit_counts, grade_counts in evals:
            has = ~np.isnan(fit_counts)
            fit_mask = mask & has
            oc = bm.make_outcomes(df, fit_counts, fit_mask)
            fits, best, sample = layer1.fit_all_models(df, Z, oc, W)
            pred_best = layer1.predict_all(best, fits[best], df, Z, W)
            cov_diag = cov_diag_for(fits[best], df, Z)
            orders_s = fit_counts[fit_mask]
            fh = layer1.fay_herriot(pred_best[fit_mask], sample["y"],
                                    orders_s, households[fit_mask],
                                    cov_diag[fit_mask])
            psi = fh["psi"]
            e = sample["y"] - pred_best[fit_mask]
            ests = estimate_A(e, psi)
            obs = np.log((grade_counts + 0.5) / households)
            held = (~mask) & (~np.isnan(grade_counts))
            rec = {"draw": r, "evaluation": label,
                   "A_shipped": fh["sigma2_u"], "behaviour": {}}
            for name, A in (("shipped", fh["sigma2_u"]),
                            ("ml", ests["ml_or_reml"]),
                            ("ll", ests["ll"]), ("yl", ests["yl"])):
                gamma = A / (A + psi)
                est = pred_best.copy()
                var = A + cov_diag
                est[fit_mask] = gamma * sample["y"] \
                    + (1 - gamma) * pred_best[fit_mask]
                var[fit_mask] = gamma * psi + cov_diag[fit_mask]
                half = 1.96 * np.sqrt(np.clip(var, 1e-6, None))
                inside = ((obs[held] >= (est - half)[held])
                          & (obs[held] <= (est + half)[held]))
                rec["behaviour"][name] = float(np.mean(inside))
                rec[f"A_{name}"] = float(A)
            rows.append(rec)
        print(f"bT draw {r} done ({time.time()-t0:.0f}s)", flush=True)
    summary = {}
    for label, _f, _g in evals:
        sub = [x for x in rows if x["evaluation"] == label]
        s = {}
        for name in ("shipped", "ml", "ll", "yl"):
            v = np.array([x["behaviour"][name] for x in sub])
            s[name] = {"behaviour_mean": float(v.mean()),
                       "behaviour_sd": float(v.std())}
            s[name]["closest_share"] = float(np.mean([
                name == min(("shipped", "ml", "ll", "yl"),
                            key=lambda nm: abs(x["behaviour"][nm] - 0.95))
                for x in sub]))
        summary[label] = s
    return rows, summary


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    path = os.path.join(OUT, "test_b_aml.json")
    out = {}
    if os.path.exists(path):
        out = json.load(open(path))
    if "method_check" not in out:
        out["method_check"] = method_check()
        print("method check:", out["method_check"], flush=True)
    if which in ("b1", "all") and "tier1_records" not in out:
        b1, b2 = panel_tier1()
        out["tier1_records"] = b1
        out["tier1_b2_records"] = b2
        out["tier1_summary"] = summarise_tier1(b1, b2)
    if which in ("bt", "all") and "tier2_records" not in out:
        rows, summary = panel_tier2()
        out["tier2_records"] = rows
        out["tier2_summary"] = summary
    with open(path, "w") as fh:
        json.dump(strict(out), fh, indent=1, allow_nan=False)
    print("wrote", path, flush=True)


if __name__ == "__main__":
    main()
