"""
lm_tests.py — Anselin-Bera LM diagnostics for spatial dependence in
OLS residuals (Anselin & Bera, 1998; Anselin, Bera, Florax & Yoon,
1996), implemented directly with numpy. spreg is not installed in the
replication environment; the formulas below are the standard ones
(PySAL's OLSLMTests computes the same statistics).

With e = OLS residuals, s2 = e'e/n, W row-standardized, beta the OLS
estimates, M = I - X(X'X)^-1 X':

    T      = tr(W'W + W^2)
    D      = (WX beta)' M (WX beta) / s2 + T
    LMerr  = (e'We / s2)^2 / T
    LMlag  = (e'Wy / s2)^2 / D
    RLMerr = (e'We/s2 - (T/D)(e'Wy/s2))^2 / (T - T^2/D)
    RLMlag = (e'Wy/s2 - e'We/s2)^2 / (D - T)

Each is asymptotically chi-square(1) under the null of no spatial
dependence. p-values from the chi-square survival function.
"""

import numpy as np
from scipy import stats


def lm_tests(X, y, W):
    """X includes an intercept column. W is a dense row-standardized
    array (the pipeline's sample graph). Returns a dict of statistics
    and p-values."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    W = np.asarray(W, float)
    n = len(y)
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    e = y - X @ beta
    s2 = float(e @ e) / n
    We = W @ e
    Wy = W @ y
    eWe = float(e @ We) / s2
    eWy = float(e @ Wy) / s2
    T = float(np.trace(W.T @ W + W @ W))
    WXb = W @ (X @ beta)
    M_WXb = WXb - X @ (XtX_inv @ (X.T @ WXb))
    D = float(WXb @ M_WXb) / s2 + T
    lm_err = eWe ** 2 / T
    lm_lag = eWy ** 2 / D
    rlm_err = (eWe - (T / D) * eWy) ** 2 / (T - T ** 2 / D)
    rlm_lag = (eWy - eWe) ** 2 / (D - T)
    out = {}
    for name, stat in (("lm_error", lm_err), ("lm_lag", lm_lag),
                       ("robust_lm_error", rlm_err),
                       ("robust_lm_lag", rlm_lag)):
        out[name] = float(stat)
        out[name + "_p"] = float(stats.chi2.sf(max(stat, 0.0), 1))
    return out
