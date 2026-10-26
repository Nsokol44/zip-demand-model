"""
STRENGTHENING TEST (c) -- simulated second wave (design note
2026-10-26). For each of the 24 draws and both products: wave 1 =
the shipped counts; wave 2 = fresh Negative Binomial counts at the
same sampled areas from the same true rates (DGP size), stream
seeded SEED + 1000r + 7,000,000. Fits of the shipped joint model:
wave 1 only (= layer1.fay_herriot's fit), wave 2 only, and pooled
(one shared area effect v_i integrated over both waves' counts).
Measurements M1 (size recovery), M2 (ridge sharpness), M3 (wave-2
coverage under the pooled vs wave-1 split), per the note's
pre-stated verdict rule.

All likelihood and post-fit constructions replicate
layer1.fay_herriot exactly (physicists' Gauss-Hermite, 16 nodes;
scipy nbinom log-pmf; Nelder-Mead, three shipped starts, shipped
tolerances). A self-check on draw 0 asserts that the injected-
parameter construction reproduces fay_herriot's sigma2_u, psi and
sample estimates under the wave-1 fit.

Run:  python s2c_wave.py
Outputs: ../results/test_c_wave.json
"""
import sys, os, json, time
import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy import optimize
from scipy.stats import nbinom

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.expanduser("~/workspace/zip-demand-model")
sys.path.insert(0, REPO)

import common, config  # noqa: E402
import layer1_econometrics as layer1  # noqa: E402

OUT = os.path.join(HERE, "..", "results")
os.makedirs(OUT, exist_ok=True)

_NODES, _WEIGHTS = hermgauss(16)
_LOG_W = np.log(_WEIGHTS) - 0.5 * np.log(np.pi)
_Z = np.sqrt(2.0) * _NODES
Z95 = 1.959964
WAVE_OFFSET = 7_000_000
STARTS = ((6.0, 0.5), (3.0, 0.3), (20.0, 0.7))
SIZE_TRUE = float(config.DGP["nb_size"])


def _negll_counts(theta, mu_hat, counts_list, fixed_size=None):
    if fixed_size is None:
        size, tau = np.exp(theta[0]), np.exp(theta[1])
    else:
        size, tau = fixed_size, np.exp(theta[0])
    v = tau * _Z - 0.5 * tau ** 2                       # (K,)
    mu_ik = mu_hat[:, None] * np.exp(v)[None, :]        # (n, K)
    ll_ik = np.zeros_like(mu_ik)
    for counts in counts_list:
        ll_ik = ll_ik + nbinom.logpmf(counts[:, None], size,
                                      size / (size + mu_ik))
    a = ll_ik + _LOG_W[None, :]
    mx = a.max(axis=1)
    return -float((mx + np.log(np.exp(a - mx[:, None]).sum(axis=1))).sum())


def joint_fit(fit_pred_sample, counts_list, households_sample,
              fixed_size=None):
    mu_hat = np.exp(fit_pred_sample) * households_sample
    best = None
    for s0, t0 in STARTS:
        x0 = (np.log([s0, t0]) if fixed_size is None
              else np.log([t0]))
        res = optimize.minimize(
            _negll_counts, x0=x0, args=(mu_hat, counts_list, fixed_size),
            method="Nelder-Mead",
            options={"maxiter": 500, "xatol": 1e-3, "fatol": 1e-3})
        if best is None or res.fun < best.fun:
            best = res
    if fixed_size is None:
        return {"size_hat": float(np.exp(best.x[0])),
                "tau_hat": float(np.exp(best.x[1])),
                "loglik": float(-best.fun)}
    return {"size_hat": float(fixed_size),
            "tau_hat": float(np.exp(best.x[0])),
            "loglik": float(-best.fun)}


def fh_from_params(fit_pred_sample, y, orders_sample, households_sample,
                   size_hat, tau_hat, cov_diag_sample=None):
    """layer1.fay_herriot's post-fit construction, (size, tau)
    injected. Mirrors the shipped code line for line."""
    mu_hat = np.exp(fit_pred_sample) * households_sample
    v = tau_hat * _Z - 0.5 * tau_hat ** 2
    mu_ik = mu_hat[:, None] * np.exp(v)[None, :]
    ll_ik = nbinom.logpmf(orders_sample[:, None], size_hat,
                          size_hat / (size_hat + mu_ik))
    a = ll_ik + _LOG_W[None, :]
    post = np.exp(a - a.max(axis=1, keepdims=True))
    post /= post.sum(axis=1, keepdims=True)
    v_hat = post @ v
    mu_star = mu_hat * np.exp(v_hat)
    var_y = mu_star + mu_star ** 2 / size_hat
    psi = np.clip(var_y / (mu_star + 0.5) ** 2, 1e-4, 4.0)
    sigma2_moment = float(np.clip(
        np.mean((y - fit_pred_sample) ** 2 - psi), 0.02, 4.0))
    sigma2_u = float(max(tau_hat ** 2, sigma2_moment))
    gamma = sigma2_u / (sigma2_u + psi)
    est_s = gamma * y + (1 - gamma) * fit_pred_sample
    var_s = gamma * psi
    if cov_diag_sample is not None:
        var_s = var_s + cov_diag_sample
    return {"gamma": gamma, "est_sample": est_s, "var_sample": var_s,
            "sigma2_u": sigma2_u, "psi": psi}


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


def coverage(est, var, truth_s):
    half = Z95 * np.sqrt(var)
    return float(np.mean((truth_s >= est - half) & (truth_s <= est + half)))


def main():
    df = common.load_features(); df = common.add_model_features(df)
    Z, _ = common.standardize(df)
    W = common.build_weights(df)
    households_all = df["households"].to_numpy(float)
    X_all = np.column_stack([np.ones(len(df)), Z])
    records = []
    t0 = time.time()
    for r in range(24):
        rng = np.random.default_rng(config.SEED + 1000 * r)
        rng_w2 = np.random.default_rng(config.SEED + 1000 * r + WAVE_OFFSET)
        rec = {"draw": r, "products": {}}
        for product in config.PRODUCTS:
            truth, outcomes = layer1.simulate_truth(df, Z, W, product, rng)
            fits, best, sample = layer1.fit_all_models(df, Z, outcomes, W)
            sampled = sample["mask"]
            pred_best = layer1.predict_all(best, fits[best], df, Z, W)
            cov = fits[best]["cov"][:X_all.shape[1], :X_all.shape[1]]
            cov_diag = np.clip(
                np.einsum("ij,jk,ik->i", X_all, cov, X_all), 0.0, 2.0)
            orders_s = outcomes.loc[sampled, "orders"].to_numpy(float)
            hh_s = households_all[sampled]
            y_s = sample["y"]
            pred_s = pred_best[sampled]
            cov_s = cov_diag[sampled]
            truth_s = truth["true_log_rate"][sampled]
            # wave 2: fresh NB counts, same sampled areas, same truth
            mu_true_s = truth["true_mu"][sampled]
            p2 = SIZE_TRUE / (SIZE_TRUE + mu_true_s)
            counts2 = rng_w2.negative_binomial(SIZE_TRUE, p2).astype(float)
            y2 = np.log((counts2 + 0.5) / hh_s)
            # shipped wave-1 fit + joint fits
            fh1 = layer1.fay_herriot(pred_s, y_s, orders_s, hh_s, cov_s)
            fit1 = joint_fit(pred_s, [orders_s], hh_s)
            fit2 = joint_fit(pred_s, [counts2], hh_s)
            fitp = joint_fit(pred_s, [orders_s, counts2], hh_s)
            if r == 0 and product == list(config.PRODUCTS)[0]:
                rep = fh_from_params(pred_s, y_s, orders_s, hh_s,
                                     fit1["size_hat"], fit1["tau_hat"],
                                     cov_s)
                assert abs(rep["sigma2_u"] - fh1["sigma2_u"]) < 1e-9
                assert np.allclose(rep["psi"], fh1["psi"], atol=1e-9)
                assert np.allclose(rep["est_sample"], fh1["est_sample"],
                                   atol=1e-9)
                assert abs(fit1["size_hat"] - fh1["nb_size_hat"]) < 0.05
                print("self-check passed: injected-params construction "
                      "reproduces shipped fay_herriot", flush=True)

            def ridge(fit, counts_list):
                drops = []
                for mult in (0.5, 2.0):
                    ff = joint_fit(pred_s, counts_list, hh_s,
                                   fixed_size=fit["size_hat"] * mult)
                    drops.append(fit["loglik"] - ff["loglik"])
                return float(np.mean(drops))

            ridge1 = ridge(fit1, [orders_s])
            ridgep = ridge(fitp, [orders_s, counts2])
            fh_p_on2 = fh_from_params(pred_s, y2, counts2, hh_s,
                                      fitp["size_hat"], fitp["tau_hat"],
                                      cov_s)
            fh_1_on2 = fh_from_params(pred_s, y2, counts2, hh_s,
                                      fit1["size_hat"], fit1["tau_hat"],
                                      cov_s)
            cov_p = coverage(fh_p_on2["est_sample"],
                             fh_p_on2["var_sample"], truth_s)
            cov_1 = coverage(fh_1_on2["est_sample"],
                             fh_1_on2["var_sample"], truth_s)
            rec["products"][product] = {
                "size_w1": fit1["size_hat"], "size_w2": fit2["size_hat"],
                "size_pooled": fitp["size_hat"],
                "tau_w1": fit1["tau_hat"], "tau_pooled": fitp["tau_hat"],
                "sigma2u_shipped_w1": fh1["sigma2_u"],
                "M1_abserr_w1": float(abs(np.log(fit1["size_hat"]
                                                 / SIZE_TRUE))),
                "M1_abserr_pooled": float(abs(np.log(fitp["size_hat"]
                                                     / SIZE_TRUE))),
                "M2_ridge_w1": ridge1, "M2_ridge_pooled": ridgep,
                "M3_cov_wave2_pooledsplit": cov_p,
                "M3_cov_wave2_w1split": cov_1,
                "loglik_w1": fit1["loglik"],
                "loglik_pooled": fitp["loglik"],
            }
            print(f"draw {r} {product}: size w1={fit1['size_hat']:.2f} "
                  f"pooled={fitp['size_hat']:.2f} ridge "
                  f"{ridge1:.1f}->{ridgep:.1f} cov2 {cov_1:.3f}->"
                  f"{cov_p:.3f} ({time.time()-t0:.0f}s)", flush=True)
        records.append(rec)
    summary = {}
    for product in config.PRODUCTS:
        rows = [rec["products"][product] for rec in records]

        def m(k):
            v = np.array([row[k] for row in rows], float)
            return {"mean": float(v.mean()), "sd": float(v.std())}
        s = {
            "M1_abserr_w1": m("M1_abserr_w1"),
            "M1_abserr_pooled": m("M1_abserr_pooled"),
            "M1_improved": bool(m("M1_abserr_pooled")["mean"]
                                < m("M1_abserr_w1")["mean"]),
            "M2_ridge_w1": m("M2_ridge_w1"),
            "M2_ridge_pooled": m("M2_ridge_pooled"),
            "M2_sharper": bool(m("M2_ridge_pooled")["mean"]
                               > m("M2_ridge_w1")["mean"]),
            "M3_cov_wave2_w1split": m("M3_cov_wave2_w1split"),
            "M3_cov_wave2_pooledsplit": m("M3_cov_wave2_pooledsplit"),
            "M3_closer": bool(abs(m("M3_cov_wave2_pooledsplit")["mean"]
                                  - 0.95)
                              < abs(m("M3_cov_wave2_w1split")["mean"]
                                    - 0.95)),
        }
        s["verdict_supported"] = bool(s["M1_improved"] and s["M2_sharper"]
                                      and s["M3_closer"])
        summary[product] = s
    out = {"master_seed": config.SEED, "wave_offset": WAVE_OFFSET,
           "size_true": SIZE_TRUE, "summary": summary,
           "records": records}
    path = os.path.join(OUT, "test_c_wave.json")
    with open(path, "w") as fh:
        json.dump(strict(out), fh, indent=1, allow_nan=False)
    print("wrote", path, flush=True)


if __name__ == "__main__":
    main()
