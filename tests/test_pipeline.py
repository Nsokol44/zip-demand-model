"""Pipeline invariant tests. Run: python -m pytest tests/ -q
Uses the cached data/features.csv (run data_fetch.py once first)
plus small synthetic frames; no network."""
import hashlib
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import common
import config
import layer1_econometrics as l1
import layer3_game as l3


@pytest.fixture(scope="module")
def small():
    df = common.load_features()
    df = df[df["region"] == config.REGION_SOUTHEAST].head(240)
    df = common.add_model_features(df.reset_index(drop=True))
    Z, _ = common.standardize(df)
    W = common.build_weights(df)
    return df, Z, W


def test_weights_row_sums(small):
    _df, _Z, W = small
    sums = np.asarray(W.sum(axis=1)).ravel()
    assert np.allclose(sums, 1.0, atol=1e-8)


def test_potential_shares_sum_to_one(small):
    df, Z, _W = small
    spend = l1.potential_allocation(df, Z, "steamers")
    for region in config.REGIONS:
        m = (df["region"] == region).to_numpy()
        if m.sum() == 0:
            continue
        expected = (df.loc[m, "households"].sum()
                    * config.CATEGORY_SPEND_PER_HH_YEAR)
        assert np.isclose(spend[m].sum(), expected, rtol=1e-9)


def test_fay_herriot_shrinkage_bounds():
    rng = np.random.default_rng(7)
    n = 60
    y = rng.normal(-5.0, 0.5, n)
    pred = y + rng.normal(0.0, 0.3, n)
    orders = rng.poisson(25, n).astype(float)
    hh = np.full(n, 5000.0)
    fh = l1.fay_herriot(pred, y, orders, hh)
    lo = np.minimum(y, pred)
    hi = np.maximum(y, pred)
    assert np.all(fh["est_sample"] >= lo - 1e-9)
    assert np.all(fh["est_sample"] <= hi + 1e-9)
    assert np.all((fh["gamma"] >= 0) & (fh["gamma"] <= 1))


def test_simulator_determinism(small):
    df, Z, W = small
    hashes = []
    for _ in range(2):
        rng = np.random.default_rng(config.SEED)
        _truth, outcomes = l1.simulate_truth(df, Z, W, "steamers", rng)
        hashes.append(hashlib.sha256(
            outcomes.to_csv(index=False).encode()).hexdigest())
    assert hashes[0] == hashes[1]


def test_huff_probabilities():
    a_own = np.array([0.5, 1.0, 2.0, 3.5])
    a_inc = np.array([2.0, 1.0, 1.0, 0.25])
    own = l3.huff_share(a_own, a_inc)
    inc = l3.huff_share(a_inc, a_own)
    assert np.all((own >= 0) & (own <= 1))
    assert np.allclose(own + inc, 1.0)
