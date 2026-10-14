"""
layer1_econometrics.py — LAYER 1: spatial econometric model.

Components:
  (a) Market-potential allocation (deterministic, documented formula).
  (b) The simulation DGP: a KNOWN true demand surface (config.DGP) from
      which a Phase 0-style observed sample is drawn. This is the
      validation design: estimators are graded against the truth.
  (c) Estimation on the observed sample only: OLS, spatial lag (SAR),
      spatial error (SEM), spatial Durbin (SDM) — maximum likelihood
      implemented directly with numpy/scipy (spreg is not installed in
      this environment). Moran's I on OLS residuals (seeded
      permutation). Model choice by AIC.
  (d) Fay-Herriot-style small-area shrinkage: sampled ZIPs blend their
      direct estimate with the model prediction by relative variance;
      unsampled ZIPs get the model prediction with a full interval.
      Every ZCTA leaves with an estimate + 95% interval on the log-rate
      scale, and interval coverage against the truth is reported.

The observed-sample table has EXACTLY the schema of the future real
Phase 0 outcomes file (config.REAL_OUTCOMES_SCHEMA, plus annualization
via exposure_days), so real data drops in without code changes.
"""

import numpy as np
import pandas as pd
from scipy import optimize, sparse
from scipy.sparse import linalg as spla

import common
import config

# Market-potential allocation weights (this layer's stated method —
# judgment weights on standardized covariates, documented here; they
# are NOT the DGP truth and NOT fitted). Direction follows each
# product's stated fit in config.PRODUCTS.
ALLOCATION_WEIGHTS = {
    "steamers": {"log_income": 0.20, "share_income_100k": 0.10,
                 "renter_share": 0.45, "seasonal_share": -0.05,
                 "pct_single_family": -0.25, "pct_large_building": 0.35,
                 "avg_hh_size": -0.10, "median_age": -0.10,
                 "log_density": 0.25},
    "trio": {"log_income": 0.40, "share_income_100k": 0.20,
             "renter_share": -0.35, "seasonal_share": 0.10,
             "pct_single_family": 0.35, "pct_large_building": -0.20,
             "avg_hh_size": 0.15, "median_age": 0.05,
             "log_density": -0.05},
}


def potential_allocation(df, Z, product):
    """Regional category spend allocated by covariate share function.

    share_i = HH_i * exp(w'Z_i) / sum_j(HH_j * exp(w'Z_j)) within the
    region; potential_spend_i = share_i * (total regional households *
    CATEGORY_SPEND_PER_HH_YEAR * product-relevance scale), where the
    relevance scale is the product's share of category spend — set to
    the product price / category spend so dollars stay interpretable
    as 'annual spend available to this product's niche'. Shares sum
    to 1 within region by construction (tested).
    """
    w = np.array([ALLOCATION_WEIGHTS[product][f] for f in common.FEATURES])
    attract = df["households"].to_numpy(float) * np.exp(Z @ w)
    out = np.zeros(len(df))
    for region in config.REGIONS:
        m = (df["region"] == region).to_numpy()
        region_total = (df.loc[m, "households"].sum() *
                        config.CATEGORY_SPEND_PER_HH_YEAR)
        shares = attract[m] / attract[m].sum()
        out[m] = shares * region_total
    return out


# ------------------------------------------------------------------- DGP

def simulate_truth(df, Z, W, product, rng):
    """Draw the true latent surface + the observed sample outcomes.

    Returns (truth dict of arrays, outcomes DataFrame). The outcomes
    frame follows config.REAL_OUTCOMES_SCHEMA with exposure_days=365,
    i.e. the simulated test is expressed at a one-year-equivalent
    exposure so rates are directly comparable to the truth.
    """
    dgp = config.DGP
    Z_dgp = np.clip(Z, -config.DGP_FEATURE_CLIP, config.DGP_FEATURE_CLIP)
    beta = np.array([dgp["beta"][product][f] for f in common.FEATURES])
    eta = dgp["intercept"][product] + Z_dgp @ beta
    n = len(df)
    eps = rng.normal(0.0, dgp["sigma"], n)
    # spatial error: u = (I - rho W)^-1 eps  (sparse solve, full graph)
    A = sparse.eye(n, format="csc") - dgp["rho"] * W.tocsc()
    u = spla.spsolve(A, eps)
    true_log_rate = eta + u
    true_rate = np.exp(true_log_rate)
    households = df["households"].to_numpy(float)
    true_mu = households * true_rate

    ubeta = np.array([dgp["uptake_beta"][f] for f in common.FEATURES])
    true_uptake = common.sigmoid(dgp["uptake_intercept"] + Z_dgp @ ubeta)

    # stratified sample: region x income tercile (rank-based terciles
    # on region-median-imputed income — robust to NaN cells and to a
    # region being absent from a subset frame)
    sampled = np.zeros(n, dtype=bool)
    income = pd.Series(df["median_hh_income"].to_numpy(float))
    income = income.fillna(
        income.groupby(df["region"].to_numpy()).transform("median")
    ).to_numpy()
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
            take = max(1, int(round(config.SAMPLE_FRACTION * len(cell))))
            sampled[rng.choice(cell, size=take, replace=False)] = True

    sessions = np.zeros(n, dtype=int)
    atc = np.zeros(n, dtype=int)
    orders = np.zeros(n, dtype=int)
    sidx = np.where(sampled)[0]
    lam = households[sidx] * dgp["test_session_rate"]
    sessions[sidx] = rng.poisson(lam)
    atc[sidx] = rng.binomial(sessions[sidx], true_uptake[sidx])
    size = dgp["nb_size"]
    p = size / (size + true_mu[sidx])
    orders[sidx] = rng.negative_binomial(size, p)

    outcomes = pd.DataFrame({
        "zcta": df["zcta"].to_numpy(),
        "product": product,
        "sampled": sampled,
        "sessions": sessions,
        "add_to_carts": atc,
        "orders": orders,
        "exposure_days": np.where(sampled, 365, 0),
        # simulated exposure is one-year-equivalent by construction
        "orders_annualized": orders.astype(float),
    })
    truth = {
        "true_log_rate": true_log_rate,
        "true_rate": true_rate,
        "true_mu": true_mu,
        "true_uptake": true_uptake,
    }
    return truth, outcomes


# ------------------------------------------------------- real outcomes

def load_real_outcomes(df, path):
    """Load a real Phase 0 outcomes CSV (config.REAL_OUTCOMES_SCHEMA)
    into the same per-product outcomes frames simulate_truth returns.
    ZCTAs absent from the file are unsampled (zeros). Returns
    {product: outcomes DataFrame}."""
    raw = pd.read_csv(path, dtype={"zcta": str})
    missing = [c for c in config.REAL_OUTCOMES_SCHEMA
               if c not in raw.columns]
    if missing:
        raise SystemExit(f"real outcomes file missing columns: {missing}")
    out = {}
    zctas = df["zcta"].to_numpy()
    pos = {z: i for i, z in enumerate(zctas)}
    for product in config.PRODUCTS:
        sub = raw[raw["product"] == product]
        oc = pd.DataFrame({
            "zcta": zctas, "product": product,
            "sampled": False,
            "sessions": 0, "add_to_carts": 0, "orders": 0,
            "exposure_days": 0, "orders_annualized": 0.0,
        })
        for _, r in sub.iterrows():
            if r["zcta"] not in pos:
                continue
            i = pos[r["zcta"]]
            days = max(int(r["exposure_days"]), 1)
            oc.loc[i, "sampled"] = True
            oc.loc[i, "sessions"] = int(r["sessions"])
            oc.loc[i, "add_to_carts"] = int(r["add_to_carts"])
            oc.loc[i, "orders"] = int(r["orders"])
            oc.loc[i, "exposure_days"] = int(r["exposure_days"])
            oc.loc[i, "orders_annualized"] = (float(r["orders"])
                                              * 365.0 / days)
        out[product] = oc
    return out


# ------------------------------------------------------------- estimation

def _logdet_spatial(param, eigvals):
    """log |I - param*W| from the eigenvalues of W (complex conjugate
    pairs contribute a real sum)."""
    return float(np.sum(np.log(1.0 - param * eigvals)).real)


def _fit_ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, k = X.shape
    sigma2 = float(resid @ resid) / max(n - k, 1)
    cov = sigma2 * np.linalg.inv(X.T @ X)
    ll = -0.5 * n * (np.log(2 * np.pi * sigma2) + 1)
    return {"beta": beta, "resid": resid, "sigma2": sigma2, "cov": cov,
            "loglik": ll, "k": k}


def _fit_sar(X, y, W, eigvals, lag_x=False):
    """ML spatial lag (optionally Durbin if X already carries WX)."""
    Wy = W @ y
    n = len(y)
    XtX_inv = np.linalg.inv(X.T @ X)

    def neg_ll(rho):
        beta = XtX_inv @ (X.T @ (y - rho * Wy))
        resid = y - rho * Wy - X @ beta
        sigma2 = max(float(resid @ resid) / n, 1e-12)
        ll = (_logdet_spatial(rho, eigvals)
              - 0.5 * n * (np.log(2 * np.pi * sigma2) + 1))
        return -ll

    res = optimize.minimize_scalar(neg_ll, bounds=(-0.95, 0.95),
                                   method="bounded")
    rho = float(res.x)
    beta = XtX_inv @ (X.T @ (y - rho * Wy))
    resid = y - rho * Wy - X @ beta
    sigma2 = float(resid @ resid) / n
    cov = sigma2 * XtX_inv  # approximation, documented in RESULTS.md
    return {"beta": beta, "rho": rho, "resid": resid, "sigma2": sigma2,
            "cov": cov, "loglik": -float(res.fun), "k": X.shape[1] + 1}


def _fit_sem(X, y, W, eigvals):
    """ML spatial error via concentrated likelihood over lambda."""
    n = len(y)
    I = np.eye(n)

    def neg_ll(lam):
        A = I - lam * W
        yl, Xl = A @ y, A @ X
        beta, *_ = np.linalg.lstsq(Xl, yl, rcond=None)
        resid = yl - Xl @ beta
        sigma2 = max(float(resid @ resid) / n, 1e-12)
        ll = (_logdet_spatial(lam, eigvals)
              - 0.5 * n * (np.log(2 * np.pi * sigma2) + 1))
        return -ll

    res = optimize.minimize_scalar(neg_ll, bounds=(-0.95, 0.95),
                                   method="bounded")
    lam = float(res.x)
    A = I - lam * W
    yl, Xl = A @ y, A @ X
    beta, *_ = np.linalg.lstsq(Xl, yl, rcond=None)
    resid = y - X @ beta
    sigma2 = float(((A @ resid) @ (A @ resid))) / n
    cov = sigma2 * np.linalg.inv(Xl.T @ Xl)
    return {"beta": beta, "lambda": lam, "resid": resid,
            "sigma2": sigma2, "cov": cov, "loglik": -float(res.fun),
            "k": X.shape[1] + 1}


def fit_all_models(df, Z, outcomes, W_full):
    """Estimate OLS / SAR / SEM / SDM on the sampled ZIPs.

    Returns (fits dict, best model name, sample arrays dict). y = log
    observed annual order rate per household, +0.5 correction.
    """
    sampled = outcomes["sampled"].to_numpy()
    households = df["households"].to_numpy(float)
    orders = outcomes["orders_annualized"].to_numpy(float)
    y_all = np.log((orders + 0.5) / households)
    Xs = np.column_stack([np.ones(sampled.sum()), Z[sampled]])
    ys = y_all[sampled]

    import common as _c
    W_s = _c.weights_for_subset(W_full, sampled)
    W_s_dense = W_s.toarray()
    eigvals = np.linalg.eigvals(W_s_dense)

    fits = {}
    fits["OLS"] = _fit_ols(Xs, ys)
    fits["SAR"] = _fit_sar(Xs, ys, W_s_dense, eigvals)
    fits["SEM"] = _fit_sem(Xs, ys, W_s_dense, eigvals)
    WX = W_s_dense @ Xs[:, 1:]
    X_durbin = np.column_stack([Xs, WX])
    fits["SDM"] = _fit_sar(X_durbin, ys, W_s_dense, eigvals)
    for name, fit in fits.items():
        fit["aic"] = 2 * fit["k"] - 2 * fit["loglik"]
    best = min(("SAR", "SEM", "SDM"), key=lambda m: fits[m]["aic"])
    sample = {"X": Xs, "y": ys, "W": W_s, "W_dense": W_s_dense,
              "mask": sampled, "y_all": y_all}
    return fits, best, sample


def predict_all(name, fit, df, Z, W_full):
    """In-population prediction of log rate for every ZCTA."""
    X = np.column_stack([np.ones(len(df)), Z])
    if name == "OLS" or name == "SEM":
        return X @ fit["beta"]
    n = len(df)
    if name == "SAR":
        rhs = X @ fit["beta"]
    elif name == "SDM":
        WX = np.asarray(W_full @ Z)
        X_aug = np.column_stack([X, WX])
        rhs = X_aug @ fit["beta"]
    A = (sparse.eye(n, format="csc") - fit["rho"] * W_full.tocsc())
    return spla.spsolve(A, rhs)


def fay_herriot(fit_pred_sample, y, orders_sample, households_sample,
                cov_diag_sample=None):
    """Fay-Herriot-style blend for the SAMPLED ZIPs.

    psi_i and sigma2_u come from a joint ML fit on the counts:

        Y_i ~ NegBin(mean = mu_hat_i * exp(v_i), size),
        v_i ~ N(-tau^2/2, tau^2)   [so E exp(v) = 1]

    with the lognormal area effect integrated out by Gauss-Hermite
    quadrature; psi_i is the delta-method log-rate variance at the
    posterior-mean area effect, and sigma2_u = tau^2.

    Why not something simpler - both one-shot alternatives were
    tried and failed in development, and the failures are the
    reason this is documented at length: (1) plug-in FH moments
    charge the area effect to the count noise (size collapses to
    ~1, psi explodes, gamma -> 0, coverage 0.28); (2) anchoring
    sigma2_u to the log-scale moment in a fixed point with the ML
    size spirals to the floor (coverage 0.48). The (size, tau)
    likelihood has a flat ridge - the split between count
    overdispersion and area variance is weakly identified from one
    cross-section (verified: delta-logLik across the plausible
    region is only ~3-11) - so the optimizer is run from three
    starts and the best-likelihood landing is kept. sigma2_u is
    then set to the LARGER of tau^2 and the classic FH moment
    estimator mean((y-pred)^2 - psi) computed with the ML-based
    psi. Calibration is imperfect and the imperfection is
    traceable: psi inherits 1/size_hat, so when the ridge lands
    on a small size (3.7 vs the DGP's 6.0 for steamers), psi is
    overstated, sigma2_u is understated, and intervals under-cover
    (0.84 vs 0.95 nominal for steamers; 0.97 for trio, whose split
    landed the other way). The simulation design exists to make
    exactly this visible - coverage is reported in RESULTS.md,
    not assumed. Only sample data is used; the DGP's true size
    is never touched.
    """
    from numpy.polynomial.hermite import hermgauss
    from scipy.stats import nbinom

    mu_hat = np.exp(fit_pred_sample) * households_sample
    nodes, weights = hermgauss(16)
    log_w = np.log(weights) - 0.5 * np.log(np.pi)
    z = np.sqrt(2.0) * nodes

    def neg_ll(params):
        log_size, log_tau = params
        size, tau = np.exp(log_size), np.exp(log_tau)
        v = tau * z - 0.5 * tau ** 2                    # (K,)
        mu_ik = mu_hat[:, None] * np.exp(v)[None, :]    # (n, K)
        ll_ik = nbinom.logpmf(orders_sample[:, None], size,
                              size / (size + mu_ik))
        a = ll_ik + log_w[None, :]
        mx = a.max(axis=1)
        return -float((mx + np.log(
            np.exp(a - mx[:, None]).sum(axis=1))).sum())

    best = None
    for start in ((6.0, 0.5), (3.0, 0.3), (20.0, 0.7)):
        res = optimize.minimize(
            neg_ll, x0=np.log(np.array(start)), method="Nelder-Mead",
            options={"maxiter": 500, "xatol": 1e-3, "fatol": 1e-3})
        if best is None or res.fun < best.fun:
            best = res
    size_hat = float(np.exp(best.x[0]))
    tau_hat = float(np.exp(best.x[1]))
    sigma2_u = float(tau_hat ** 2)

    # posterior mean of v_i under the fitted model
    v = tau_hat * z - 0.5 * tau_hat ** 2
    mu_ik = mu_hat[:, None] * np.exp(v)[None, :]
    ll_ik = nbinom.logpmf(orders_sample[:, None], size_hat,
                          size_hat / (size_hat + mu_ik))
    a = ll_ik + log_w[None, :]
    post = np.exp(a - a.max(axis=1, keepdims=True))
    post /= post.sum(axis=1, keepdims=True)
    v_hat = post @ v
    mu_star = mu_hat * np.exp(v_hat)

    # delta-method variance of the log rate, evaluated at the
    # posterior mean mu_star in BOTH numerator and denominator
    # (using the observed count in the denominator injects noise
    # and badly upward-biases psi wherever the count drew low)
    var_y = mu_star + mu_star ** 2 / size_hat
    psi = np.clip(var_y / (mu_star + 0.5) ** 2, 1e-4, 4.0)
    sigma2_moment = float(np.clip(
        np.mean((y - fit_pred_sample) ** 2 - psi), 0.02, 4.0))
    sigma2_u = float(max(sigma2_u, sigma2_moment))
    gamma = sigma2_u / (sigma2_u + psi)
    est_s = gamma * y + (1 - gamma) * fit_pred_sample
    var_s = gamma * psi
    if cov_diag_sample is not None:
        var_s = var_s + cov_diag_sample  # parameter-uncertainty term
    return {"gamma": gamma, "est_sample": est_s, "var_sample": var_s,
            "sigma2_u": sigma2_u, "nb_size_hat": size_hat,
            "psi": psi}




def run_layer1(df, Z, W, rng, real_path=None):
    """Full Layer 1 for both products. With real_path set, the DGP
    sample is replaced by the real outcomes file and every
    truth-recovery metric is reported as None (there is no truth to
    recover against — that is the point of real data)."""
    results = {"products": {}, "real_mode": real_path is not None}
    outcomes_store = {}
    truth_store = {}
    real = load_real_outcomes(df, real_path) if real_path else None

    for product in config.PRODUCTS:
        if real is not None:
            outcomes, truth = real[product], None
        else:
            truth, outcomes = simulate_truth(df, Z, W, product, rng)
        fits, best, sample = fit_all_models(df, Z, outcomes, W)
        sampled = sample["mask"]

        pred_best = predict_all(best, fits[best], df, Z, W)
        # approximate prediction variance: sigma2 * (1 + leverage proxy)
        X_all = np.column_stack([np.ones(len(df)), Z])
        cov = fits[best]["cov"][:X_all.shape[1], :X_all.shape[1]]
        cov_diag = np.einsum("ij,jk,ik->i", X_all, cov, X_all)
        cov_diag = np.clip(cov_diag, 0.0, 2.0)

        orders_s = outcomes.loc[sampled, "orders"].to_numpy(float)
        fh = fay_herriot(
            pred_best[sampled], sample["y"], orders_s,
            df.loc[sampled, "households"].to_numpy(float),
            cov_diag_sample=cov_diag[sampled])
        est_all = pred_best.copy()
        var_all = fh["sigma2_u"] + cov_diag
        est_all[sampled] = fh["est_sample"]
        var_all[sampled] = fh["var_sample"]
        half = 1.96 * np.sqrt(np.clip(var_all, 1e-6, None))
        lo, hi = est_all - half, est_all + half

        if truth is not None:
            true_log = truth["true_log_rate"]
            covered = (true_log >= lo) & (true_log <= hi)
            coverage = float(covered.mean())
            coverage_s = float(covered[sampled].mean())
            rmse_log = float(np.sqrt(np.mean((est_all - true_log) ** 2)))
            rmse_best = float(np.sqrt(np.mean(
                (pred_best - true_log) ** 2)))
            rmse_ols = float(np.sqrt(np.mean(
                (predict_all("OLS", fits["OLS"], df, Z, W)
                 - true_log) ** 2)))
        else:
            coverage = coverage_s = rmse_log = rmse_best = rmse_ols = None

        # Moran's I on OLS residuals (sample graph), seeded permutation
        mi, mi_p = common.morans_i(fits["OLS"]["resid"], sample["W"], rng)

        coef_table = []
        dgp_beta = config.DGP["beta"][product]
        for j, fname in enumerate(["intercept"] + common.FEATURES):
            true_val = (config.DGP["intercept"][product] if j == 0
                        else dgp_beta[fname]) if truth is not None \
                else float("nan")
            coef_table.append({
                "term": fname, "true": true_val,
                "OLS": fits["OLS"]["beta"][j],
                "SAR": fits["SAR"]["beta"][j],
                "SEM": fits["SEM"]["beta"][j],
                "SDM": fits["SDM"]["beta"][j],
            })

        results["products"][product] = {
            "fits": fits, "best": best,
            "moran_i": mi, "moran_p": mi_p,
            "rmse_log_fh": rmse_log, "rmse_log_best_model": rmse_best,
            "rmse_log_ols": rmse_ols,
            "coverage": coverage,
            "coverage_sampled": coverage_s,
            "coef_table": coef_table,
            "fh": {"est_log_rate": est_all, "lo": lo, "hi": hi,
                   "gamma_mean": float(fh["gamma"].mean()),
                   "sigma2_u": fh["sigma2_u"],
                   "nb_size_hat": fh["nb_size_hat"]},
            "potential_spend": potential_allocation(df, Z, product),
            "model_pred_log_rate": pred_best,
        }
        outcomes_store[product] = outcomes
        truth_store[product] = truth

    results["outcomes"] = outcomes_store
    results["truth"] = truth_store
    return results
