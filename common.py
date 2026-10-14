"""
common.py — shared machinery: feature loading/standardization, sparse
kNN spatial weights, and small numeric helpers. No randomness here.
"""

import os

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.spatial import cKDTree

import config

# Model features, in the fixed order the DGP config keys refer to.
# All are built from data/features.csv columns.
FEATURES = [
    "log_income",         # log(median_hh_income)
    "share_income_100k",  # share of households with income >= $100k
    "renter_share",       # renter-occupied / occupied units
    "seasonal_share",     # seasonal vacant / housing units
    "pct_single_family",  # 1-unit structures / units in structure
    "pct_large_building",  # 20+ unit structures / units in structure
    "avg_hh_size",        # average household size
    "median_age",         # median age
    "log_density",        # log(population per sq mi)
]


def load_features():
    path = os.path.join(config.DATA_DIR, "features.csv")
    if not os.path.exists(path):
        raise SystemExit(
            f"{path} missing — run `python data_fetch.py` once first.")
    df = pd.read_csv(path, dtype={"zcta": str, "county_fips": str})
    df["county_fips"] = df["county_fips"].str.zfill(5)
    return df


def add_model_features(df):
    """Add log transforms; median-impute any missing ACS cells within
    region (counted and printed by the caller via .attrs)."""
    df = df.copy()
    df["log_income"] = np.log(df["median_hh_income"].clip(lower=1))
    df["log_density"] = np.log(df["pop_density"].clip(lower=0.01))
    imputations = {}
    for col in FEATURES:
        med = df.groupby("region")[col].transform("median")
        missing = df[col].isna()
        imputations[col] = int(missing.sum())
        df[col] = df[col].fillna(med).fillna(df[col].median())
    df.attrs["imputations"] = imputations
    return df


def standardize(df, cols=FEATURES):
    """Z-score columns using the pooled study-population mean/sd.
    Returns (Z matrix aligned to df rows, {col: (mean, sd)})."""
    stats = {}
    Z = np.empty((len(df), len(cols)))
    for j, col in enumerate(cols):
        values = df[col].to_numpy(dtype=float)
        mean, sd = values.mean(), values.std(ddof=0)
        if sd == 0:
            sd = 1.0
        stats[col] = (mean, sd)
        Z[:, j] = (values - mean) / sd
    return Z, stats


def build_weights(df, k=config.KNN_K):
    """Row-standardized kNN weights over ZCTA centroids.

    Distances are computed on a locally-scaled lon/lat projection
    (degrees * (111.32 km, 111.32*cos(mean lat) km)) — adequate for
    neighbor selection. Returns a scipy sparse CSR matrix aligned to
    df rows. Neighbors are chosen within the full study set (the two
    regions are geographically disjoint, so no cross-region edges
    arise in practice).
    """
    lat = np.radians(df["lat"].to_numpy(dtype=float))
    lon = np.radians(df["lon"].to_numpy(dtype=float))
    scale_x = 111.32 * np.cos(lat.mean())
    xy = np.column_stack([lon * scale_x, lat * 111.32])
    tree = cKDTree(xy)
    kk = min(k + 1, len(df))
    _dist, idx = tree.query(xy, k=kk)
    n = len(df)
    rows, cols, vals = [], [], []
    for i in range(n):
        for j in idx[i]:
            if j != i:
                rows.append(i)
                cols.append(j)
                vals.append(1.0)
    W = sparse.csr_matrix((vals, (rows, cols)), shape=(n, n))
    # kNN as returned can leave duplicate/extra entries; normalize rows
    W = W.tocsr()
    W.data[:] = 1.0
    row_sums = np.asarray(W.sum(axis=1)).ravel()
    inv = np.where(row_sums > 0, 1.0 / np.maximum(row_sums, 1e-12), 0.0)
    W = sparse.diags(inv) @ W
    return W.tocsr()


def weights_for_subset(W, mask):
    """Induced subgraph of the full weights among the selected rows,
    renormalized to row-standardized. Each selected unit keeps only
    its TRUE geographic neighbors that are also selected — at an 8%
    sampling rate most rows keep 0-1 edges, which is the honest
    graph: the spatial process lives on the full geography, and
    inventing long 'nearest sampled' edges would misstate its
    distance scale (verified: Moran's I of the true DGP error is
    0.38 on this graph vs 0.05 on a rebuilt kNN graph)."""
    sub = W[mask][:, mask]
    row_sums = np.asarray(sub.sum(axis=1)).ravel()
    inv = np.where(row_sums > 0, 1.0 / np.maximum(row_sums, 1e-12), 0.0)
    return (sparse.diags(inv) @ sub).tocsr()


def save_weights(W, path):
    sparse.save_npz(path, W)


def load_weights(path):
    return sparse.load_npz(path)


def morans_i(residuals, W, rng, n_perm=999):
    """Moran's I with a seeded permutation reference distribution."""
    x = np.asarray(residuals, dtype=float)
    x = x - x.mean()
    denom = float(x @ x)
    if denom == 0:
        return 0.0, 1.0
    n = len(x)
    s0 = float(W.sum())
    stat = (n / s0) * float(x @ (W @ x)) / denom
    count = 0
    for _ in range(n_perm):
        xp = rng.permutation(x)
        stat_p = (n / s0) * float(xp @ (W @ xp)) / denom
        if abs(stat_p) >= abs(stat):
            count += 1
    return stat, (count + 1) / (n_perm + 1)


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))
