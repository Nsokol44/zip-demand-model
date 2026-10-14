"""
layer3_game.py — LAYER 3: geospatial game-theory play-through.

For the top-25 shortlist ZIPs per region (demo product), a Huff-model
contest against an aggregate incumbent is simulated under three
competitor response strategies, with Monte Carlo draws (SEED-fixed,
config.GT_MONTE_CARLO_DRAWS per ZIP) over which strategy materializes,
auction prices, and funnel conversion.

HONEST PROXY NOTE: there is no POI database in this pipeline. The
incumbent-intensity index is built from ACS covariates only —
standardized log population density + large-building share + share of
households earning $100k+ — i.e. "places that are dense, urban, and
rich are places incumbents already contest." It is a proxy for
competitive presence, not a measurement of it, and RESULTS.md says so.

Payoff per draw (per ZIP, one-year horizon):
  share        = A_own / (A_own + A_inc * strategy.attractiveness)
  orders       = true-addressable orders (Layer 1 FH rate x households)
                 x GT_REACH x share
  contribution = orders x AOV x margin x strategy.margin_squeeze
  acquisition  = (orders / orders_per_customer) x CAC_customer
                 x strategy.cac_pressure
  payoff       = contribution - acquisition - GT_FIXED_COST_PER_ZIP
CAC_customer is the first-order acquisition cost implied by the Phase 0
benchmark funnel: CPC U[$0.70,$1.10] / (landing->ATC U[4%,8%] x
ATC->order 0.35). Repeat orders inside the year carry no further CAC,
which is the only reason any ZIP can win — the model is deliberately
as unforgiving as the real unit economics.
"""

import numpy as np
import pandas as pd

import common
import config


def incumbent_index(Z):
    cols = {f: j for j, f in enumerate(common.FEATURES)}
    return (Z[:, cols["log_density"]] + Z[:, cols["pct_large_building"]]
            + Z[:, cols["share_income_100k"]]) / 3.0


def huff_share(a_own, a_inc):
    """Two-player Huff contest; returns own share in [0,1]."""
    total = a_own + a_inc
    return np.where(total > 0, a_own / np.maximum(total, 1e-12), 0.0)


def _pct_rank(values):
    return pd.Series(values).rank(pct=True).to_numpy()


def combined_scores(df, layer1, layer2, product):
    fh = np.exp(layer1["products"][product]["fh"]["est_log_rate"])
    gb = np.exp(layer2["products"][product]["pred_log_rate"])
    return 0.5 * (_pct_rank(fh) + _pct_rank(gb))


def run_layer3(df, Z, layer1, layer2, rng):
    product = config.DEMO_PRODUCT
    spec = config.PRODUCTS[product]
    inc = incumbent_index(Z)
    score = combined_scores(df, layer1, layer2, product)
    fh_rate = np.exp(layer1["products"][product]["fh"]["est_log_rate"])
    households = df["households"].to_numpy(float)
    addressable_orders = fh_rate * households

    a_own = 1.0 + score                      # offer strength in [1, 2]
    a_inc_base = np.exp(inc)                 # incumbent pull, mean ~1

    strat_names = list(config.GT_STRATEGIES)
    strat = config.GT_STRATEGIES
    logi = config.GT_RESPONSE_LOGISTIC

    rows = []
    showcase = None
    for region in config.REGIONS:
        m = (df["region"] == region).to_numpy()
        idx = np.where(m)[0]
        top = idx[np.argsort(-score[idx])[:config.GT_SHORTLIST_N]]
        for i in top:
            # response-strategy probabilities for this ZIP
            p_esc = common.sigmoid(logi["intercept"]
                                   + logi["slope"] * inc[i])
            p_agg = p_esc * logi["aggressive_share"]
            p_mod = p_esc * (1 - logi["aggressive_share"])
            p_none = 1.0 - p_esc
            probs = np.array([p_none, p_mod, p_agg])

            draws = config.GT_MONTE_CARLO_DRAWS
            s_draw = rng.choice(3, size=draws, p=probs)
            attr = np.array([strat[s]["incumbent_attractiveness"]
                             for s in strat_names])[s_draw]
            cacp = np.array([strat[s]["cac_pressure"]
                             for s in strat_names])[s_draw]
            msq = np.array([strat[s]["margin_squeeze"]
                            for s in strat_names])[s_draw]

            share = huff_share(a_own[i], a_inc_base[i] * attr)
            orders = (addressable_orders[i] * config.GT_REACH
                      * config.GT_HORIZON_YEARS * share)
            cpc = rng.uniform(config.CAC_CPC_LOW, config.CAC_CPC_HIGH,
                              draws)
            conv = (rng.uniform(config.LANDING_TO_ATC_LOW,
                                config.LANDING_TO_ATC_HIGH, draws)
                    * config.ATC_TO_ORDER)
            cac_customer = cpc / conv
            contribution = (orders * spec["assumed_aov"]
                            * spec["contribution_margin"] * msq)
            acquisition = (orders / config.GT_ORDERS_PER_CUSTOMER
                           * cac_customer * cacp)
            payoff = (contribution - acquisition
                      - config.GT_FIXED_COST_PER_ZIP)

            win_rate = float(np.mean(payoff > config.GT_WIN_THRESHOLD))
            p10 = float(np.quantile(payoff, 0.10))
            if win_rate >= 0.70 and p10 > 0:
                decision = "Launch"
            elif win_rate >= 0.40:
                decision = "Test"
            else:
                decision = "Avoid"
            row = {
                "zcta": df["zcta"].iloc[i], "region": region,
                "combined_score": float(score[i]),
                "incumbent_index": float(inc[i]),
                "addressable_orders_yr": float(addressable_orders[i]),
                "share_p10": float(np.quantile(share, 0.10)),
                "share_p50": float(np.quantile(share, 0.50)),
                "share_p90": float(np.quantile(share, 0.90)),
                "contribution_p10": p10,
                "contribution_p50": float(np.quantile(payoff, 0.50)),
                "contribution_p90": float(np.quantile(payoff, 0.90)),
                "win_rate": win_rate, "decision": decision,
                "p_no_response": float(p_none),
                "p_moderate": float(p_mod),
                "p_aggressive": float(p_agg),
                "_row_index": int(i),
            }
            rows.append(row)
            if region == config.REGION_NYC and (
                    showcase is None
                    or score[i] > showcase["combined_score"]):
                showcase = dict(row)
                showcase["payoff_draws"] = payoff
                showcase["share_draws"] = share
                showcase["strategy_draws"] = s_draw
                showcase["base_share"] = float(
                    huff_share(a_own[i], a_inc_base[i]))

    shortlist = pd.DataFrame(rows)
    return {"shortlist": shortlist, "showcase": showcase,
            "incumbent_index": inc, "combined_score": score}
