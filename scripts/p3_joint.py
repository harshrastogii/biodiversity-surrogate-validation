#!/usr/bin/env python
"""
p3_joint.py — FINAL confirmatory analysis: joint multivariate surrogate model vs individuals.
Question: does COMBINING open-data surrogates predict expert BIORISK better than the best single
surrogate, and does the gain GENERALISE (or is it overfitting)?

Design (honest, guards against overfitting/pseudoreplication):
  - Model = linear combiner (OLS on standardised raw surrogates), evaluated OUT-OF-SAMPLE by
      (a) SPATIAL-BLOCK CV: hold out whole (catchment x 10km-tile) blocks (k=10);
      (b) LEAVE-ONE-CATCHMENT-OUT (LOCO): train on 4 catchments, predict the 5th (transfer test).
  - Metric = Spearman(predicted, observed BIORISK) on held-out data, E-UNIT (unweighted) primary,
      E-AREA (area-weighted) companion.
  - Predictor sets: each single surrogate; CORE joint (landsys+nvis+convertibility+protection,
      preserves n); FULL joint (+DEA, on the smaller complete-case set).
  - Incremental value = test-Spearman(joint) - test-Spearman(best single), with block-bootstrap CI.
  - Overfitting check = train vs test Spearman gap; LOCO reveals transfer failure.
  - No catchment dummies in the transfer model (unknown for an unsurveyed area) — honest.
Writes analysis_p3/joint_{report.txt, results.csv, verdict.json}.
"""
import os, sys, json, warnings, itertools
import numpy as np, pandas as pd, geopandas as gpd
from scipy.stats import spearmanr, rankdata
from shapely import make_valid
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

OUT = os.path.join(C.V2, "analysis_p3"); os.makedirs(OUT, exist_ok=True)
B = 2000; rng = np.random.default_rng(42)
poly = pd.read_parquet(os.path.join(C.PROC, "harmonized_polygon.parquet"))

def centroids(name):
    b = C.BENCHMARKS[name]; g = gpd.read_file(b["path"], layer=b["layer"]).to_crs(C.CRS)
    g["geometry"] = make_valid(g.geometry); g = g[g.geometry.notna() & ~g.geometry.is_empty]
    g["bio"] = (g[b["field"]].map(C.BV_MAP) if b["scheme"] == "biovalue" else pd.to_numeric(g[b["field"]], errors="coerce"))
    g = g.dropna(subset=["bio"]); g = g[(g["bio"] >= 1) & (g["bio"] <= 5)].reset_index(drop=True)
    c = g.geometry.centroid
    return pd.DataFrame({"unit_id": [f"p{i}" for i in range(len(g))], "cx": c.x.values, "cy": c.y.values})

D = pd.concat([poly[poly.catchment == n].merge(centroids(n), on="unit_id") for n in C.BIORISK_POOL], ignore_index=True)
D["tile"] = D["catchment"] + "_" + (D.cx//10000).astype(int).astype(str) + "_" + (D.cy//10000).astype(int).astype(str)

SINGLES = ["sig_landsys", "sig_nvis_mvg", "cond_dea", "convertibility", "protection"]
CORE = ["sig_landsys", "sig_nvis_mvg", "convertibility", "protection"]
FULL = CORE + ["cond_dea"]

def fit_predict(train, test, preds):
    X = train[preds].values; y = train["biorisk_awm"].values
    mu = X.mean(0); sd = X.std(0); sd[sd == 0] = 1
    Xs = (X-mu)/sd; Xs = np.c_[np.ones(len(Xs)), Xs]
    beta, *_ = np.linalg.lstsq(Xs, y, rcond=None)
    Xt = (test[preds].values-mu)/sd; Xt = np.c_[np.ones(len(Xt)), Xt]
    return Xt@beta

def wspear(x, y, w=None):
    rx, ry = rankdata(x), rankdata(y)
    if w is None: return np.corrcoef(rx, ry)[0, 1]
    w = np.asarray(w, float); w /= w.sum(); mx = (w*rx).sum(); my = (w*ry).sum()
    return (w*(rx-mx)*(ry-my)).sum()/np.sqrt((w*(rx-mx)**2).sum()*(w*(ry-my)**2).sum())

def cc(preds):  # complete-case subset for a predictor set
    return D.dropna(subset=preds+["biorisk_awm"]).copy()

def blockcv(preds, k=10):
    d = cc(preds); tiles = d["tile"].unique(); rng.shuffle(tiles)
    folds = np.array_split(tiles, k); rec = []
    for f in folds:
        te = d[d.tile.isin(f)]; tr = d[~d.tile.isin(f)]
        if len(tr) < 20 or len(te) < 3: continue
        p = fit_predict(tr, te, preds)
        rec.append(pd.DataFrame({"pred": p, "obs": te["biorisk_awm"].values,
                                 "w": te["unit_km2"].values, "tile": te["tile"].values}))
    R = pd.concat(rec, ignore_index=True)
    return R, len(d)

def loco(preds):
    d = cc(preds); out = {}
    for name in C.BIORISK_POOL:
        te = d[d.catchment == name]; tr = d[d.catchment != name]
        if len(te) < 6 or len(tr) < 20: out[name] = np.nan; continue
        p = fit_predict(tr, te, preds)
        out[name] = spearmanr(p, te["biorisk_awm"]).correlation
    return out

def boot_ci(R, w=False):
    tiles = R.tile.unique(); by = {t: R.index[R.tile == t].values for t in tiles}
    obs = wspear(R.pred, R.obs, R.w if w else None); bs = []
    for _ in range(B):
        pick = rng.choice(tiles, len(tiles), replace=True)
        idx = np.concatenate([by[t] for t in pick]); s = R.loc[idx]
        bs.append(wspear(s.pred.values, s.obs.values, s.w.values if w else None))
    lo, hi = np.nanpercentile(bs, [2.5, 97.5]); return obs, lo, hi, np.array(bs)

# ---- spatial-block CV: singles vs joint ----
models = {**{s: [s] for s in SINGLES}, "CORE_joint": CORE, "FULL_joint": FULL}
res, bootcache = [], {}
for name, preds in models.items():
    R, n = blockcv(preds)
    for est, w in [("E-UNIT", False), ("E-AREA", True)]:
        # train (in-sample) skill for overfit check
        d = cc(preds); ptr = fit_predict(d, d, preds)
        tr_rho = wspear(ptr, d["biorisk_awm"].values, d["unit_km2"].values if w else None)
        o, lo, hi, bs = boot_ci(R, w); bootcache[(name, est)] = bs
        res.append(dict(model=name, n=n, estimand=est, test_rho=round(o, 3),
                        ci_lo=round(lo, 3), ci_hi=round(hi, 3), train_rho=round(tr_rho, 3),
                        overfit_gap=round(tr_rho-o, 3)))
res = pd.DataFrame(res)

# ---- incremental value: joint - best single (E-UNIT), block-bootstrap CI on delta ----
def delta(joint, est):
    singles_e = res[(res.model.isin(SINGLES)) & (res.estimand == est)]
    best = singles_e.loc[singles_e.test_rho.idxmax(), "model"]
    bj, bb = bootcache[(joint, est)], bootcache[(best, est)]
    m = min(len(bj), len(bb)); d = bj[:m]-bb[:m]
    return best, float(np.median(d)), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))

# ---- LOCO transfer ----
loco_core = loco(CORE); loco_best_nvis = loco(["sig_nvis_mvg"]); loco_conv = loco(["convertibility"])

# ---- report ----
L = ["P3 JOINT MULTIVARIATE MODEL — final confirmatory (spatially cross-validated)",
     "Out-of-sample Spearman(pred, expert BIORISK). Guards vs overfitting via block CV + LOCO.", ""]
L += ["SPATIAL-BLOCK CV (hold out catchment x 10km tiles):",
      f"  {'model':16s} {'est':6s} {'test_rho':>9s} {'95% CI':>16s} {'train':>6s} {'overfit_gap':>11s}"]
for _, r in res.sort_values(["estimand", "model"]).iterrows():
    L.append(f"  {r.model:16s} {r.estimand:6s} {r.test_rho:+9.3f} [{r.ci_lo:+.2f},{r.ci_hi:+.2f}] "
             f"{r.train_rho:+6.2f} {r.overfit_gap:+11.3f}")
L += ["", "INCREMENTAL VALUE of combining (joint - best single), E-UNIT, block-bootstrap CI:"]
for j in ["CORE_joint", "FULL_joint"]:
    best, md, lo, hi = delta(j, "E-UNIT")
    verdict = "ADDS value" if lo > 0 else ("NO added value" if hi < 0.02 else "inconclusive")
    L.append(f"  {j:12s} vs best single ({best}): Δrho={md:+.3f} [{lo:+.3f},{hi:+.3f}]  -> {verdict}")
L += ["", "LEAVE-ONE-CATCHMENT-OUT transfer (predict a held-out landscape), E-UNIT Spearman:",
      f"  {'held-out':10s} {'CORE_joint':>11s} {'NVIS-only':>10s} {'conv-only':>10s}"]
for name in C.BIORISK_POOL:
    def f(x): return f"{x[name]:+.3f}" if np.isfinite(x.get(name, np.nan)) else "   n/a"
    L.append(f"  {name:10s} {f(loco_core):>11s} {f(loco_best_nvis):>10s} {f(loco_conv):>10s}")
def mean_ok(x):
    v=[x[n] for n in C.BIORISK_POOL if np.isfinite(x.get(n,np.nan))]; return np.mean(v)
L.append(f"  {'MEAN':10s} {mean_ok(loco_core):+11.3f} {mean_ok(loco_best_nvis):+10.3f} {mean_ok(loco_conv):+10.3f}")
report = "\n".join(L); print(report)
open(os.path.join(OUT, "joint_report.txt"), "w").write(report+"\n")
res.to_csv(os.path.join(OUT, "joint_results.csv"), index=False)
json.dump(dict(blockcv=res.to_dict("records"),
               delta_core=delta("CORE_joint", "E-UNIT"), delta_full=delta("FULL_joint", "E-UNIT"),
               loco_core=loco_core, loco_nvis=loco_best_nvis, loco_conv=loco_conv),
          open(os.path.join(OUT, "joint_verdict.json"), "w"), indent=2, default=str)
print("\nwrote", OUT)
