#!/usr/bin/env python
"""
p3_blockboot.py — HARDENED spatial inference for the P3 confirmatory analysis.
Replaces the KNN(k=8) effective-n (which under-captured long-range dependence and gave
over-optimistic CIs, see RESEARCH_LOG T3.1) with a SPATIAL BLOCK BOOTSTRAP: polygons are
assigned to contiguous spatial tiles (default 10 km, = V1 autocorrelation band); tiles are
resampled with replacement so whole neighbourhoods move together. Per-catchment bootstrap
Fisher-z variances feed the DerSimonian-Laird meta. Reported for BOTH co-primary estimands
and for the NVIS circularity partial. Sensitivity: 5 km and 20 km tiles.

Writes analysis_p3/hardened_{report.txt, meta.csv, verdict.json}.
"""
import os, sys, json, warnings
import numpy as np, pandas as pd, geopandas as gpd
from scipy.stats import spearmanr, rankdata, norm, chi2
from shapely import make_valid
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

OUT = os.path.join(C.V2, "analysis_p3"); os.makedirs(OUT, exist_ok=True)
SURR = ["sig_landsys", "sig_nvis_mvg", "cond_dea", "convertibility", "protection"]
B = 2000; SEED = 42; rng = np.random.default_rng(SEED)
poly = pd.read_parquet(os.path.join(C.PROC, "harmonized_polygon.parquet"))

def bench_centroids(name):
    b = C.BENCHMARKS[name]
    g = gpd.read_file(b["path"], layer=b["layer"]).to_crs(C.CRS)
    g["geometry"] = make_valid(g.geometry)
    g = g[g.geometry.notna() & ~g.geometry.is_empty]
    g["bio"] = (g[b["field"]].map(C.BV_MAP) if b["scheme"] == "biovalue"
                else pd.to_numeric(g[b["field"]], errors="coerce"))
    g = g.dropna(subset=["bio"]); g = g[(g["bio"] >= 1) & (g["bio"] <= 5)].reset_index(drop=True)
    cen = g.geometry.centroid
    return pd.DataFrame({"unit_id": [f"p{i}" for i in range(len(g))], "cx": cen.x.values, "cy": cen.y.values})

CEN = {n: bench_centroids(n) for n in C.BIORISK_POOL}

def wspear(x, y, w=None):
    rx = rankdata(x); ry = rankdata(y)
    if w is None:
        return np.corrcoef(rx, ry)[0, 1]
    w = np.asarray(w, float); w = w/w.sum()
    mx = np.sum(w*rx); my = np.sum(w*ry)
    cov = np.sum(w*(rx-mx)*(ry-my)); vx = np.sum(w*(rx-mx)**2); vy = np.sum(w*(ry-my)**2)
    return cov/np.sqrt(vx*vy) if vx > 0 and vy > 0 else np.nan

def blockboot(sub, xcol, ycol, tile_m, weighted):
    """spatial block bootstrap: resample tiles with replacement. Returns obs, z_var, lo, hi, n_tiles."""
    x = sub[xcol].to_numpy(float); y = sub[ycol].to_numpy(float)
    w = sub["unit_km2"].to_numpy(float) if weighted else None
    tx = np.floor(sub["cx"].to_numpy()/tile_m).astype(int)
    ty = np.floor(sub["cy"].to_numpy()/tile_m).astype(int)
    tid = tx*100000 + ty
    tiles = np.unique(tid)
    ntile = len(tiles)
    obs = wspear(x, y, w)
    if ntile < 3:
        return obs, np.nan, np.nan, np.nan, ntile
    idx_by_tile = {t: np.where(tid == t)[0] for t in tiles}
    boots = np.empty(B)
    for b in range(B):
        pick = rng.choice(tiles, size=ntile, replace=True)
        idx = np.concatenate([idx_by_tile[t] for t in pick])
        wi = w[idx] if weighted else None
        boots[b] = wspear(x[idx], y[idx], wi)
    boots = boots[np.isfinite(boots)]
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    z = np.arctanh(np.clip(boots, -0.999, 0.999))
    return obs, float(np.var(z)), float(lo), float(hi), ntile

def dl(zs, vs):
    zs, vs = np.asarray(zs, float), np.asarray(vs, float)
    ok = np.isfinite(zs) & np.isfinite(vs) & (vs > 0)
    zs, vs = zs[ok], vs[ok]; k = len(zs)
    if k == 0: return dict(rho=np.nan, lo=np.nan, hi=np.nan, p=np.nan, I2=np.nan, k=0)
    w = 1/vs; zf = np.sum(w*zs)/np.sum(w); Q = float(np.sum(w*(zs-zf)**2)); dfree = k-1
    Cc = np.sum(w)-np.sum(w**2)/np.sum(w); tau2 = max(0.0, (Q-dfree)/Cc) if Cc > 0 else 0.0
    wr = 1/(vs+tau2); zre = np.sum(wr*zs)/np.sum(wr); se = np.sqrt(1/np.sum(wr))
    I2 = max(0.0, (Q-dfree)/Q)*100 if Q > 0 else 0.0
    return dict(rho=float(np.tanh(zre)), lo=float(np.tanh(zre-1.96*se)), hi=float(np.tanh(zre+1.96*se)),
                p=float(2*(1-norm.cdf(abs(zre/se)))), I2=float(I2), k=k)

def frame(name):
    return poly[poly.catchment == name].merge(CEN[name], on="unit_id")

def run(tile_m):
    per, meta = [], []
    for name in C.BIORISK_POOL:
        d = frame(name)
        for s in SURR:
            for est, wtd in [("E-UNIT", False), ("E-AREA", True)]:
                sub = d[[s, "biorisk_awm", "unit_km2", "cx", "cy"]].dropna()
                if len(sub) < 6 or sub[s].nunique() < 2:
                    continue
                obs, zv, lo, hi, nt = blockboot(sub, s, "biorisk_awm", tile_m, wtd)
                per.append(dict(catchment=name, surrogate=s, estimand=est, rho=round(obs, 3),
                                ci_lo=round(lo, 3) if np.isfinite(lo) else np.nan,
                                ci_hi=round(hi, 3) if np.isfinite(hi) else np.nan,
                                n_tiles=nt, z_var=zv))
    per = pd.DataFrame(per)
    for s in SURR:
        for est in ["E-UNIT", "E-AREA"]:
            sub = per[(per.surrogate == s) & (per.estimand == est)]
            zs = np.arctanh(np.clip(sub["rho"].values, -0.999, 0.999)); vs = sub["z_var"].values
            m = dl(zs, vs)
            meta.append(dict(surrogate=s, estimand=est, pooled_rho=round(m["rho"], 3),
                             ci_lo=round(m["lo"], 3), ci_hi=round(m["hi"], 3),
                             p=round(m["p"], 4), I2=round(m["I2"], 0), k=m["k"]))
    return per, pd.DataFrame(meta)

# NVIS circularity partial, block-bootstrapped (E-UNIT)
def partial_boot(name, tile_m):
    d = frame(name)
    sub = d[["sig_nvis_mvg", "biorisk_awm", "sig_landsys", "convertibility", "unit_km2", "cx", "cy"]].dropna()
    if len(sub) < 12:
        return np.nan, np.nan
    def pcorr(idx):
        R = {c: rankdata(sub[c].values[idx]) for c in ["sig_nvis_mvg", "biorisk_awm", "sig_landsys", "convertibility"]}
        Z = np.c_[np.ones(len(idx)), R["sig_landsys"], R["convertibility"]]
        rx = R["sig_nvis_mvg"] - Z@np.linalg.lstsq(Z, R["sig_nvis_mvg"], rcond=None)[0]
        ry = R["biorisk_awm"] - Z@np.linalg.lstsq(Z, R["biorisk_awm"], rcond=None)[0]
        return np.corrcoef(rx, ry)[0, 1]
    tid = (np.floor(sub["cx"]/tile_m).astype(int)*100000 + np.floor(sub["cy"]/tile_m).astype(int)).values
    tiles = np.unique(tid);
    if len(tiles) < 3: return pcorr(np.arange(len(sub))), np.nan
    obs = pcorr(np.arange(len(sub)))
    idx_by = {t: np.where(tid == t)[0] for t in tiles}
    bs = []
    for _ in range(B):
        pick = rng.choice(tiles, size=len(tiles), replace=True)
        idx = np.concatenate([idx_by[t] for t in pick])
        try: bs.append(pcorr(idx))
        except Exception: pass
    z = np.arctanh(np.clip(np.array(bs), -0.999, 0.999))
    return obs, float(np.var(z))

# ---- main -----------------------------------------------------------------
per10, meta10 = run(10000)
_, meta05 = run(5000)
_, meta20 = run(20000)

# circularity partial meta (10 km)
zc, vc, rows = [], [], []
for name in C.BIORISK_POOL:
    o, v = partial_boot(name, 10000)
    rows.append(dict(catchment=name, partial=round(o, 3) if np.isfinite(o) else np.nan))
    if np.isfinite(o) and np.isfinite(v) and v > 0:
        zc.append(np.arctanh(np.clip(o, -0.999, 0.999))); vc.append(v)
mp = dl(zc, vc)

L = ["P3 HARDENED — spatial BLOCK BOOTSTRAP inference (10 km tiles; 5/20 km sensitivity)",
     f"B={B}, seed={SEED}. Tiles resampled with replacement (contiguous neighbourhoods).", ""]
L += ["n_tiles per catchment (E-UNIT, sig_nvis_mvg) — the true replication scale:"]
for name in C.BIORISK_POOL:
    r = per10[(per10.catchment == name) & (per10.surrogate == "sig_nvis_mvg") & (per10.estimand == "E-UNIT")]
    if len(r): L.append(f"  {name:10s} n_tiles(10km)={int(r.iloc[0]['n_tiles'])}")
L += ["", "HARDENED META (block-bootstrap CIs), 10 km tiles:",
      f"  {'surrogate':16s} {'estimand':8s} {'rho':>7s} {'95% CI':>18s} {'p':>7s} {'I2':>4s} k"]
for _, r in meta10.iterrows():
    L.append(f"  {r.surrogate:16s} {r.estimand:8s} {r.pooled_rho:+7.3f} [{r.ci_lo:+.3f},{r.ci_hi:+.3f}] {r.p:7.4f} {r.I2:4.0f} {r.k}")
L += ["", "TILE-SIZE SENSITIVITY (E-UNIT pooled rho [CI]):  5km | 10km | 20km"]
for s in SURR:
    def g(m):
        rr = m[(m.surrogate == s) & (m.estimand == "E-UNIT")]
        return f"{rr.iloc[0].pooled_rho:+.3f}[{rr.iloc[0].ci_lo:+.2f},{rr.iloc[0].ci_hi:+.2f}]" if len(rr) else "n/a"
    L.append(f"  {s:16s} {g(meta05)} | {g(meta10)} | {g(meta20)}")
L += ["", "NVIS CIRCULARITY PARTIAL (block-bootstrap, 10 km): per-catchment + pooled",
      "  " + "  ".join(f"{r['catchment']}={r['partial']}" for r in rows),
      f"  POOLED partial NVIS|(LS,conv): rho={mp['rho']:+.3f} [{mp['lo']:+.3f},{mp['hi']:+.3f}] p={mp['p']:.4f} k={mp['k']}"]
report = "\n".join(L); print(report)
open(os.path.join(OUT, "hardened_report.txt"), "w").write(report+"\n")
meta10.to_csv(os.path.join(OUT, "hardened_meta.csv"), index=False)
json.dump(dict(meta_10km=meta10.to_dict("records"), meta_5km=meta05.to_dict("records"),
               meta_20km=meta20.to_dict("records"), circularity_partial_pooled=mp,
               circularity_per_catchment=rows),
          open(os.path.join(OUT, "hardened_verdict.json"), "w"), indent=2)
print("\nwrote", OUT)
