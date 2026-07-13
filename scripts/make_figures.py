#!/usr/bin/env python
"""
make_figures.py — publication figures for the V2 manuscript (Diversity and Distributions).
Reads ONLY the frozen analysis outputs (analysis_p3/*.json,*.csv) and the benchmark geometries
(for the study-area map); recomputes NO statistic. Every plotted value is taken verbatim from the
frozen pipeline. Outputs PDF (vector) + 300 dpi PNG to ../paper/figures/.
"""
import os, sys, json, warnings
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib as mpl; mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from shapely import make_valid
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

AP = os.path.join(C.V2, "analysis_p3")
FIG = os.path.join(C.V2, "paper", "figures"); os.makedirs(FIG, exist_ok=True)

# ---- publication style ----
mpl.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9, "axes.linewidth": 0.7,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 120,
    "savefig.bbox": "tight", "pdf.fonttype": 42, "ps.fonttype": 42,
})
MM = 1/25.4
# Okabe-Ito colourblind-safe palette
OI = dict(blue="#0072B2", orange="#E69F00", green="#009E73", vermillion="#D55E00",
          purple="#CC79A7", sky="#56B4E9", yellow="#F0E442", grey="#7F7F7F", black="#111111")

SUR_NAME = {"sig_nvis_mvg": "Vegetation-type rarity (NVIS)", "convertibility": "Convertibility",
            "cond_dea": "Vegetation cover (DEA)", "sig_landsys": "Land-system rarity",
            "protection": "Protection"}
SUR_COL = {"sig_nvis_mvg": OI["green"], "convertibility": OI["orange"], "cond_dea": OI["sky"],
           "sig_landsys": OI["vermillion"], "protection": OI["grey"]}
CATCH = ["Roper", "Larrimah", "Wadeye", "GunnPoint", "DeepWell"]
CATCH_LAB = {"Roper": "Roper", "Larrimah": "Larrimah", "Wadeye": "Wadeye",
             "GunnPoint": "Gunn Point", "DeepWell": "Deep Well"}

def load():
    hv = json.load(open(f"{AP}/hardened_verdict.json"))
    jv = json.load(open(f"{AP}/joint_verdict.json"))
    per = pd.read_csv(f"{AP}/per_catchment.csv")
    circ = pd.read_csv(f"{AP}/circularity.csv")
    return hv, jv, per, circ
HV, JV, PER, CIRC = load()

def meta_row(meta, surr, est):
    for r in meta:
        if r["surrogate"] == surr and r["estimand"] == est:
            return r
    return None

def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=300)
    plt.close(fig); print("wrote", name)

# =====================================================================================
# FIGURE 1 — Study area + BIORISK class composition
# =====================================================================================
def biorisk_composition():
    rows = {}
    for name in CATCH + ["Weddell"]:
        b = C.BENCHMARKS[name]; g = gpd.read_file(b["path"], layer=b["layer"]).to_crs(C.CRS)
        g["geometry"] = make_valid(g.geometry); g = g[g.geometry.notna() & ~g.geometry.is_empty]
        g["bio"] = (g[b["field"]].map(C.BV_MAP) if b["scheme"] == "biovalue"
                    else pd.to_numeric(g[b["field"]], errors="coerce"))
        g = g.dropna(subset=["bio"]); g = g[(g.bio >= 1) & (g.bio <= 5)]
        g["km2"] = g.area/1e6
        rows[name] = g.groupby(g.bio.astype(int))["km2"].sum()
    return pd.DataFrame(rows).T.reindex(columns=[1, 2, 3, 4, 5]).fillna(0.0)

def fig1():
    comp = biorisk_composition()
    nt = gpd.read_file(os.path.join(C.V1, "data", "nt_boundary.gpkg")).to_crs(C.CRS)
    nt["geometry"] = nt.geometry.simplify(2000)   # 2 km tolerance -> small vector file
    cents, foot = {}, {}
    for name in CATCH + ["Weddell"]:
        b = C.BENCHMARKS[name]; g = gpd.read_file(b["path"], layer=b["layer"]).to_crs(C.CRS)
        u = g.union_all(); foot[name] = u; cents[name] = u.centroid

    # explicit label offsets (metres) + alignment to avoid overlap in the Darwin/Roper clusters
    LP = {"Roper":     (70000,  70000, "left"),
          "Larrimah":  (70000, -80000, "left"),
          "Wadeye":    (-55000,     0, "right"),
          "GunnPoint": (20000, 120000, "left"),
          "Weddell":   (120000, -10000, "left"),
          "DeepWell":  (70000,      0, "left")}

    fig = plt.figure(figsize=(170*MM, 92*MM))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.0], wspace=0.30)
    ax = fig.add_subplot(gs[0])
    nt.plot(ax=ax, color="0.94", zorder=0)
    nt.boundary.plot(ax=ax, color="0.4", linewidth=0.7)
    for name in CATCH + ["Weddell"]:
        c = cents[name]; sep = name == "Weddell"; col = OI["purple"] if sep else OI["blue"]
        dx, dy, ha = LP[name]
        # actual assessment footprint (tiny at NT scale) + a marker so small areas stay visible
        gpd.GeoSeries([foot[name]], crs=C.CRS).plot(ax=ax, color=col, edgecolor=col, linewidth=0.5, zorder=4)
        ax.scatter([c.x], [c.y], s=30, facecolor="none", edgecolor=col, linewidth=1.1, zorder=5)
        ax.annotate(CATCH_LAB.get(name, "Greater Weddell"), (c.x, c.y),
                    xytext=(c.x+dx, c.y+dy), fontsize=7.5, ha=ha, va="center", zorder=6,
                    arrowprops=dict(arrowstyle="-", lw=0.5, color="0.45"))
    ax.set_title("(a) Expert assessment extents", loc="left", fontweight="bold")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_aspect("equal")
    ax.legend(handles=[Patch(color=OI["blue"], label="BIORISK catchments (pooled)"),
                       Patch(color=OI["purple"], label="Greater Weddell (separate scheme)")],
              loc="lower left", frameon=False, fontsize=7)

    ax2 = fig.add_subplot(gs[1])
    classcol = {1: "#c9c9c9", 2: OI["sky"], 3: OI["yellow"], 4: OI["orange"], 5: OI["vermillion"]}
    classlab = {1: "1 nil", 2: "2 low", 3: "3 mitigable", 4: "4 moderate", 5: "5 high"}
    prop = comp.div(comp.sum(axis=1), axis=0) * 100
    order = ["Roper", "GunnPoint", "Wadeye", "Larrimah", "DeepWell", "Weddell"]
    prop = prop.reindex(order); ypos = np.arange(len(order))[::-1]
    left = np.zeros(len(order))
    for cls in [1, 2, 3, 4, 5]:
        vals = prop[cls].values
        ax2.barh(ypos, vals, left=left, color=classcol[cls], edgecolor="white", linewidth=0.4,
                 label=classlab[cls])
        left += vals
    ax2.set_yticks(ypos)
    ax2.set_yticklabels([CATCH_LAB.get(n, "Gt Weddell") for n in order])
    ax2.set_xlabel("Share of assessed area (%)")
    ax2.set_xlim(0, 100)
    ax2.set_title("(b) BIORISK class composition", loc="left", fontweight="bold")
    ax2.legend(title="BIORISK class", ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.22),
               frameon=False, columnspacing=0.9, handlelength=0.9, handletextpad=0.4)
    save(fig, "Figure1_study_area")

# =====================================================================================
# FIGURE 2 — Surrogate benchmarking forest plot (E-UNIT)
# =====================================================================================
def fig2():
    order = ["sig_nvis_mvg", "convertibility", "cond_dea", "sig_landsys", "protection"]
    fig, ax = plt.subplots(figsize=(120*MM, 78*MM))
    ax.axvline(0, color="0.6", lw=0.8, ls="--", zorder=0)
    yy = np.arange(len(order))[::-1]
    for y, s in zip(yy, order):
        # per-catchment points
        pc = PER[(PER.surrogate == s)]
        for _, r in pc.iterrows():
            ax.scatter(r["rho_unit"], y + 0.0, s=16, color=SUR_COL[s], alpha=0.35,
                       edgecolor="none", zorder=2)
        # pooled diamond + block-bootstrap CI
        m = meta_row(HV["meta_10km"], s, "E-UNIT")
        ax.plot([m["ci_lo"], m["ci_hi"]], [y, y], color=SUR_COL[s], lw=1.8, zorder=3)
        ax.scatter([m["pooled_rho"]], [y], marker="D", s=52, color=SUR_COL[s],
                   edgecolor="black", linewidth=0.6, zorder=4)
        ax.text(0.60, y, f"{m['pooled_rho']:+.2f} [{m['ci_lo']:+.2f}, {m['ci_hi']:+.2f}]",
                ha="left", va="center", fontsize=6.8, color="0.25")
    ax.axvline(0.55, color="0.85", lw=0.6, zorder=1)  # light separator before value column
    ax.set_yticks(yy); ax.set_yticklabels([SUR_NAME[s] for s in order])
    ax.set_xlabel("Spearman ρ with expert BIORISK (per expert unit)")
    ax.set_xlim(-0.45, 1.12)
    ax.set_xticks([-0.4, -0.2, 0.0, 0.2, 0.4])
    ax.set_title("Surrogate benchmarking (pooled block-bootstrap meta)", loc="left", fontweight="bold")
    ax.scatter([], [], s=16, color="0.5", alpha=0.4, label="per-catchment estimate")
    ax.scatter([], [], marker="D", s=52, color="0.5", edgecolor="black", linewidth=0.6,
               label="pooled meta (95% CI)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, frameon=False, fontsize=7.5)
    save(fig, "Figure2_surrogate_benchmarking")

# =====================================================================================
# FIGURE 3 — Estimand & scale sensitivity
# =====================================================================================
def fig3():
    order = ["sig_nvis_mvg", "convertibility", "cond_dea", "sig_landsys", "protection"]
    fig, axes = plt.subplots(1, 2, figsize=(170*MM, 78*MM)); a, b = axes
    yy = np.arange(len(order))[::-1]
    # (a) two estimands
    a.axvline(0, color="0.6", lw=0.8, ls="--", zorder=0)
    for y, s in zip(yy, order):
        mu = meta_row(HV["meta_10km"], s, "E-UNIT"); ma = meta_row(HV["meta_10km"], s, "E-AREA")
        a.plot([mu["ci_lo"], mu["ci_hi"]], [y+0.16, y+0.16], color=OI["blue"], lw=1.5)
        a.scatter([mu["pooled_rho"]], [y+0.16], s=34, color=OI["blue"], edgecolor="black", lw=0.5, zorder=4)
        a.plot([ma["ci_lo"], ma["ci_hi"]], [y-0.16, y-0.16], color=OI["orange"], lw=1.5)
        a.scatter([ma["pooled_rho"]], [y-0.16], s=34, color=OI["orange"], edgecolor="black", lw=0.5, zorder=4)
    a.set_yticks(yy); a.set_yticklabels([SUR_NAME[s] for s in order])
    a.set_xlabel("Pooled Spearman ρ"); a.set_xlim(-0.65, 0.9)
    a.set_title("(a) Estimand sensitivity", loc="left", fontweight="bold")
    a.scatter([], [], s=34, color=OI["blue"], edgecolor="black", lw=0.5, label="per unit (E-UNIT)")
    a.scatter([], [], s=34, color=OI["orange"], edgecolor="black", lw=0.5, label="per area (E-AREA)")
    a.legend(loc="lower right", frameon=False, fontsize=7)
    # (b) tile-size sensitivity (E-UNIT)
    tiles = [("meta_5km", "5 km"), ("meta_10km", "10 km"), ("meta_20km", "20 km")]
    xpos = np.arange(3)
    for s in order:
        ys = [meta_row(HV[k], s, "E-UNIT")["pooled_rho"] for k, _ in tiles]
        b.plot(xpos, ys, "-o", color=SUR_COL[s], lw=1.4, ms=4, label=SUR_NAME[s])
    b.axhline(0, color="0.6", lw=0.8, ls="--", zorder=0)
    b.set_xticks(xpos); b.set_xticklabels([t for _, t in tiles])
    b.set_xlabel("Spatial block size"); b.set_ylabel("Pooled Spearman ρ (per unit)")
    b.set_title("(b) Scale (block-size) robustness", loc="left", fontweight="bold")
    b.set_xlim(-0.3, 2.3); b.legend(loc="center right", frameon=False, fontsize=6.6)
    save(fig, "Figure3_estimand_scale_sensitivity")

# =====================================================================================
# FIGURE 4 — NVIS circularity control
# =====================================================================================
def fig4():
    cats = [c for c in CATCH if c in CIRC.catchment.values]
    fig, ax = plt.subplots(figsize=(130*MM, 74*MM))
    ax.axhline(0, color="0.6", lw=0.8, ls="--", zorder=0)
    x = np.arange(len(cats)); w = 0.26
    series = [("nvis_raw", "raw", OI["green"]), ("nvis_partial", "partial | land-system, convertibility", OI["blue"]),
              ("nvis_3v4", "class 3-vs-4 only", OI["orange"])]
    for i, (col, lab, colr) in enumerate(series):
        vals = [CIRC.loc[CIRC.catchment == c, col].values[0] for c in cats]
        vals = [np.nan if pd.isna(v) else v for v in vals]
        ax.bar(x + (i-1)*w, vals, w, color=colr, edgecolor="white", linewidth=0.4, label=lab)
    ax.set_xticks(x); ax.set_xticklabels([CATCH_LAB[c] for c in cats])
    ax.set_ylabel("Spearman ρ (NVIS vs BIORISK)")
    ax.set_title("NVIS circularity control", loc="left", fontweight="bold")
    # pooled partial band
    cp = HV["circularity_partial_pooled"]
    ax.axhspan(cp["lo"], cp["hi"], color=OI["blue"], alpha=0.10, zorder=0)
    ax.axhline(cp["rho"], color=OI["blue"], lw=1.0, ls=":", zorder=1)
    ax.text(len(cats)-0.5, cp["rho"], f" pooled partial\n {cp['rho']:+.2f} [{cp['lo']:+.2f}, {cp['hi']:+.2f}]",
            va="center", ha="left", fontsize=6.6, color=OI["blue"])
    ax.set_xlim(-0.6, len(cats)-0.1+0.9)
    ax.legend(loc="upper center", bbox_to_anchor=(0.42, 1.0), frameon=False, fontsize=6.8)
    save(fig, "Figure4_circularity_control")

# =====================================================================================
# FIGURE 5 — Joint model & transfer
# =====================================================================================
def fig5():
    bc = {r["model"]: r for r in JV["blockcv"] if r["estimand"] == "E-UNIT"}
    order = ["CORE_joint", "FULL_joint", "sig_nvis_mvg", "convertibility", "sig_landsys",
             "cond_dea", "protection"]
    lab = {"CORE_joint": "Core joint", "FULL_joint": "Full joint (+DEA)", **SUR_NAME}
    fig, axes = plt.subplots(1, 2, figsize=(170*MM, 78*MM)); a, b = axes
    # (a) block-CV forest
    a.axvline(0, color="0.6", lw=0.8, ls="--", zorder=0)
    yy = np.arange(len(order))[::-1]
    for y, m in zip(yy, order):
        r = bc[m]; joint = m.endswith("joint")
        col = OI["black"] if joint else "0.45"
        a.plot([r["ci_lo"], r["ci_hi"]], [y, y], color=col, lw=1.7)
        a.scatter([r["test_rho"]], [y], marker=("D" if joint else "o"),
                  s=(52 if joint else 34), color=col, edgecolor="black", lw=0.5, zorder=4)
    a.set_yticks(yy); a.set_yticklabels([lab[m] for m in order])
    a.set_xlabel("Out-of-sample Spearman ρ (spatial-block CV)"); a.set_xlim(-0.25, 0.45)
    a.set_title("(a) Predictive skill: single vs joint", loc="left", fontweight="bold")
    dc = JV["delta_core"]
    a.text(0.98, 0.03, f"combining vs best single:\nΔρ = {float(dc[1]):+.3f} [{float(dc[2]):+.2f}, {float(dc[3]):+.2f}] (n.s.)",
           transform=a.transAxes, ha="right", va="bottom", fontsize=6.6, color="0.25")
    # (b) LOCO transfer
    loco = {"Core joint": JV["loco_core"], "NVIS only": JV["loco_nvis"], "Convertibility": JV["loco_conv"]}
    cols = {"Core joint": OI["black"], "NVIS only": OI["green"], "Convertibility": OI["orange"]}
    x = np.arange(len(CATCH)); w = 0.26
    for i, (k, d) in enumerate(loco.items()):
        vals = [np.nan if (d.get(c) is None or (isinstance(d.get(c), float) and np.isnan(d.get(c)))) else d[c] for c in CATCH]
        b.bar(x + (i-1)*w, vals, w, color=cols[k], edgecolor="white", linewidth=0.4, label=k)
    b.axhline(0, color="0.6", lw=0.8, ls="--", zorder=0)
    b.set_xticks(x); b.set_xticklabels([CATCH_LAB[c] for c in CATCH], rotation=20, ha="right")
    b.set_ylabel("Transfer Spearman ρ (held-out catchment)")
    b.set_title("(b) Leave-one-catchment-out transfer", loc="left", fontweight="bold")
    b.legend(loc="upper left", frameon=False, fontsize=7)
    save(fig, "Figure5_joint_model_transfer")

if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5()
    print("all figures ->", FIG)
