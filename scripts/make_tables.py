#!/usr/bin/env python
"""
make_tables.py — manuscript and Supporting Information tables, generated from frozen outputs
(analysis_p3/, analysis_p4/) so that no number is typed by hand. Writes Markdown tables to
paper/tables/. Run after p4_revision.py.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

AP3 = os.path.join(C.V2, "analysis_p3")
AP4 = os.environ.get("P4_DIR", os.path.join(C.V2, "analysis_p4"))
OUT = os.environ.get("TABLE_DIR", os.path.join(C.V2, "paper", "tables")); os.makedirs(OUT, exist_ok=True)
NAME = {"sig_nvis_mvg": "Vegetation-type rarity (NVIS)", "sig_landsys": "Land-system rarity",
        "convertibility": "Convertibility", "cond_dea": "Vegetation cover (DEA)", "protection": "Protection",
        "nvis_partial": "NVIS, partial (land-system, convertibility)"}
CATCH = {"Roper": "Roper", "Larrimah": "Larrimah", "Wadeye": "Wadeye", "GunnPoint": "Gunn Point",
         "DeepWell": "Deep Well", "Weddell": "Greater Weddell"}
ORDER = ["sig_nvis_mvg", "sig_landsys", "convertibility", "cond_dea", "protection"]

def r3(v): return "n.e." if v is None or not np.isfinite(v) else f"{v:.3f}".replace("-", "−")
def ci(lo, hi): return "n.e." if not (np.isfinite(lo) and np.isfinite(hi)) else f"[{r3(lo)}, {r3(hi)}]"
def md(df):
    head = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
    return head + "\n".join("| " + " | ".join(str(v) for v in row) + " |" for row in df.values) + "\n"
def write(name, title, df, note=""):
    with open(os.path.join(OUT, f"{name}.md"), "w") as f:
        f.write(f"**{title}**\n\n" + md(df) + (f"\n{note}\n" if note else ""))
    print("wrote", name)
def p4(name): return pd.read_csv(os.path.join(AP4, name))

# ---------------------------------------------------------------- Table 1 benchmarks
b = p4("benchmarks.csv")
write("Table1_benchmarks", "Table 1. Expert benchmarks.", pd.DataFrame({
    "Area": [CATCH[c] for c in b.catchment],
    "Scale": ["biodiversity values (separate)" if c == "Weddell" else "BIORISK" for c in b.catchment],
    "Polygons": [f"{n:,}" for n in b.n_polygons],
    "Area (km²)": [f"{a:,.0f}" for a in b.area_km2],
    "Polygons per class (class: n)": b.classes,
    "Median polygon (ha)": [f"{v:.2f}" for v in b.median_polygon_ha],
    "Polygons < 1 ha (%)": [f"{v:.0f}" for v in b.pct_lt_1ha],
    "10 km blocks": b.n_tiles_10km}),
    "Counts are polygons with a valid class (1–5) after geometry repair. Analyses of each surrogate use "
    "the polygons where that surrogate is defined (pairwise deletion).")

# ---------------------------------------------------------------- Table 2 pooled agreement
m = p4("meta_hksj.csv"); s = p4("screening.csv")
from p4_revision import meta_auc  # same estimator as the analysis
rows = []
for q in ORDER + ["nvis_partial"]:
    row = {"Surrogate": NAME[q]}
    for est, lab in [("E-UNIT", "ρ per polygon"), ("E-AREA", "ρ area-weighted")]:
        r = m[(m.quantity == q) & (m.estimand == est)]
        row[lab] = f"{r3(r.est.iloc[0])} {ci(r.mhk_lo.iloc[0], r.mhk_hi.iloc[0])}" if len(r) else "—"
        if est == "E-UNIT": row["k"] = int(r.k.iloc[0]) if len(r) else "—"
    for thr, lab in [(">=4", "AUC class ≥ 4"), ("==5", "AUC class 5")]:
        g = s[(s.surrogate == q) & (s.threshold == thr) & (s.catchment != "Weddell")]
        if len(g):
            mm = meta_auc(g.auc.values, g.auc_var.values)
            row[lab] = f"{r3(mm['est'])} {ci(mm['mhk_lo'], mm['mhk_hi'])}"
        else:
            row[lab] = "—"
    rows.append(row)
write("Table2_pooled_agreement", "Table 2. Pooled agreement with expert BIORISK under four metrics.",
      pd.DataFrame(rows),
      "Random-effects meta-analysis over the estimable BIORISK catchments (k). Intervals are 95% modified "
      "Hartung–Knapp–Sidik–Jonkman intervals (t on k − 1 df) from spatial block-bootstrap variances (10 km blocks). "
      "Area-weighted ρ uses area-weighted mid-ranks. AUC: probability that a polygon in the higher class "
      "scores higher on the surrogate (0.5 = no discrimination). n.e. = not estimable.")

# ---------------------------------------------------------------- Table 3 joint model
j = p4("joint_paired.csv")
lab = {"CORE_joint": "Joint model (land-system + NVIS + convertibility + protection)", **NAME,
       "DELTA joint-NVIS (paired)": "Joint minus NVIS (paired)"}
loco = p4("loco.csv")
t3 = []
for mdl in ["CORE_joint", "sig_nvis_mvg", "sig_landsys", "convertibility", "DELTA joint-NVIS (paired)"]:
    w = j[(j["mode"] == "within") & (j.model == mdl)].iloc[0]; p = j[(j["mode"] == "pooled") & (j.model == mdl)].iloc[0]
    t3.append({"Model": lab[mdl], "Within-catchment ρ [95% CI]": f"{r3(w.test_rho)} {ci(w.ci_lo, w.ci_hi)}",
               "Pooled ρ [95% CI]": f"{r3(p.test_rho)} {ci(p.ci_lo, p.ci_hi)}"})
write("Table3_joint_model", "Table 3. Out-of-sample agreement of the joint model and single surrogates.",
      pd.DataFrame(t3),
      "Spatial-block cross-validation (10 km blocks, 10 folds, 20 repeats); all models fitted on the same "
      f"{int(j.n.iloc[0]):,} polygons with the same folds. The difference row is a paired block bootstrap "
      "stratified by catchment. Leave-one-catchment-out transfer of the joint model: " +
      "; ".join(f"{CATCH[r.catchment]} {r3(r.joint)}" for r in loco.itertuples()) + ".")

# ---------------------------------------------------------------- Supporting Information
dv = p4("multiverse_nvis_vs_landsys.csv")
write("TableS1_multiverse", "Table S1. Every specification: paired NVIS minus land-system difference.",
      pd.DataFrame({"Metric": dv.metric, "Min. polygon (ha)": dv.mmu_ha, "Class 1 excluded": dv.exclude_class1,
                    "Difference [mHKSJ 95% CI]": [f"{r3(a)} {ci(b_, c)}" for a, b_, c in zip(dv.diff_nvis_minus_landsys, dv.lo, dv.hi)],
                    "DL 95% CI": [ci(a, b_) for a, b_ in zip(dv.dl_lo, dv.dl_hi)], "k": dv.k,
                    "Highest-scoring surrogate": [NAME.get(x, x) for x in dv.best_surrogate]}))
g = p4("nvis_class_sensitivity.csv")
write("TableS2_nvis_groups", "Table S2. NVIS agreement after removing rare vegetation groups.",
      pd.DataFrame({"Area": [CATCH[c] for c in g.catchment], "Removed": g["drop"], "Polygons removed": g.n_dropped,
                    "ρ per polygon": [r3(v) for v in g.rho]}),
      "Groups are identified by their NT-wide rarity value (rounded to 3 d.p.); share of BIORISK ≥ 4 in brackets.")
mo = p4("modification_sensitivity.csv")
write("TableS3_modification", "Table S3. Pooled per-polygon ρ after excluding class 1 (nil or highly modified).",
      pd.DataFrame({"Surrogate": [NAME[q] for q in mo.quantity], "ρ [mHKSJ 95% CI]":
                    [f"{r3(a)} {ci(b_, c)}" for a, b_, c in zip(mo.est, mo.mhk_lo, mo.mhk_hi)], "k": mo.k}))
write("TableS4_meta_methods", "Table S4. Pooled estimates under three random-effects interval methods.",
      pd.DataFrame({"Quantity": [NAME[q] for q in m.quantity], "Estimand": m.estimand, "ρ": [r3(v) for v in m.est],
                    "DerSimonian–Laird": [ci(a, b_) for a, b_ in zip(m.dl_lo, m.dl_hi)],
                    "HKSJ": [ci(a, b_) for a, b_ in zip(m.hk_lo, m.hk_hi)],
                    "Modified HKSJ": [ci(a, b_) for a, b_ in zip(m.mhk_lo, m.mhk_hi)],
                    "I² (%)": [f"{v:.0f}" for v in m.I2], "k": m.k,
                    "Leave-one-out range": [ci(a, b_) for a, b_ in zip(m.loo_min, m.loo_max)],
                    "Catchments": m.catchments}))
w = p4("weddell.csv")
write("TableS5_weddell", "Table S5. Greater Weddell (biodiversity-values scale; not pooled).",
      pd.DataFrame({"Quantity": [NAME[q] for q in w.quantity], "Estimand": w.estimand, "ρ": [r3(v) for v in w.rho],
                    "Polygons": w.n, "10 km blocks": w.n_tiles}))
k3 = pd.read_csv(os.path.join(AP3, "meta.csv"))
write("TableS6_prespecified_knn", "Table S6. Results under the originally pre-specified inference (KNN effective sample size).",
      pd.DataFrame({"Surrogate": [NAME[q] for q in k3.surrogate], "Estimand": k3.estimand,
                    "ρ [95% CI]": [f"{r3(a)} {ci(b_, c)}" for a, b_, c in zip(k3.pooled_rho, k3.ci_lo, k3.ci_hi)],
                    "I² (%)": [f"{v:.0f}" for v in k3.I2], "k": k3.k}),
      "Pre-specified method (P3.PR2.2), replaced by the spatial block bootstrap after it was found to "
      "under-represent long-range dependence (Section 2.5).")
lv = pd.read_csv(os.path.join(AP3, "per_catchment.csv"))
write("TableS7_leverage", "Table S7. Area-weighted ρ before and after removing the largest 5% of polygons.",
      pd.DataFrame({"Area": [CATCH[c] for c in lv.catchment], "Surrogate": [NAME[q] for q in lv.surrogate],
                    "All polygons": [r3(v) for v in lv.rho_area], "Largest 5% removed": [r3(v) for v in lv.rho_area_lev]}),
      "Pre-specified leverage check (P3.PR2.5), applied to every surrogate. P3 weighting (unweighted ranks).")
mmu = p4("mmu_per_catchment.csv")
pv = mmu.pivot_table(index=["catchment", "surrogate"], columns="mmu_ha", values="rho").reset_index()
pv.columns = ["Area", "Surrogate"] + [f"≥ {c:g} ha" if c else "all" for c in pv.columns[2:]]
pv["Area"] = pv.Area.map(CATCH); pv["Surrogate"] = pv.Surrogate.map(NAME)
for c in pv.columns[2:]: pv[c] = pv[c].map(r3)
write("TableS8_polygon_size", "Table S8. Per-polygon ρ as polygons below a minimum area are removed.", pv)
