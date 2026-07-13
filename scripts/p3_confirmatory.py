#!/usr/bin/env python
"""
p3_confirmatory.py — CONFIRMATORY surrogate validation per PRE-REGISTRATION P3.PR1/PR2.
Unit = native expert polygon. Co-primary estimands E-UNIT (unweighted) & E-AREA (area-weighted).
Spatial-corrected effective n (KNN k=8), DerSimonian-Laird meta over 5 BIORISK catchments,
E-AREA leverage guardrail, and the NVIS vegetation-circularity control. Weddell separate.
Positives challenged as hard as negatives (PR2.8).

Reads harmonized_polygon.parquet (attributes) + re-derives polygon geometry from the benchmarks
(aligned on unit_id) for the spatial weights.
Writes outputs_p3/{report.txt, meta.csv, circularity.csv, verdict.json}.
"""
import os, sys, json, warnings
import numpy as np, pandas as pd, geopandas as gpd
from scipy.stats import spearmanr, rankdata, norm, chi2
from shapely import make_valid
import libpysal
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

OUT = os.path.join(C.V2, "analysis_p3"); os.makedirs(OUT, exist_ok=True)
SURR = ["sig_landsys", "sig_nvis_mvg", "cond_dea", "convertibility", "protection"]
poly = pd.read_parquet(os.path.join(C.PROC, "harmonized_polygon.parquet"))

def bench_centroids(name):
    """re-derive polygon geometry aligned to unit_id 'p{i}' (mirrors harmonize.load_benchmark)."""
    b = C.BENCHMARKS[name]
    g = gpd.read_file(b["path"], layer=b["layer"]).to_crs(C.CRS)
    g["geometry"] = make_valid(g.geometry)
    g = g[g.geometry.notna() & ~g.geometry.is_empty]
    if b["scheme"] == "biovalue":
        g["bio"] = g[b["field"]].map(C.BV_MAP)
    else:
        g["bio"] = pd.to_numeric(g[b["field"]], errors="coerce")
    g = g.dropna(subset=["bio"]); g = g[(g["bio"] >= 1) & (g["bio"] <= 5)].reset_index(drop=True)
    cen = g.geometry.centroid
    return pd.DataFrame({"unit_id": [f"p{i}" for i in range(len(g))],
                         "cx": cen.x.values, "cy": cen.y.values})

# ---- stats helpers ---------------------------------------------------------
def wspear(x, y, w):
    rx = rankdata(x); ry = rankdata(y); w = np.asarray(w, float); w = w / w.sum()
    mx = np.sum(w*rx); my = np.sum(w*ry)
    cov = np.sum(w*(rx-mx)*(ry-my)); vx = np.sum(w*(rx-mx)**2); vy = np.sum(w*(ry-my)**2)
    return cov/np.sqrt(vx*vy) if vx > 0 and vy > 0 else np.nan

def eff_n(cx, cy, x, y):
    n = len(x)
    if n < 6: return float(n)
    try:
        W = libpysal.weights.KNN.from_array(np.c_[cx, cy], k=min(8, n-1), silence_warnings=True)
        W.transform = "r"
        def lag1(v):
            r = rankdata(v); lg = libpysal.weights.lag_spatial(W, r)
            rc = r-r.mean(); lc = lg-lg.mean(); d = np.sqrt((rc**2).sum()*(lc**2).sum())
            return (rc*lc).sum()/d if d > 0 else 0.0
        rx, ry = lag1(x), lag1(y); den = 1+rx*ry
        ne = 1 + (n-1)*(1-rx*ry)/den if den != 0 else n
        return float(np.clip(ne, 3, n))
    except Exception:
        return float(n)

def fisher(rho, ne):
    rho = np.clip(rho, -0.999, 0.999); z = np.arctanh(rho)
    v = (1 + rho**2/2.0)/(ne-3) if ne > 3 else np.nan
    return z, v

def dl(zs, vs):
    zs, vs = np.asarray(zs, float), np.asarray(vs, float)
    ok = np.isfinite(zs) & np.isfinite(vs) & (vs > 0)
    zs, vs = zs[ok], vs[ok]; k = len(zs)
    if k == 0: return dict(rho=np.nan, lo=np.nan, hi=np.nan, p=np.nan, I2=np.nan, k=0)
    w = 1/vs; zf = np.sum(w*zs)/np.sum(w); Q = float(np.sum(w*(zs-zf)**2)); dfree = k-1
    Cc = np.sum(w)-np.sum(w**2)/np.sum(w); tau2 = max(0.0, (Q-dfree)/Cc) if Cc > 0 else 0.0
    wr = 1/(vs+tau2); zre = np.sum(wr*zs)/np.sum(wr); se = np.sqrt(1/np.sum(wr))
    I2 = max(0.0, (Q-dfree)/Q)*100 if Q > 0 else 0.0
    return dict(rho=float(np.tanh(zre)), lo=float(np.tanh(zre-1.96*se)),
                hi=float(np.tanh(zre+1.96*se)), p=float(2*(1-norm.cdf(abs(zre/se)))),
                I2=float(I2), k=k)

def partial_spearman(df, x, y, ctrl):
    d = df[[x, y]+ctrl].dropna()
    if len(d) < 10: return np.nan, len(d)
    R = {c: rankdata(d[c]) for c in [x, y]+ctrl}
    Z = np.c_[np.ones(len(d))] if not ctrl else np.c_[np.ones(len(d)), *[R[c] for c in ctrl]]
    def resid(v):
        beta, *_ = np.linalg.lstsq(Z, R[v], rcond=None); return R[v]-Z@beta
    ex, ey = resid(x), resid(y)
    return float(np.corrcoef(ex, ey)[0, 1]), len(d)

# ---- per-catchment estimates ----------------------------------------------
cen = {n: bench_centroids(n) for n in C.BIORISK_POOL + ["Weddell"]}
rows = []
for name in C.BIORISK_POOL:
    d = poly[poly.catchment == name].merge(cen[name], on="unit_id")
    for s in SURR:
        sub = d[[s, "biorisk_awm", "unit_km2", "cx", "cy"]].dropna()
        if len(sub) < 6 or sub[s].nunique() < 2:
            continue
        ru = spearmanr(sub[s], sub["biorisk_awm"]).correlation
        ra = wspear(sub[s].values, sub["biorisk_awm"].values, sub["unit_km2"].values)
        ne = eff_n(sub["cx"].values, sub["cy"].values, sub[s].values, sub["biorisk_awm"].values)
        # E-AREA leverage guardrail: drop largest 5% polygons
        thr = sub["unit_km2"].quantile(0.95); s2 = sub[sub["unit_km2"] <= thr]
        ra_lev = wspear(s2[s].values, s2["biorisk_awm"].values, s2["unit_km2"].values) if len(s2) > 6 else np.nan
        rows.append(dict(catchment=name, surrogate=s, n=len(sub), n_eff=round(ne, 1),
                         rho_unit=ru, rho_area=ra, rho_area_lev=ra_lev))
per = pd.DataFrame(rows)

# ---- meta-analysis per surrogate x estimand -------------------------------
meta = []
for s in SURR:
    sub = per[per.surrogate == s]
    for est, col in [("E-UNIT", "rho_unit"), ("E-AREA", "rho_area")]:
        zv = [fisher(r[col], r["n_eff"]) for _, r in sub.iterrows()]
        m = dl([z for z, v in zv], [v for z, v in zv])
        meta.append(dict(surrogate=s, estimand=est, pooled_rho=round(m["rho"], 4),
                         ci_lo=round(m["lo"], 4), ci_hi=round(m["hi"], 4),
                         p=round(m["p"], 4), I2=round(m["I2"], 1), k=m["k"]))
meta = pd.DataFrame(meta)

# ---- NVIS circularity control (PR2.6) -------------------------------------
circ = []
for name in C.BIORISK_POOL:
    d = poly[poly.catchment == name]
    # (a) partial NVIS | {landsys, convertibility}
    pr, npr = partial_spearman(d, "sig_nvis_mvg", "biorisk_awm", ["sig_landsys", "convertibility"])
    raw = spearmanr(*d[["sig_nvis_mvg", "biorisk_awm"]].dropna().values.T).correlation \
          if d[["sig_nvis_mvg", "biorisk_awm"]].dropna().shape[0] > 5 else np.nan
    # (b) restrict to 3-vs-4 core contrast
    d34 = d[d["biorisk_majority"].round().isin([3, 4])]
    sub34 = d34[["sig_nvis_mvg", "biorisk_awm"]].dropna()
    r34 = spearmanr(sub34["sig_nvis_mvg"], sub34["biorisk_awm"]).correlation if len(sub34) > 5 and sub34["sig_nvis_mvg"].nunique() > 1 else np.nan
    circ.append(dict(catchment=name, nvis_raw=round(raw, 3) if np.isfinite(raw) else np.nan,
                     nvis_partial=round(pr, 3) if np.isfinite(pr) else np.nan,
                     nvis_3v4=round(r34, 3) if np.isfinite(r34) else np.nan, n=npr))
circ = pd.DataFrame(circ)
# pooled partial (meta of per-catchment partials, unit weights via n_eff of nvis)
zvp = []
for _, r in circ.iterrows():
    ne = per[(per.catchment == r["catchment"]) & (per.surrogate == "sig_nvis_mvg")]["n_eff"]
    if len(ne) and np.isfinite(r["nvis_partial"]):
        zvp.append(fisher(r["nvis_partial"], ne.iloc[0]))
mp = dl([z for z, v in zvp], [v for z, v in zvp])

# ---- Weddell separate (PR2.7) ---------------------------------------------
wd = poly[poly.catchment == "Weddell"]
wed = {}
for s in SURR:
    sub = wd[[s, "biorisk_awm"]].dropna()
    wed[s] = round(spearmanr(sub[s], sub["biorisk_awm"]).correlation, 3) if len(sub) > 5 and sub[s].nunique() > 1 else None

# ---- co-primary verdict per surrogate -------------------------------------
def verdict(s):
    u = meta[(meta.surrogate == s) & (meta.estimand == "E-UNIT")].iloc[0]
    a = meta[(meta.surrogate == s) & (meta.estimand == "E-AREA")].iloc[0]
    up = u.ci_lo > 0; un = u.ci_hi < 0; an = a.ci_hi < 0; ap = a.ci_lo > 0
    uu = (not up and not un); au = (not ap and not an)
    if up and ap: return "VALIDATED (both estimands +)"
    if uu and au: return "NOT VALIDATED (both null)"
    if up and not ap: return "ESTIMAND-DEPENDENT (per-unit + / area not)"
    if ap and not up: return "ESTIMAND-DEPENDENT (area + / per-unit not)"
    return "MIXED/weak"

# ---- report ---------------------------------------------------------------
L = ["P3 CONFIRMATORY — surrogate validation (pre-registered P3.PR1/PR2)",
     "Unit=native expert polygon; co-primary E-UNIT/E-AREA; spatial-corrected n_eff; DL meta.", ""]
L += ["PER-CATCHMENT n_eff (spatial correction shrinks polygon counts drastically):"]
for name in C.BIORISK_POOL:
    sub = per[per.catchment == name]
    if len(sub):
        ex = sub.iloc[0]
        L.append(f"  {name:10s} n_poly~{int(ex['n']):6d}  n_eff~{ex['n_eff']:.0f}")
L += ["", "META-ANALYSIS (pooled over 5 BIORISK catchments), both estimands:"]
L.append(f"  {'surrogate':16s} {'estimand':8s} {'rho':>7s} {'95% CI':>18s} {'p':>7s} {'I2':>5s}  verdict")
for s in SURR:
    for est in ["E-UNIT", "E-AREA"]:
        r = meta[(meta.surrogate == s) & (meta.estimand == est)].iloc[0]
        vd = verdict(s) if est == "E-UNIT" else ""
        L.append(f"  {s:16s} {est:8s} {r.pooled_rho:+7.3f} [{r.ci_lo:+.3f},{r.ci_hi:+.3f}] {r.p:7.4f} {r.I2:5.0f}  {vd}")
L += ["", "E-AREA LEVERAGE GUARDRAIL (drop largest 5% polygons) — per catchment rho_area / rho_area_lev:"]
for name in C.BIORISK_POOL:
    sub = per[(per.catchment == name)]
    parts = [f"{r.surrogate.split('_')[-1][:4]}:{r.rho_area:+.2f}/{r.rho_area_lev:+.2f}" for _, r in sub.iterrows()]
    L.append(f"  {name:10s} " + "  ".join(parts))
L += ["", "NVIS VEGETATION-CIRCULARITY CONTROL (PR2.6) — challenges the NVIS positive:",
      f"  {'catchment':10s} {'raw':>7s} {'partial|LS,conv':>16s} {'3v4-only':>9s}"]
for _, r in circ.iterrows():
    L.append(f"  {r.catchment:10s} {str(r.nvis_raw):>7s} {str(r.nvis_partial):>16s} {str(r.nvis_3v4):>9s}")
L.append(f"  POOLED partial NVIS|(LS,conv): rho={mp['rho']:+.3f} [{mp['lo']:+.3f},{mp['hi']:+.3f}] p={mp['p']:.4f}  (k={mp['k']})")
L += ["", "WEDDELL (separate BioValues scheme, E-UNIT Spearman):",
      "  " + "  ".join(f"{k}={v}" for k, v in wed.items())]

report = "\n".join(L); print(report)
open(os.path.join(OUT, "report.txt"), "w").write(report+"\n")
per.to_csv(os.path.join(OUT, "per_catchment.csv"), index=False)
meta.to_csv(os.path.join(OUT, "meta.csv"), index=False)
circ.to_csv(os.path.join(OUT, "circularity.csv"), index=False)
json.dump(dict(meta=meta.to_dict("records"),
               nvis_partial_pooled=mp, weddell=wed,
               verdicts={s: verdict(s) for s in SURR}),
          open(os.path.join(OUT, "verdict.json"), "w"), indent=2)
print("\nwrote", OUT)
