#!/usr/bin/env python
"""
make_figures.py — publication figures. Reads ONLY frozen outputs in analysis_p4/ (and, for the
Figure 1 map, the benchmark geometries); recomputes no statistic. PDF (vector) + 300 dpi PNG.

  Figure 1  Study area and expert class composition (BIORISK pool; Greater Weddell on its own scale)
  Figure 2  Which surrogate looks best depends on the metric (pooled, modified-HKSJ 95% CI)
  Figure 3  Specification curve: paired NVIS minus land-system difference across all specifications
  Figure 4  Why verdicts flip: polygon size, rare vegetation groups, already-modified land
  Figure 5  Joint model versus NVIS (paired, same rows and folds) and leave-one-catchment-out transfer

Palette: Okabe-Ito subset, checked for colour-vision separation; every series is also labelled
directly, so identity never rests on colour alone.
"""
import os, sys, warnings
import numpy as np, pandas as pd
import matplotlib as mpl; mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

AP = os.environ.get("P4_DIR", os.path.join(C.V2, "analysis_p4"))
FIG = os.environ.get("FIG_DIR", os.path.join(C.V2, "paper", "figures")); os.makedirs(FIG, exist_ok=True)

mpl.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5, "axes.linewidth": 0.6,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 120,
    "savefig.bbox": "tight", "pdf.fonttype": 42, "ps.fonttype": 42,
    "axes.edgecolor": "0.35", "xtick.color": "0.35", "ytick.color": "0.35", "axes.labelcolor": "0.15",
})
MM = 1 / 25.4
INK, MUTED, RULE = "0.15", "0.45", "0.82"
SUR = ["sig_nvis_mvg", "sig_landsys", "convertibility", "cond_dea", "protection"]
SUR_NAME = {"sig_nvis_mvg": "Vegetation-type rarity (NVIS)", "sig_landsys": "Land-system rarity",
            "convertibility": "Convertibility", "cond_dea": "Vegetation cover (DEA)",
            "protection": "Protection"}
SUR_COL = {"sig_nvis_mvg": "#009E73", "sig_landsys": "#D55E00", "convertibility": "#E69F00",
           "cond_dea": "#0072B2", "protection": "#CC79A7"}
CATCH_LAB = {"Roper": "Roper", "Larrimah": "Larrimah", "Wadeye": "Wadeye", "GunnPoint": "Gunn Point",
             "DeepWell": "Deep Well", "Weddell": "Greater Weddell"}
METRIC_LAB = {"spearman_unit": "Spearman ρ,\nper polygon", "spearman_area": "Spearman ρ,\narea-weighted",
              "auc_ge4": "AUC,\nclass ≥ 4 vs rest", "auc_eq5": "AUC,\nclass 5 vs rest",
              "kendall_tau_b": "Kendall τ-b, per polygon"}

def read(name): return pd.read_csv(os.path.join(AP, name))

def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=300)
    plt.close(fig); print("wrote", name)

def panel(ax, letter, title):
    ax.set_title(f"({letter}) {title}", loc="left", fontweight="bold", color=INK)

# ===================================================================================== Figure 1
def fig1():
    import geopandas as gpd
    from shapely import make_valid
    poly = C.load_polygons()
    nt = gpd.read_file(os.path.join(C.V1, "data", "nt_boundary.gpkg")).to_crs(C.CRS)
    nt["geometry"] = nt.geometry.simplify(1000)
    foot = {}
    for name in C.BENCHMARKS:
        b = C.BENCHMARKS[name]; g = gpd.read_file(b["path"], layer=b["layer"]).to_crs(C.CRS)
        g["geometry"] = make_valid(g.geometry); foot[name] = g.union_all()
    LP = {"Roper": (200000, -250000, "left"), "Larrimah": (70000, -80000, "left"),
          "Wadeye": (-60000, 0, "right"), "GunnPoint": (-60000, 120000, "right"),
          "Weddell": (150000, -30000, "left"), "DeepWell": (70000, 0, "left")}
    fig = plt.figure(figsize=(174 * MM, 96 * MM))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.05], wspace=0.35)
    ax = fig.add_subplot(gs[0])
    nt.plot(ax=ax, color="0.95", zorder=0); nt.boundary.plot(ax=ax, color="0.45", linewidth=0.6)
    for name, u in foot.items():
        sep = name == "Weddell"; col = "#CC79A7" if sep else "#0072B2"; c = u.centroid
        gpd.GeoSeries([u], crs=C.CRS).plot(ax=ax, color=col, edgecolor=col, linewidth=0.5, zorder=4)
        ax.scatter([c.x], [c.y], s=26, facecolor="none", edgecolor=col, linewidth=1.0, zorder=5)
        dx, dy, ha = LP[name]
        ax.annotate(CATCH_LAB[name], (c.x, c.y), xytext=(c.x + dx, c.y + dy), fontsize=7, ha=ha,
                    va="center", color=INK, arrowprops=dict(arrowstyle="-", lw=0.5, color=MUTED))
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    sx, sy = x0 + 0.06 * (x1 - x0), y0 + 0.05 * (y1 - y0)            # 200 km scale bar
    ax.plot([sx, sx + 200000], [sy, sy], color=INK, lw=1.4)
    ax.text(sx + 100000, sy + 0.02 * (y1 - y0), "200 km", ha="center", fontsize=6.5, color=INK)
    ax.annotate("N", xy=(x1 - 0.06 * (x1 - x0), y1 - 0.04 * (y1 - y0)),
                xytext=(x1 - 0.06 * (x1 - x0), y1 - 0.14 * (y1 - y0)), ha="center", fontsize=7.5,
                arrowprops=dict(arrowstyle="-|>", lw=0.8, color=INK))
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    for s in ax.spines.values(): s.set_visible(False)
    panel(ax, "a", "Expert assessment areas")
    ax.legend(handles=[Patch(color="#0072B2", label="BIORISK scale (pooled)"),
                       Patch(color="#CC79A7", label="Biodiversity-values scale")],
              loc="upper left", bbox_to_anchor=(0.0, -0.02), frameon=False, fontsize=6.8, ncol=1)
    # (b) class composition by area, BIORISK pool; Weddell drawn on its own scale and legend
    ax2 = fig.add_subplot(gs[1])
    order = ["Roper", "GunnPoint", "Wadeye", "Larrimah", "DeepWell", "Weddell"]
    seq = ["#f1eef6", "#bdc9e1", "#74a9cf", "#2b8cbe", "#045a8d"]     # ordinal: light -> dark
    comp = (poly.groupby(["catchment", poly.biorisk_awm.astype(int)]).unit_km2.sum()
            .unstack(fill_value=0).reindex(index=order, columns=[1, 2, 3, 4, 5], fill_value=0))
    prop = comp.div(comp.sum(axis=1), axis=0) * 100
    ypos = np.arange(len(order))[::-1]; left = np.zeros(len(order))
    for k, cls in enumerate([1, 2, 3, 4, 5]):
        ax2.barh(ypos, prop[cls].values, left=left, color=seq[k], edgecolor="white", linewidth=0.8)
        left += prop[cls].values
    n = poly.groupby("catchment").size()
    ax2.set_yticks(ypos)
    ax2.set_yticklabels([f"{CATCH_LAB[c]}{' †' if c == 'Weddell' else ''}\n(n = {n[c]:,})" for c in order])
    ax2.set_xlabel("Share of assessed area (%)"); ax2.set_xlim(0, 100)
    panel(ax2, "b", "Expert class composition")
    labs = ["1 nil / highly modified", "2 low", "3 mitigable", "4 moderate", "5 high"]
    ax2.legend(handles=[Patch(color=seq[k], label=labs[k]) for k in range(5)], title="BIORISK class",
               ncol=3, loc="upper center", bbox_to_anchor=(0.45, -0.17), frameon=False,
               columnspacing=0.8, handlelength=0.9, fontsize=6.6, title_fontsize=7)
    ax2.text(0, -0.52, "† Greater Weddell uses a separate five-level biodiversity-values scale "
             "(highly modified, low, medium, high, very high), shown on the same shading; never pooled.",
             transform=ax2.transAxes, fontsize=6.2, color=MUTED, wrap=True)
    save(fig, "Figure1_study_area")

# ===================================================================================== Figure 2
def fig2():
    """Same estimates as Table 2: correlations from meta_hksj.csv (B = 2,000), AUCs pooled from
    screening.csv with the analysis's own meta_auc. Bars are modified-HKSJ intervals."""
    from p4_revision import meta_auc
    mh, scr = read("meta_hksj.csv"), read("screening.csv")
    def est(s, m):
        if m in ("spearman_unit", "spearman_area"):
            r = mh[(mh.quantity == s) & (mh.estimand == ("E-UNIT" if m == "spearman_unit" else "E-AREA"))]
            return None if not len(r) else (r.est.iloc[0], r.mhk_lo.iloc[0], r.mhk_hi.iloc[0])
        g = scr[(scr.surrogate == s) & (scr.threshold == (">=4" if m == "auc_ge4" else "==5"))
                & (scr.catchment != "Weddell")].dropna(subset=["auc", "auc_var"])
        if not len(g): return None
        mm = meta_auc(g.auc.values, g.auc_var.values); return (mm["est"], mm["mhk_lo"], mm["mhk_hi"])
    metrics = ["spearman_unit", "spearman_area", "auc_ge4", "auc_eq5"]
    fig, axes = plt.subplots(1, 4, figsize=(174 * MM, 64 * MM), sharey=True)
    yy = np.arange(len(SUR))[::-1]
    for j, (ax, m) in enumerate(zip(axes, metrics)):
        null = 0.5 if m.startswith("auc") else 0.0
        lim = (0.0, 1.0) if m.startswith("auc") else (-0.6, 0.8)
        ax.axvline(null, color=RULE, lw=0.8, zorder=0)
        vals = {s: est(s, m) for s in SUR}
        for y, s in zip(yy, SUR):
            if vals[s] is None:
                ax.text(null, y, "n.e.", ha="center", va="center", fontsize=6.5, color=MUTED); continue
            e, lo, hi = vals[s]
            ax.plot([max(lo, lim[0]), min(hi, lim[1])], [y, y], color=SUR_COL[s], lw=1.6, solid_capstyle="round")
            for end, mk in [(lo < lim[0], "<"), (hi > lim[1], ">")]:
                if end:
                    ax.plot([lim[0] if mk == "<" else lim[1]], [y], marker=mk, ms=4, color=SUR_COL[s], clip_on=False)
            ax.scatter([e], [y], s=30, color=SUR_COL[s], edgecolor="white", linewidth=0.8, zorder=3)
        cand = {s: v[0] for s, v in vals.items() if v is not None and s != "protection"}
        best = max(cand, key=cand.get)
        ax.scatter([cand[best]], [yy[SUR.index(best)]], s=90, facecolor="none", edgecolor=INK, linewidth=0.8, zorder=4)
        ax.set_xlabel(METRIC_LAB[m], fontsize=7.5); ax.set_xlim(*lim)
        panel(ax, "abcd"[j], "")
    axes[0].set_yticks(yy); axes[0].set_yticklabels([SUR_NAME[s] for s in SUR])
    fig.text(0.5, -0.14, "Points: pooled estimate over the BIORISK catchments; bars: modified-HKSJ 95% CI "
             "(arrowheads: interval continues beyond the axis); ring: highest-scoring candidate surrogate. "
             "n.e. = not estimable.", ha="center", fontsize=6.6, color=MUTED, wrap=True)
    save(fig, "Figure2_metric_dependence")

# ===================================================================================== Figure 3
def fig3():
    dv = read("multiverse_nvis_vs_landsys.csv").sort_values("diff_nvis_minus_landsys").reset_index(drop=True)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(174 * MM, 120 * MM), sharex=True,
                                 gridspec_kw=dict(height_ratios=[2.0, 1.5], hspace=0.08))
    pos, neg = dv.lo > 0, dv.hi < 0
    col = np.where(pos, "#009E73", np.where(neg, "#D55E00", "0.55"))
    for i, r in dv.iterrows():
        a1.plot([i, i], [r.lo, r.hi], color=col[i], lw=1.0)
    a1.scatter(dv.index, dv.diff_nvis_minus_landsys, c=col, s=16, zorder=3, edgecolor="white", linewidth=0.5)
    a1.axhline(0, color=INK, lw=0.6)
    a1.set_ylabel("NVIS minus land-system\n(paired; modified-HKSJ 95% CI)")
    a1.set_title(f"NVIS better: {int(pos.sum())}   land-system better: {int(neg.sum())}   "
                 f"inconclusive: {int((~pos & ~neg).sum())}   (of {len(dv)} specifications)",
                 loc="left", fontsize=7, color=INK)
    pad = 0.05 * (dv.hi.max() - dv.lo.min()); a1.set_ylim(dv.lo.min() - pad, dv.hi.max() + pad)
    choices = ([("metric", m, METRIC_LAB[m].replace("\n", " ")) for m in METRIC_LAB if m in dv.metric.unique()]
               + [("mmu_ha", v, f"polygons ≥ {v:g} ha" if v else "all polygons") for v in sorted(dv.mmu_ha.unique())]
               + [("exclude_class1", True, "class 1 excluded")])
    for j, (k, v, lab) in enumerate(choices):
        on = (dv[k] == v).values
        a2.scatter(np.where(on)[0], np.full(on.sum(), j), s=7, color=INK)
    a2.set_yticks(range(len(choices))); a2.set_yticklabels([c[2] for c in choices], fontsize=6.8)
    a2.invert_yaxis(); a2.set_xlabel("Specification (sorted by estimate)")
    for s in ["left", "bottom"]: a2.spines[s].set_color(RULE)
    save(fig, "Figure3_specification_curve")

# ===================================================================================== Figure 4
def fig4():
    poly = C.load_polygons()
    mmu = read("mmu_per_catchment.csv"); mvg = read("nvis_class_sensitivity.csv")
    mod_all = read("per_catchment_z.csv")
    fig, axes = plt.subplots(2, 2, figsize=(174 * MM, 140 * MM))
    (a, b), (c, d) = axes
    # (a) polygon size distribution
    lines = {"Roper": "-", "GunnPoint": "--", "Wadeye": ":", "Weddell": "-."}
    for name, ls in lines.items():
        ha = np.sort(np.clip(poly[poly.catchment == name].unit_km2.values * 100, 1e-4, None))
        a.plot(ha, np.arange(1, len(ha) + 1) / len(ha), ls=ls, color=INK, lw=1.1, label=CATCH_LAB[name])
    a.axvline(1, color="#009E73", lw=0.8)
    a.text(1.3, 0.04, "1 ha (one\nNVIS pixel)", fontsize=6.3, color=INK, va="bottom")
    a.set_xscale("log"); a.set_xlim(1e-4, 1e6)
    a.set_xlabel("Polygon area (ha; values below 0.0001 shown at 0.0001)", fontsize=7.5)
    a.set_ylabel("Cumulative share of polygons")
    a.legend(frameon=False, loc="center right", fontsize=6.6); panel(a, "a", "Polygon size")
    # (b) per-polygon agreement as small polygons are removed (Gunn Point, Wadeye)
    for name, ls in [("GunnPoint", "-"), ("Wadeye", "--")]:
        for s in ["sig_nvis_mvg", "sig_landsys"]:
            g = mmu[(mmu.catchment == name) & (mmu.surrogate == s)].sort_values("mmu_ha")
            x = g.mmu_ha.replace(0, 0.003)
            b.plot(x, g.rho, ls=ls, color=SUR_COL[s], lw=1.4, marker="o", ms=3)
            b.text(x.iloc[-1] * 1.15, g.rho.iloc[-1], f"{'NVIS' if s == 'sig_nvis_mvg' else 'land-system'}, {CATCH_LAB[name]}",
                   fontsize=6.3, va="center", color=INK)
    b.axhline(0, color=RULE, lw=0.8); b.set_xscale("log")
    b.set_xticks([0.003, 0.01, 0.1, 1, 5]); b.set_xticklabels(["all", "0.01", "0.1", "1", "5"])
    b.set_xlabel("Minimum polygon area kept (ha)"); b.set_ylabel("Spearman ρ, per polygon")
    b.set_xlim(0.002, 60); panel(b, "b", "Removing small polygons")
    # (c) NVIS with and without the rarest vegetation groups
    cats = ["Roper", "Wadeye", "GunnPoint", "Weddell"]; x = np.arange(len(cats)); w = 0.36
    v0 = [mvg[(mvg.catchment == k) & (mvg["drop"] == "none")].rho.iloc[0] for k in cats]
    v1 = [mvg[(mvg.catchment == k) & (mvg["drop"] == "all rarity>=0.25")].rho.iloc[0] for k in cats]
    c.bar(x - w / 2 - 0.01, v0, w, color="#009E73", label="all polygons")
    c.bar(x + w / 2 + 0.01, v1, w, color="#009E73", alpha=0.45, hatch="///", edgecolor="white",
          label="rarest groups removed (rarity ≥ 0.25)")
    c.axhline(0, color=INK, lw=0.6); c.set_xticks(x)
    c.set_xticklabels(["Roper", "Wadeye", "Gunn Point", "Greater\nWeddell"])
    c.set_ylim(-0.1, 0.85)
    c.set_ylabel("NVIS Spearman ρ, per polygon"); c.legend(frameon=False, loc="upper left", fontsize=6.6)
    panel(c, "c", "Removing rare vegetation groups")
    # (d) convertibility with and without already-modified land (class 1)
    pool = ["Roper", "GunnPoint", "Weddell"]          # the areas with class 1 polygons
    allc = pd.concat([mod_all, read("weddell.csv")]); nc1 = pd.concat([read("modification_per_catchment.csv"),
                                                                        read("modification_weddell.csv")])
    a0 = [allc[(allc.catchment == k) & (allc.quantity == "convertibility") & (allc.estimand == "E-UNIT")].rho
          for k in pool]
    a0 = [r.iloc[0] if len(r) else np.nan for r in a0]
    a1 = [nc1[(nc1.catchment == k) & (nc1.quantity == "convertibility") & (nc1.estimand == "E-UNIT")].rho for k in pool]
    a1 = [r.iloc[0] if len(r) else np.nan for r in a1]
    x = np.arange(len(pool))
    d.bar(x - w / 2 - 0.01, a0, w, color="#E69F00", label="all classes")
    d.bar(x + w / 2 + 0.01, a1, w, color="#E69F00", alpha=0.45, hatch="///", edgecolor="white",
          label="class 1 (already modified) removed")
    d.axhline(0, color=INK, lw=0.6); d.set_xticks(x)
    d.set_xticklabels([CATCH_LAB[k] if k != "Weddell" else "Greater\nWeddell" for k in pool])
    d.set_ylim(min(-0.05, np.nanmin(a0 + a1) - 0.03), max(0.3, np.nanmax(a0 + a1) + 0.1))
    d.set_ylabel("Convertibility Spearman ρ, per polygon"); d.legend(frameon=False, loc="upper left", fontsize=6.6)
    panel(d, "d", "Removing already-modified land")
    fig.tight_layout(h_pad=2.2, w_pad=2.5)
    save(fig, "Figure4_mechanisms")

# ===================================================================================== Figure 5
def fig5():
    j = read("joint_paired.csv"); j = j[j["mode"] == "within"]
    order = ["CORE_joint", "sig_nvis_mvg", "sig_landsys", "convertibility", "DELTA joint-NVIS (paired)"]
    lab = {"CORE_joint": "Joint model", "DELTA joint-NVIS (paired)": "Joint minus NVIS (paired)", **SUR_NAME}
    col = {"CORE_joint": INK, "DELTA joint-NVIS (paired)": MUTED, **SUR_COL}
    fig, (a, b) = plt.subplots(1, 2, figsize=(174 * MM, 70 * MM), gridspec_kw=dict(width_ratios=[1.1, 1]))
    yy = np.arange(len(order))[::-1]; a.axvline(0, color=RULE, lw=0.8)
    for y, m in zip(yy, order):
        r = j[j.model == m].iloc[0]
        a.plot([r.ci_lo, r.ci_hi], [y, y], color=col[m], lw=1.6)
        a.scatter([r.test_rho], [y], s=30, color=col[m], edgecolor="white", linewidth=0.8, zorder=3,
                  marker="D" if m == "CORE_joint" else "o")
    a.set_yticks(yy); a.set_yticklabels([lab[m] for m in order])
    a.set_xlabel("Out-of-sample Spearman ρ, within catchment\n(spatial-block CV; 95% CI)")
    panel(a, "a", "Combining surrogates")
    loco = read("loco.csv")
    x = np.arange(len(loco)); w = 0.36
    b.bar(x - w / 2 - 0.01, loco.joint, w, color=INK, label="joint model (weights transferred)")
    b.bar(x + w / 2 + 0.01, loco.nvis_raw, w, color="#009E73", label="NVIS alone")
    for i, r in enumerate(loco.itertuples()):
        for dx, v in [(-w / 2 - 0.01, r.joint), (w / 2 + 0.01, r.nvis_raw)]:
            if np.isfinite(v) and abs(v) < 0.005:
                b.text(i + dx, 0.01, "0", ha="center", va="bottom", fontsize=6.3, color=INK)
    b.set_ylim(min(0, np.nanmin(loco[["joint", "nvis_raw"]].values)) - 0.02, 0.75)
    b.axhline(0, color=INK, lw=0.6); b.set_xticks(x)
    b.set_xticklabels([CATCH_LAB[c] for c in loco.catchment], rotation=30, ha="right", rotation_mode="anchor")
    b.set_ylabel("Spearman ρ in held-out catchment"); b.legend(frameon=False, fontsize=6.6, loc="upper left")
    panel(b, "b", "Transfer to an unseen catchment")
    fig.tight_layout()
    save(fig, "Figure5_joint_model")

if __name__ == "__main__":
    only = sys.argv[1:]
    for k, f in [("1", fig1), ("2", fig2), ("3", fig3), ("4", fig4), ("5", fig5)]:
        if not only or k in only: f()
    print("figures ->", FIG)
