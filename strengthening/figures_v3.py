"""
figures_v3.py — v3 figures (2026-10-18 review fixes A5, F6, F7, A2).

Figure 5 (A5): the v2 maps plotted two different quantities on
pooled classes, so the visual contrast was mostly level, and the
caption's "visibly rougher" was unsupported. v3 maps each surface
STANDARDISED (z-scores, common fixed breaks in sd units), so the
panels are commensurate in pattern, and the caption reports the
measured roughness statistics (roughness.json) instead of an
impression.
Figure 6 (F6): panel (b) now carries ALL FOUR Tier 2 evaluations
(v2 omitted SOI returns and the transfer) as 24-draw means +- 1 sd;
panel (c) is rebuilt with a legend and legible labels at final
size.
Figure 7 (A2): every Tier 1 value is now the 24-draw mean +- 1 sd
from the calibration study (v2 plotted the single canonical run
as the grey "raw" bars next to 24-draw calibrated means); Tier 2
values are means across the same 24 sample draws (tier2_draws).
Canonical-run values appear only as labelled diamond markers.

F7: map polygon fills are rasterised at 300 dpi inside the vector
masters (text, bars and axes stay vector), which takes the
Figure 5 PDF from 21 MB to well under 1 MB with no visible loss.

Reads computed artifacts only. Writes ../results/figures_v3/.
"""

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
REPO = os.path.abspath(os.path.join(HERE, ".."))  # repo root (Tier 1 pipeline)
FIGDIR = os.path.join(ROOT, "results", "figures_v3")
os.makedirs(FIGDIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif", "font.size": 9,
    "axes.titlesize": 9.5, "axes.labelsize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 8, "figure.dpi": 300,
    "axes.spines.top": False, "axes.spines.right": False,
    "svg.fonttype": "none",
})
OI = {"blue": "#0072B2", "vermillion": "#D55E00", "sky": "#56B4E9",
      "green": "#009E73", "grey": "#7f7f7f", "orange": "#E69F00",
      "purple": "#CC79A7"}
EST_LABELS = ["OLS", "Best spatial", "Fay–Herriot", "GeoAI"]
KEYS = ["ols", "best_spatial", "fay_herriot", "geoai"]


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
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    bx = x0 + 0.04 * (x1 - x0)
    by = y0 + 0.035 * (y1 - y0)
    bh = 0.012 * (y1 - y0)
    for i in range(2):
        ax.add_patch(plt.Rectangle(
            (bx + i * length_m * 0.5, by), length_m * 0.5, bh,
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
    truth = pd.read_csv(os.path.join(REPO, "results",
                                     "grading_truth.csv"),
                        dtype={"zcta": str})
    bench = pd.read_csv(os.path.join(ROOT, "results",
                                     "benchmark_predictions.csv"),
                        dtype={"zcta": str})
    sim = truth.set_index("zcta")["true_log_rate_steamers"]
    obs = bench.set_index("zcta")["obs_log_rate_zbp22"]

    def z(s):
        v = s.to_numpy(float)
        return (v - np.nanmean(v)) / np.nanstd(v)

    breaks = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    cmap = ListedColormap(plt.get_cmap("RdBu_r")(
        np.linspace(0.06, 0.94, 6)))
    norm = BoundaryNorm(np.concatenate(([-np.inf], breaks,
                                          [np.inf])), cmap.N)
    labels = ["≤ −2", "−2 to −1", "−1 to 0", "0 to 1", "1 to 2",
              "> 2"]

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.8))
    bars = {"southeast": (200_000, "200 km"),
            "nyc_metro": (20_000, "20 km")}
    for row, region in enumerate(("southeast", "nyc_metro")):
        gname = {"southeast": "geometry_southeast.parquet",
                 "nyc_metro": "geometry_nyc.parquet"}[region]
        geo = gpd.read_parquet(os.path.join(
            REPO, "data", gname)).to_crs(5070)
        geo["sim"] = z(geo["zcta"].map(sim))
        geo["obs"] = z(geo["zcta"].map(obs))
        for col, (field, title) in enumerate((
                ("sim", "SIMULATED — DGP truth (steamers)"),
                ("obs", "OBSERVED — ZBP 2022"))):
            ax = axes[row][col]
            geo.plot(column=field, ax=ax, cmap=cmap, norm=norm,
                     linewidth=0, rasterized=True,
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
               for i in range(6)]
    fig.legend(handles=handles,
               title="standardized log rate (z-score, sd units)",
               loc="lower center", ncol=6, frameon=False,
               bbox_to_anchor=(0.5, -0.05))
    _save(fig, "figure5_map_pair_z")


# ------------------------------------------------------------ Figure 6

def _topdec(pred, target):
    k = int(round(0.10 * len(pred)))
    return len(set(np.argsort(pred)[-k:])
               & set(np.argsort(target)[-k:])) / k


def figure_tiers(bench, draws):
    metrics = json.load(open(os.path.join(
        REPO, "results", "model_metrics.json")))
    scores = pd.read_csv(os.path.join(REPO, "results",
                                      "zip_scores.csv"),
                         dtype={"zcta": str})
    truth = pd.read_csv(os.path.join(REPO, "results",
                                     "grading_truth.csv"),
                        dtype={"zcta": str}).set_index("zcta")
    s = scores.set_index("zcta")
    # zip_scores.csv carries Layer 1 / Layer 2 rates for the demo
    # product (steamers) only, so Tier 1 overlap is steamers only.
    tt = truth["true_log_rate_steamers"].reindex(s.index).to_numpy()
    t1_overlap = {
        "Fay–Herriot": _topdec(
            np.log(s["econ_est_rate"].to_numpy()), tt),
        "GeoAI": _topdec(
            np.log(s["geoai_pred_rate"].to_numpy()), tt),
    }
    rmse_t1 = {p.capitalize(): [metrics[p]["rmse_log_ols"],
                               metrics[p]["rmse_log_best_model"],
                               metrics[p]["rmse_log_fh"],
                               metrics[p]["geoai"]["rmse_vs_truth"]]
               for p in ("steamers", "trio")}
    outcomes = [("zbp22_establishments", "ZBP"),
                ("soi22_returns", "SOI ret"),
                ("soi22_business_returns", "SOI bus"),
                ("temporal_transfer_zbp19_to_zbp22", "Transf")]
    ds = draws["summary"]

    fig, axes = plt.subplots(1, 3, figsize=(7.6, 3.4),
                             gridspec_kw={"width_ratios":
                                          [1, 1.3, 1.15]})
    x = np.arange(4)
    # (a) Tier 1 canonical
    ax = axes[0]
    w = 0.38
    for i, (series, vals) in enumerate(rmse_t1.items()):
        ax.bar(x + (i - 0.5) * w, vals, w, label=series,
               color=[OI["grey"], OI["blue"]][i])
    ax.set_xticks(x)
    ax.set_xticklabels(EST_LABELS, rotation=24, ha="right",
                       fontsize=7.6)
    ax.set_title("Tier 1 — SIMULATION\nrecovery RMSE vs. truth",
                 fontsize=8.5, pad=24)
    ax.legend(frameon=False, loc="lower left",
              bbox_to_anchor=(-0.03, 1.01), ncol=2,
              columnspacing=0.9, handlelength=1.1, fontsize=7.6)
    ax.set_ylabel("RMSE (log-rate scale)")
    ax.set_ylim(0, 0.78)
    ax.grid(axis="y", lw=0.4, color="#cccccc")
    ax.set_axisbelow(True)
    _panel_label(ax, "(a)")
    # (b) Tier 2: 24-draw means, all four outcomes
    ax = axes[1]
    w = 0.19
    colors = [OI["blue"], OI["orange"], OI["green"], OI["purple"]]
    for i, (key, lab) in enumerate(outcomes):
        means = [ds[key]["rmse"][k]["mean"] for k in KEYS]
        sds = [ds[key]["rmse"][k]["sd"] for k in KEYS]
        ax.bar(x + (i - 1.5) * w, means, w, label=lab,
               color=colors[i])
        ax.errorbar(x + (i - 1.5) * w, means, yerr=sds, fmt="none",
                    ecolor="black", elinewidth=0.6, capsize=1.6)
    ax.set_xticks(x)
    ax.set_xticklabels(EST_LABELS, rotation=24, ha="right",
                       fontsize=7.6)
    ax.set_title("Tier 2 — REAL DATA\nout-of-sample RMSE "
                 "(24-draw mean \u00b1 1 sd)", fontsize=8.5, pad=24)
    ax.legend(frameon=False, loc="lower left",
              bbox_to_anchor=(-0.03, 1.01), ncol=4,
              columnspacing=0.7, handlelength=1.0, fontsize=7.2)
    ax.set_ylim(0, 0.95)
    ax.grid(axis="y", lw=0.4, color="#cccccc")
    ax.set_axisbelow(True)
    _panel_label(ax, "(b)")
    # (c) top-decile overlap: Tier 1 canonical + Tier 2 draw means
    # v4.1 fix: tick labels rotated fully vertical (90 deg). The
    # v3/v4 single-line labels at rotation 26 physically
    # overlapped each other at final size (verified on the
    # packaged PNG, 2026-10-19 audit-response pass); two-line
    # wraps at rotations 26 and 90 were also tried and still
    # interleaved (the panel's ~0.25 in tick pitch is narrower
    # than any multi-column label block). Single-line labels at
    # 90 deg have a one-line-height horizontal footprint
    # (~0.11 in) and are collision-free. Values are unchanged.
    ax = axes[2]
    groups = ["T1 FH", "T1 GeoAI"]
    vals = [t1_overlap["Fay–Herriot"], t1_overlap["GeoAI"]]
    cols = [OI["blue"], OI["vermillion"]]
    errs = [0, 0]
    for key, lab in outcomes:
        for layer, col in (("fay_herriot", OI["blue"]),
                           ("geoai", OI["vermillion"])):
            groups.append(f"{lab} "
                          f"{'FH' if layer == 'fay_herriot' else 'GeoAI'}")
            vals.append(ds[key]["top_decile_overlap"][layer]
                        ["mean"])
            errs.append(ds[key]["top_decile_overlap"][layer]
                        ["sd"])
            cols.append(col)
    xb = np.arange(len(groups))
    ax.bar(xb, vals, color=cols)
    xe = [i for i, e in enumerate(errs) if e > 0]
    ax.errorbar(xe, [vals[i] for i in xe],
                yerr=[errs[i] for i in xe], fmt="none",
                ecolor="black", elinewidth=0.6, capsize=1.6)
    ax.set_xticks(xb)
    ax.set_xticklabels(groups, fontsize=7.2, rotation=90,
                       ha="right", va="top")
    ax.set_title("Top-decile overlap\nwith grading target",
                 fontsize=8.5, pad=24)
    ax.set_ylim(0, 1.02)
    ax.grid(axis="y", lw=0.4, color="#cccccc")
    ax.set_axisbelow(True)
    handles = [Patch(facecolor=OI["blue"], label="Fay–Herriot"),
               Patch(facecolor=OI["vermillion"], label="GeoAI")]
    ax.legend(handles=handles, frameon=False, loc="lower left",
              bbox_to_anchor=(-0.03, 1.01), ncol=2,
              columnspacing=0.9, handlelength=1.1, fontsize=7.6)
    _panel_label(ax, "(c)")
    _save(fig, "figure6_tier_comparison_v3")


# ------------------------------------------------------------ Figure 7

def figure_coverage(calib, draws):
    metrics = json.load(open(os.path.join(
        REPO, "results", "model_metrics.json")))
    groups, vals, errs, cols, canon = [], [], [], [], []
    for prod, lab in (("steamers", "Stm"), ("trio", "Trio")):
        sm = calib["summary"][prod]
        groups += [f"T1 {lab}\nraw·samp", f"T1 {lab}\ncal·samp",
                   f"T1 {lab}\nraw·all", f"T1 {lab}\ncal·all"]
        vals += [sm["coverage_sampled"]["mean"],
                 sm["coverage_sampled_calibrated"]["mean"],
                 sm["coverage_all"]["mean"],
                 sm["coverage_all_calibrated"]["mean"]]
        errs += [sm["coverage_sampled"]["sd"],
                 sm["coverage_sampled_calibrated"]["sd"],
                 sm["coverage_all"]["sd"],
                 sm["coverage_all_calibrated"]["sd"]]
        cols += [OI["grey"], OI["blue"], OI["grey"], OI["blue"]]
        canon += [metrics[prod]["coverage_sampled"], None,
                  metrics[prod]["coverage"], None]
    ds = draws["summary"]
    for key, lab in (("zbp22_establishments", "ZBP"),
                     ("soi22_returns", "SOI ret."),
                     ("soi22_business_returns", "SOI bus."),
                     ("temporal_transfer_zbp19_to_zbp22",
                      "Transf.")):
        groups.append(f"T2\n{lab}")
        vals.append(ds[key]["fh_coverage"]["mean"])
        errs.append(ds[key]["fh_coverage"]["sd"])
        cols.append(OI["vermillion"])
        canon.append(None)
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    x = np.arange(len(groups))
    ax.bar(x, vals, color=cols)
    ax.errorbar(x, vals, yerr=errs, fmt="none", ecolor="black",
                elinewidth=0.7, capsize=2)
    cx = [xi for xi, c in enumerate(canon) if c is not None]
    ax.plot(cx, [canon[i] for i in cx], "D", color="black", ms=4,
            label="canonical single run (Tier 1)")
    ax.axhline(0.95, color="black", lw=0.9, ls="--")
    # v4.1 fix: white bbox so the dashed 0.95 line no longer
    # strikes through the label text (verified on the packaged
    # PNG, 2026-10-19 audit-response pass).
    ax.text(len(groups) - 0.45, 0.962, "nominal 95%", ha="right",
            fontsize=8,
            bbox=dict(facecolor="white", edgecolor="none",
                      pad=1.0))
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=7.2, rotation=26,
                       ha="right")
    ax.set_ylabel("Coverage of nominal 95% intervals")
    ax.set_ylim(0, 1.08)
    ax.grid(axis="y", lw=0.4, color="#cccccc")
    ax.set_axisbelow(True)
    ax.set_title("All bars are 24-draw means ± 1 sd. Tier 1: vs. "
                 "known truth. Tier 2: vs. observed held-out "
                 "rates (behaviour)", fontsize=8.5)
    # v4.1 fix: the v3/v4 legend sat at lower-left INSIDE the axes
    # and its text printed across bars 1-3 (verified on the
    # packaged PNG, 2026-10-19 audit-response pass). Move it
    # below the axes, clear of the bars and the tick labels.
    ax.legend(frameon=False, loc="upper center",
              bbox_to_anchor=(0.5, -0.30), fontsize=7.5)
    _panel_label(ax, "(a)")
    _save(fig, "figure7_interval_coverage_v3")


def main():
    bench = json.load(open(os.path.join(
        ROOT, "results", "benchmark_results.json")))
    calib = json.load(open(os.path.join(
        ROOT, "results", "calibration_results.json")))
    draws = json.load(open(os.path.join(
        ROOT, "results", "tier2_draws.json")))
    figure_maps()
    figure_tiers(bench, draws)
    figure_coverage(calib, draws)
    return 0


if __name__ == "__main__":
    sys.exit(main())
