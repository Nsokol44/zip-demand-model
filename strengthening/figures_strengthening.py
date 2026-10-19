"""
figures_strengthening.py — the three strengthening figures, built to
the publication standard: matplotlib + geopandas + mapclassify,
colorblind-safe palettes (ColorBrewer sequential for choropleths;
Okabe-Ito for categorical series), consistent typography across the
set, panel labels, scale bar + north arrow on maps, vector masters
(PDF + SVG) plus 300 dpi PNGs.

Figure 5 (map pair): SIMULATED DGP-truth surface vs. OBSERVED
  ZBP 2022 outcome surface over the same ZCTA geographies. Both
  panels use the SAME six classes: Fisher-Jenks breaks computed on
  the POOLED distribution of the two log-rate surfaces (stated in
  the caption), so a given color means the same log-rate range in
  every panel. Simulated panels are titled SIMULATED; observed
  panels carry source + vintage.
Figure 6 (tier comparison): recovery / out-of-sample RMSE by
  estimator and top-decile overlap with the grading target, Tier 1
  vs. Tier 2. Levels are not commensurate across tiers (different
  grading targets); orderings are the content (manuscript caption).
Figure 7 (interval behaviour): nominal-95% Fay-Herriot coverage —
  Tier 1 canonical, Tier 1 bootstrap-calibrated (24-replicate mean
  +- 1 sd), Tier 2 behaviour against observed held-out rates.

Reads only computed artifacts. Writes to ../results/figures/.
"""

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
REPO = os.path.abspath(os.path.join(HERE, ".."))  # repo root (Tier 1 pipeline)
FIGDIR = os.path.join(ROOT, "results", "figures")
os.makedirs(FIGDIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif", "font.size": 9,
    "axes.titlesize": 9.5, "axes.labelsize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 8, "figure.dpi": 300,
    "axes.spines.top": False, "axes.spines.right": False,
    "svg.fonttype": "none",
})

# Okabe-Ito colorblind-safe categorical palette (consistent all set)
OI = {"blue": "#0072B2", "vermillion": "#D55E00", "sky": "#56B4E9",
      "green": "#009E73", "grey": "#7f7f7f", "orange": "#E69F00"}
EST_COLORS = {"OLS": OI["grey"], "Best spatial": OI["sky"],
              "Fay–Herriot": OI["blue"], "GeoAI": OI["vermillion"]}


def _save(fig, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(os.path.join(FIGDIR, f"{name}.{ext}"),
                    bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def _panel_label(ax, label):
    ax.text(0.015, 0.985, label, transform=ax.transAxes,
            fontsize=10, fontweight="bold", va="top", ha="left")


def _scale_bar(ax, length_m, label):
    """Simple two-segment scale bar, lower-left, in data coords."""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    bx = x0 + 0.04 * (x1 - x0)
    by = y0 + 0.035 * (y1 - y0)
    bh = 0.012 * (y1 - y0)
    for i, frac in enumerate((0.5, 0.5)):
        ax.add_patch(plt.Rectangle(
            (bx + i * length_m * 0.5, by), length_m * frac, bh,
            facecolor="black" if i == 0 else "white",
            edgecolor="black", lw=0.6, zorder=5))
    ax.text(bx + length_m / 2, by + bh * 1.7, label, ha="center",
            va="bottom", fontsize=7.5)


def _north_arrow(ax):
    ax.annotate("N", xy=(0.965, 0.94), xytext=(0.965, 0.855),
                xycoords="axes fraction", ha="center", va="center",
                fontsize=9, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", lw=1.0,
                                color="black"))


# ------------------------------------------------------------ Figure 5

def figure_maps():
    import geopandas as gpd
    import mapclassify as mc
    truth = pd.read_csv(os.path.join(REPO, "results",
                                     "grading_truth.csv"),
                        dtype={"zcta": str})
    bench = pd.read_csv(os.path.join(ROOT, "results",
                                     "benchmark_predictions.csv"),
                        dtype={"zcta": str})
    sim = truth.set_index("zcta")["true_log_rate_steamers"]
    obs = bench.set_index("zcta")["obs_log_rate_zbp22"]
    pooled = np.concatenate([sim.to_numpy(),
                             obs.dropna().to_numpy()])
    k = 6
    np.random.seed(20261013)  # FisherJenksSampled draws its fit
    # sample from numpy's RNG; seeding here keeps breaks exact.
    fj = mc.FisherJenksSampled(pooled, k=k, pct=0.25)
    edges = np.concatenate(([-np.inf], fj.bins, [np.inf]))
    cmap = ListedColormap(
        plt.get_cmap("YlOrBr")(np.linspace(0.25, 0.95, k)))
    labels = [f"{fj.bins[i-1]:.2f} – {fj.bins[i]:.2f}" if i > 0
              else f"≤ {fj.bins[0]:.2f}" for i in range(k)]
    labels[-1] = f"> {fj.bins[-2]:.2f}"

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.8))
    bars = {"southeast": (200_000, "200 km"), "nyc_metro": (20_000,
                                                           "20 km")}
    for row, region in enumerate(("southeast", "nyc_metro")):
        gname = {"southeast": "geometry_southeast.parquet",
                 "nyc_metro": "geometry_nyc.parquet"}[region]
        geo = gpd.read_parquet(os.path.join(
            REPO, "data", gname)).to_crs(5070)
        geo["sim"] = geo["zcta"].map(sim)
        geo["obs"] = geo["zcta"].map(obs)
        for field in ("sim", "obs"):
            geo[f"cls_{field}"] = np.digitize(
                geo[field].to_numpy(), fj.bins)
        for col, (field, title) in enumerate((
                ("sim", "SIMULATED — DGP truth (steamers)"),
                ("obs", "OBSERVED — ZBP 2022"))):
            ax = axes[row][col]
            geo.plot(column=f"cls_{field}", ax=ax, cmap=cmap,
                     vmin=-0.5,
                     vmax=k - 0.5, linewidth=0,
                     missing_kwds={"color": "#e5e5e5"})
            ax.set_title(("Southeast — " if row == 0
                          else "NYC metro — ") + title,
                         fontsize=8.2)
            ax.set_axis_off()
            _panel_label(ax, f"({chr(97 + row * 2 + col)})")
            _north_arrow(ax)
            lb, lt = bars[region]
            _scale_bar(ax, lb, lt)
    handles = [Patch(facecolor=cmap(i), label=labels[i])
               for i in range(k)]
    fig.legend(handles=handles, title="log count per household "
               "(identical classes, both data kinds)",
               loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, -0.055))
    _save(fig, "figure5_map_pair")
    return {"fisher_jenks_bins": [float(b) for b in fj.bins],
            "class_labels": labels}


# ------------------------------------------------------------ Figure 6

def _topdec(pred, target):
    k = int(round(0.10 * len(pred)))
    return len(set(np.argsort(pred)[-k:])
               & set(np.argsort(target)[-k:])) / k


def figure_tiers(bench):
    metrics = json.load(open(os.path.join(
        REPO, "results", "model_metrics.json")))
    scores = pd.read_csv(os.path.join(REPO, "results",
                                      "zip_scores.csv"),
                         dtype={"zcta": str})
    truth = pd.read_csv(os.path.join(REPO, "results",
                                     "grading_truth.csv"),
                        dtype={"zcta": str}).set_index("zcta")
    s = scores.set_index("zcta")
    tt = truth["true_log_rate_steamers"].reindex(s.index).to_numpy()
    t1_overlap = {
        "Fay–Herriot": _topdec(np.log(s["econ_est_rate"].to_numpy()),
                               tt),
        "GeoAI": _topdec(np.log(s["geoai_pred_rate"].to_numpy()), tt),
    }
    zbp = bench["outcomes"]["zbp22_establishments"]
    bus = bench["outcomes"]["soi22_business_returns"]
    labels = ["OLS", "Best spatial", "Fay–Herriot", "GeoAI"]
    keys = ["ols", "best_spatial", "fay_herriot", "geoai"]
    rmse_t1 = {"Steamers": [metrics["steamers"]["rmse_log_ols"],
                            metrics["steamers"]["rmse_log_best_model"],
                            metrics["steamers"]["rmse_log_fh"],
                            metrics["steamers"]["geoai"]
                            ["rmse_vs_truth"]],
               "Trio": [metrics["trio"]["rmse_log_ols"],
                        metrics["trio"]["rmse_log_best_model"],
                        metrics["trio"]["rmse_log_fh"],
                        metrics["trio"]["geoai"]["rmse_vs_truth"]]}
    rmse_t2 = {"ZBP 2022": [zbp[k]["rmse"] for k in keys],
               "SOI business": [bus[k]["rmse"] for k in keys]}

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.8),
                             gridspec_kw={"width_ratios": [1, 1, 0.7]})
    x = np.arange(4)
    for ax, data, title, lab in (
            (axes[0], rmse_t1,
             "Tier 1 — SIMULATION\nrecovery RMSE vs. truth", "(a)"),
            (axes[1], rmse_t2,
             "Tier 2 — REAL DATA\nout-of-sample RMSE vs. observed",
             "(b)")):
        w = 0.38
        for i, (series, vals) in enumerate(data.items()):
            ax.bar(x + (i - 0.5) * w, vals, w, label=series,
                   color=[OI["grey"], OI["blue"]][i])
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=28, ha="right")
        ax.set_title(title, fontsize=8.5, pad=20)
        ax.legend(frameon=False, loc="lower left",
                  bbox_to_anchor=(-0.02, 1.005), ncol=2,
                  columnspacing=1.0, handlelength=1.2)
        ax.grid(axis="y", lw=0.4, color="#cccccc")
        ax.set_axisbelow(True)
        ax.set_ylim(0, max(max(v) for v in data.values()) * 1.18)
        _panel_label(ax, lab)
    axes[0].set_ylabel("RMSE (log-rate scale)")
    ov = [t1_overlap["Fay–Herriot"], t1_overlap["GeoAI"],
          zbp["fay_herriot"]["top_decile_overlap"],
          zbp["geoai"]["top_decile_overlap"],
          bus["fay_herriot"]["top_decile_overlap"],
          bus["geoai"]["top_decile_overlap"]]
    names = ["T1\nFH", "T1\nGeoAI", "T2 FH\nZBP", "T2 GeoAI\nZBP",
             "T2 FH\nSOI", "T2 GeoAI\nSOI"]
    cols = [OI["blue"], OI["vermillion"]] * 3
    axes[2].bar(range(6), ov, color=cols)
    axes[2].set_xticks(range(6))
    axes[2].set_xticklabels(names, fontsize=6.6, rotation=22,
                            ha="right")
    axes[2].set_title("Top-decile overlap\nwith grading target",
                      fontsize=8.5)
    axes[2].set_ylim(0, 1.0)
    axes[2].grid(axis="y", lw=0.4, color="#cccccc")
    axes[2].set_axisbelow(True)
    _panel_label(axes[2], "(c)")
    _save(fig, "figure6_tier_comparison")
    return t1_overlap


# ------------------------------------------------------------ Figure 7

def figure_coverage(bench, calib):
    metrics = json.load(open(os.path.join(
        REPO, "results", "model_metrics.json")))
    groups, vals, errs, cols = [], [], [], []
    for prod, lab in (("steamers", "Stm"), ("trio", "Trio")):
        sm = calib["summary"][prod]
        groups += [f"T1 {lab}\nraw·s", f"T1 {lab}\ncal·s",
                   f"T1 {lab}\nraw·all", f"T1 {lab}\ncal·all"]
        vals += [metrics[prod]["coverage_sampled"],
                 sm["coverage_sampled_calibrated"]["mean"],
                 metrics[prod]["coverage"],
                 sm["coverage_all_calibrated"]["mean"]]
        errs += [0, sm["coverage_sampled_calibrated"]["sd"],
                 0, sm["coverage_all_calibrated"]["sd"]]
        cols += [OI["grey"], OI["blue"], OI["grey"], OI["blue"]]
    for key, lab in (("zbp22_establishments", "ZBP"),
                     ("soi22_returns", "SOI ret."),
                     ("soi22_business_returns", "SOI bus.")):
        groups.append(f"T2\n{lab}")
        vals.append(bench["outcomes"][key]
                    ["fh_interval_behaviour"]
                    ["coverage_vs_observed_nominal95"])
        errs.append(0)
        cols.append(OI["vermillion"])
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    x = np.arange(len(groups))
    ax.bar(x, vals, color=cols)
    xe = [xi for xi, e in zip(x, errs) if e > 0]
    ve = [v for v, e in zip(vals, errs) if e > 0]
    ee = [e for e in errs if e > 0]
    ax.errorbar(xe, ve, yerr=ee, fmt="none", ecolor="black",
                elinewidth=0.7, capsize=2)
    ax.axhline(0.95, color="black", lw=0.9, ls="--")
    ax.text(len(groups) - 0.45, 0.962, "nominal 95%", ha="right",
            fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=7.2)
    ax.set_ylabel("Coverage of nominal 95% intervals")
    ax.set_ylim(0, 1.06)
    ax.grid(axis="y", lw=0.4, color="#cccccc")
    ax.set_axisbelow(True)
    ax.set_title("Tier 1: coverage vs. known truth (grey = raw; "
                 "blue = calibrated,\n24 replicates, ±1 sd). "
                 "Tier 2: vs. observed held-out rates (behaviour)",
                 fontsize=8.5)
    _panel_label(ax, "(a)")
    _save(fig, "figure7_interval_coverage")


def main():
    bench = json.load(open(os.path.join(
        ROOT, "results", "benchmark_results.json")))
    calib = json.load(open(os.path.join(
        ROOT, "results", "calibration_results.json")))
    info = figure_maps()
    ov = figure_tiers(bench)
    figure_coverage(bench, calib)
    print("map class breaks:", info)
    print("Tier-1 steamers top-decile overlap vs truth:", ov)
    return 0


if __name__ == "__main__":
    sys.exit(main())
