"""
figures.py — the four RESULTS figures (matplotlib, Agg, no network).
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config


def _choropleth(parquet_name, values, title, out_name):
    import geopandas as gpd
    path = os.path.join(config.DATA_DIR, parquet_name)
    if not os.path.exists(path):
        return None
    gdf = gpd.read_parquet(path)
    gdf["value"] = gdf["zcta"].map(values)
    fig, ax = plt.subplots(figsize=(9, 8))
    gdf.plot(column="value", ax=ax, cmap="viridis", linewidth=0.05,
             edgecolor="white", legend=True,
             legend_kwds={"label": "predicted orders / household / yr",
                          "shrink": 0.6},
             missing_kwds={"color": "lightgrey"})
    ax.set_title(title)
    ax.set_axis_off()
    fig.tight_layout()
    out = os.path.join(config.FIGURES_DIR, out_name)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def make_figures(df, layer2, layer3):
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    demo = layer2["products"][config.DEMO_PRODUCT]
    pred_rate = pd.Series(np.exp(demo["pred_log_rate"]),
                          index=df["zcta"]).to_dict()

    made = []
    p = _choropleth(
        "geometry_nyc.parquet", pred_rate,
        "NYC metro — GeoAI predicted demand, Qutipi Shower Steamers\n"
        "(SIMULATED-sample model; see RESULTS.md)",
        "choropleth_nyc.png")
    if p:
        made.append(p)
    p = _choropleth(
        "geometry_southeast.parquet", pred_rate,
        "Southeast — GeoAI predicted demand, Qutipi Shower Steamers\n"
        "(SIMULATED-sample model; see RESULTS.md)",
        "choropleth_southeast.png")
    if p:
        made.append(p)

    # Monte Carlo payoff distribution, showcase ZIP
    sc = layer3["showcase"]
    if sc is not None:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.hist(sc["payoff_draws"], bins=40, color="#4477aa",
                edgecolor="white", linewidth=0.3)
        ax.axvline(0, color="red", linewidth=1.2)
        ax.axvline(np.quantile(sc["payoff_draws"], 0.10),
                   color="black", linestyle="--", linewidth=0.9)
        ax.axvline(np.quantile(sc["payoff_draws"], 0.90),
                   color="black", linestyle="--", linewidth=0.9)
        ax.set_xlabel("one-year payoff ($)")
        ax.set_ylabel("Monte Carlo draws (of 500)")
        ax.set_title(f"Showcase play-through — ZIP {sc['zcta']} "
                     f"(NYC metro), Shower Steamers\n"
                     f"win rate {sc['win_rate']:.0%}, "
                     f"decision: {sc['decision']}")
        fig.tight_layout()
        out = os.path.join(config.FIGURES_DIR, "showcase_payoff.png")
        fig.savefig(out, dpi=130)
        plt.close(fig)
        made.append(out)
    return made


def agreement_scatter(df, layer1, layer2):
    l1 = layer1["products"][config.DEMO_PRODUCT]["fh"]["est_log_rate"]
    l2 = layer2["products"][config.DEMO_PRODUCT]["pred_log_rate"]
    fig, ax = plt.subplots(figsize=(6.5, 6))
    for region, color in ((config.REGION_SOUTHEAST, "#4477aa"),
                          (config.REGION_NYC, "#cc6677")):
        m = (df["region"] == region).to_numpy()
        ax.scatter(l1[m], l2[m], s=3, alpha=0.35, color=color,
                   label=region)
    lo = min(l1.min(), l2.min())
    hi = max(l1.max(), l2.max())
    ax.plot([lo, hi], [lo, hi], color="black", linewidth=0.8)
    ax.set_xlabel("Layer 1 (econometric, Fay-Herriot) log rate")
    ax.set_ylabel("Layer 2 (GeoAI boosting) log rate")
    ax.set_title("Layer 1 vs Layer 2 agreement — Shower Steamers")
    ax.legend(markerscale=3)
    fig.tight_layout()
    out = os.path.join(config.FIGURES_DIR, "layer_agreement.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out
