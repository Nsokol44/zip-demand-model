"""
config.py — every declared input, assumption, and DGP truth for the
ZIP-demand-model pipeline. If a number appears anywhere in the results,
it is either (a) computed from the cached ACS/gazetteer data in data/,
or (b) written here and labeled ASSUMPTION or DGP-TRUTH.

DGP-TRUTH values are the parameters of the simulation that GENERATES
the synthetic "observed" sample used to validate the estimators. They
are not estimates and not claims about the real world; they exist so
recovery (estimate vs. known truth) can be measured exactly. When real
Phase 0 outcome data replaces the simulated sample, the DGP block is
retired and the same estimators run unchanged on the real outcomes.

Reproducibility: SEED below is the single source of randomness for the
whole pipeline (DGP draws, sampling, Monte Carlo, k-means, boosters).
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
RESULTS_DIR = os.path.join(HERE, "results")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")

SEED = 20261013  # the one and only seed

# ---------------------------------------------------------------- geography

ACS_VINTAGE = "2023"            # ACS 5-year 2023 (2019-2023 pooled)
ZCTA_POLYGON_VINTAGE = "2020"   # cartographic boundary file (see data_fetch)

# Southeast study states (USPS) — ZCTAs assigned by centroid-in-state.
SOUTHEAST_STATES = ("TN", "NC", "SC", "GA", "FL", "AL", "VA", "KY")

# NYC metro counties (5-digit FIPS): the five boroughs + Nassau, Suffolk,
# Westchester (NY) + Hudson, Bergen, Essex (NJ). ZCTAs assigned by
# centroid-in-county.
NYC_METRO_COUNTIES = (
    "36005",  # Bronx
    "36047",  # Kings (Brooklyn)
    "36061",  # New York (Manhattan)
    "36081",  # Queens
    "36085",  # Richmond (Staten Island)
    "36059",  # Nassau
    "36103",  # Suffolk
    "36119",  # Westchester
    "34017",  # Hudson, NJ
    "34003",  # Bergen, NJ
    "34013",  # Essex, NJ
)

REGION_SOUTHEAST = "southeast"
REGION_NYC = "nyc_metro"
REGIONS = (REGION_SOUTHEAST, REGION_NYC)

KNN_K = 6  # spatial weights: k-nearest ZCTA centroids, row-standardized

# Minimum size filters for a ZCTA to enter the study (tiny/PO-box ZCTAs
# with almost no households produce meaningless rates).
MIN_POPULATION = 500
MIN_HOUSEHOLDS = 200

# ---------------------------------------------------------------- products
# ASSUMPTION block: prices are the real Phase 0 slate prices; margins,
# basket sizes, and repeat behavior are stated assumptions, NOT measured.

PRODUCTS = {
    "steamers": {
        "label": "Qutipi Shower Steamers 8-Pack",
        "price": 13.99,                    # real slate price
        "contribution_margin": 0.55,       # ASSUMPTION: 55% of price
        "assumed_aov": 31.00,              # ASSUMPTION: basket AOV when
                                           # a steamer buyer checks out
        "fit": "renter / small-bathroom",
    },
    "trio": {
        "label": "Qutipi The Full Trio",
        "price": 39.99,                    # real slate price
        "contribution_margin": 0.60,       # ASSUMPTION: 60% of price
        "assumed_aov": 46.00,              # ASSUMPTION: basket AOV
        "fit": "owner / family",
    },
}
DEMO_PRODUCT = "steamers"      # game-theory layer runs on this product
SECOND_PRODUCT = "trio"        # carried through Layers 1-2 for contrast

# ASSUMPTION: per-household annual spend on bath/body consumables.
# A round number in the plausible range of BLS CEX personal-care
# product spending per consumer unit; it only scales the
# market-potential dollar column, never the demand-rate estimation.
CATEGORY_SPEND_PER_HH_YEAR = 120.00  # ASSUMPTION (round number)

# ------------------------------------------------- acquisition economics
# Benchmarks (from Phase 0 planning, Triple Whale-cited medians):
# Meta Reels CPC $0.70-$1.10; landing-page-view -> add-to-cart 4-8%.
CAC_CPC_LOW, CAC_CPC_HIGH = 0.70, 1.10          # benchmark range
LANDING_TO_ATC_LOW, LANDING_TO_ATC_HIGH = 0.04, 0.08   # benchmark range
ATC_TO_ORDER = 0.35        # ASSUMPTION: share of add-to-carts that
                           # become orders (funnel stage, unobserved)
# Implied CAC per acquired customer = CPC / (landing->ATC * ATC->order),
# drawn per ZIP in Layer 3 and scaled by competitive intensity.

# ------------------------------------------- simulation (DGP) — the "truth"
# These parameters GENERATE the synthetic observed sample. They are the
# ground truth the recovery metrics grade against.

SAMPLE_FRACTION = 0.08     # share of ZCTAs "observed" (Phase 0-style test)
SAMPLE_STRATA = "region x income tercile"

# DGP: log expected order rate per household per year =
#   intercept + X @ beta_product + spatial_error, spatial_error ~ SAR(rho)
#   observed orders ~ NegBin(mean = households * rate, size = NB_SIZE)
#   observed sessions ~ Poisson(households * TEST_SESSION_RATE)
#   observed ATC ~ Binomial(sessions, true_uptake), with
#   logit(true_uptake) = UPTAKE_INTERCEPT + X @ UPTAKE_BETA
# The DGP evaluates X with covariates CLIPPED at |z| = 2.5: demand
# response saturates in extreme covariate tails. Without the clip,
# Manhattan's density/renter/building z-scores (+3 to +4) stack
# linearly into absurd true rates (>10 orders/household/yr —
# verified in development). Estimators see the UNclipped covariates
# and must cope with the tails, as they would in reality.
DGP_FEATURE_CLIP = 2.5
DGP = {
    "rho": 0.55,               # DGP-TRUTH: spatial autocorrelation
    "sigma": 0.45,             # DGP-TRUTH: spatial error std (log scale)
    "nb_size": 6.0,            # DGP-TRUTH: NegBin dispersion (size)
    "test_session_rate": 0.06,  # DGP: test sessions per household in
                                # sampled ZIPs (the Phase 0-style exposure)
    "intercept": {             # DGP-TRUTH: baseline log order rate / HH / yr
        "steamers": -5.10,
        "trio": -5.55,
    },
    # DGP-TRUTH coefficients on standardized features (feature order =
    # FEATURES in common.py). Steamers load on renter share + large
    # buildings + density; Trio loads on income + single-family + owner.
    "beta": {
        "steamers": {
            "log_income": 0.22, "share_income_100k": 0.10,
            "renter_share": 0.48, "seasonal_share": -0.08,
            "pct_single_family": -0.30, "pct_large_building": 0.38,
            "avg_hh_size": -0.12, "median_age": -0.15,
            "log_density": 0.30,
        },
        "trio": {
            "log_income": 0.42, "share_income_100k": 0.25,
            "renter_share": -0.38, "seasonal_share": 0.12,
            "pct_single_family": 0.40, "pct_large_building": -0.25,
            "avg_hh_size": 0.20, "median_age": 0.05,
            "log_density": -0.10,
        },
    },
    "uptake_intercept": -3.35,  # DGP-TRUTH: ~3.4% baseline session->ATC
    "uptake_beta": {            # DGP-TRUTH: logit coefficients
        "log_income": 0.30, "share_income_100k": 0.15,
        "renter_share": 0.10, "seasonal_share": 0.00,
        "pct_single_family": 0.05, "pct_large_building": 0.05,
        "avg_hh_size": -0.05, "median_age": -0.20,
        "log_density": 0.10,
    },
}

# ------------------------------------------------------- game theory (L3)
# All ASSUMPTIONS — a parameterized play-through, not a forecast.

GT_SHORTLIST_N = 25            # top ZIPs per region entering the game
GT_MONTE_CARLO_DRAWS = 500     # per ZIP, SEED-fixed
GT_HORIZON_YEARS = 1.0         # payoff horizon
GT_REACH = 0.35                # ASSUMPTION: share of a ZIP's modeled
                               # product demand reachable in year 1
GT_FIXED_COST_PER_ZIP = 200.0  # ASSUMPTION: creative/localization setup
GT_ORDERS_PER_CUSTOMER = 2.2   # ASSUMPTION: year-1 orders per acquired
                               # customer (initial + repeats)
GT_WIN_THRESHOLD = 0.0         # payoff ($) above this counts as a "win"

# Competitor response strategies: multipliers applied when drawn.
#   incumbent_attractiveness: scales the Huff incumbent term
#   cac_pressure:             scales our CAC (auction escalation)
#   margin_squeeze:           scales our contribution (promo matching)
GT_STRATEGIES = {
    "no_response": {"incumbent_attractiveness": 1.00,
                    "cac_pressure": 1.00, "margin_squeeze": 1.00},
    "moderate":    {"incumbent_attractiveness": 1.25,
                    "cac_pressure": 1.20, "margin_squeeze": 0.95},
    "aggressive":  {"incumbent_attractiveness": 1.60,
                    "cac_pressure": 1.50, "margin_squeeze": 0.85},
}
# Probability a competitor escalates (moderate+aggressive mass) rises
# with the incumbent-intensity index z-score via this logistic map.
GT_RESPONSE_LOGISTIC = {"intercept": -0.40, "slope": 0.90,
                        "aggressive_share": 0.40}  # of escalations

# Decision rule (printed verbatim in RESULTS.md):
GT_DECISION_RULE = (
    "Launch if win rate >= 70% and p10 contribution > $0; "
    "Test if win rate 40-70%; Avoid otherwise."
)

# ------------------------------------------------------------- real-data
# Future Phase 0 outcomes drop in as a CSV with EXACTLY this schema
# (one row per tested ZCTA). When data/real_outcomes.csv exists and
# run_all.py is called with --real, the DGP sample is replaced by it
# and every estimator runs unchanged. See README.md.
REAL_OUTCOMES_SCHEMA = [
    "zcta",            # 5-digit ZCTA, must exist in data/features.csv
    "product",         # 'steamers' | 'trio'
    "sessions",        # landing sessions observed
    "add_to_carts",    # add-to-cart events observed
    "orders",          # orders observed
    "exposure_days",   # length of the test window
]
