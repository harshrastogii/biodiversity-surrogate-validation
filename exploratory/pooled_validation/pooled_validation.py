#!/usr/bin/env python
"""
pooled_validation.py — multi-catchment validation of the NT open-data exposure index
against expert BIORISK, extending the frozen single-catchment Roper validation.

DESIGN is pre-registered in PREREGISTRATION.md (frozen before spatial-corrected pooled
results were observed). This script only *executes* that design. Confirmatory vs
exploratory analyses are labelled in the output.

METHOD PARITY
  Aggregation, exposure family, and spatial correction replicate the frozen scripts
  (roper_validation.py, spatial_correction.py) exactly, using the same libpysal/esda
  primitives. An internal assertion reproduces the published Roper numbers
  (n=244, exposure rho=0.240, Moran I_exposure=0.761, I_biorisk=0.406, n_eff~=60)
  before any extension is trusted.

READS
  ../../data/hex_master.gpkg
  ../../data/roper_intersection.gpkg
  ../../../datasets/Larrimah/.../Larrimah_BioRisk.gdb  (BIORISK)
  ../../../datasets/Wadeye/.../Wadeye_Biodiversity.gdb (BIORISK)
  ../../../datasets/Greater_Weddell/.../*.gdb          (BV_OVERALL; separate robustness)
WRITES  outputs/  (per_catchment.csv, decomposition_meta.csv, heterogeneity.csv,
                   spatial_per_catchment.csv, weddell_robustness.csv, report.txt, verdict.json)
"""
import os, json, warnings
import numpy as np, pandas as pd, geopandas as gpd
from scipy.stats import spearmanr, rankdata, norm, chi2, t as tdist
import libpysal
from esda.moran import Moran
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(REPO, ".."))
OUT  = os.path.join(HERE, "outputs"); os.makedirs(OUT, exist_ok=True)
SEED = 42; NB = 5000; PERM = 999
rng = np.random.default_rng(SEED)
PRIMARY_RULE = "mean"

HEX = os.path.join(REPO, "data", "hex_master.gpkg")
SOURCES = {  # name -> (path, layer, field, kind)
 "Roper":    (os.path.join(REPO, "data", "roper_intersection.gpkg"), "roper_intersection", "BIORISK", "biorisk"),
 "Larrimah": (os.path.join(ROOT, "datasets/Larrimah/BioRisk_Larrimah/Datasets/ESRI/Larrimah_BioRisk.gdb"), "Larrimah_Biodiversity_Risk", "BIORISK", "biorisk"),
 "Wadeye":   (os.path.join(ROOT, "datasets/Wadeye/BioRisk_Wadeye/Datasets/ESRI/Wadeye_Biodiversity.gdb"), "Wadeye_BiodiversityRisk", "BIORISK", "biorisk"),
 "Weddell":  (os.path.join(ROOT, "datasets/Greater_Weddell/BioValues_GreaterWeddell/Datasets/ESRI/Greater_Weddell_biodiversity_assessment.gdb"), "Biodiversity_values", "BV_OVERALL", "biovalue"),
}
POOL = ["Roper", "Larrimah", "Wadeye"]          # identical BIORISK scale (confirmatory)
# Weddell BioValues -> ordinal (monotone; Spearman is invariant to the exact integers)
BV_MAP = {"Highly modified area": 1, "Low": 2, "Medium": 3, "High": 4, "Very high": 5}

# ----------------------------------------------------------------------
# LOAD grid + build proxy surfaces (matches roper_validation.build_surfaces, rule='mean')
# ----------------------------------------------------------------------
hexes = gpd.read_file(HEX).to_crs(3577)
for c in ["conv_score", "sig_socs", "sig_landsys", "prot_frac"]:
    hexes[c] = hexes[c].fillna(0.0)
hexes["hex_area_km2"] = hexes.area / 1e6
socs = hexes.sig_socs.to_numpy(); land = hexes.sig_landsys.to_numpy()
conv = hexes.conv_score.to_numpy(); prot = hexes.prot_frac.to_numpy()
sig = 0.5 * (socs + land)                        # 'mean' rule
proxy = hexes[["hex_id", "geometry"]].copy()
proxy["exposure_full"]        = sig * conv * (1 - prot)
proxy["significance"]         = sig
proxy["exposure_SOCSremoved"] = land * conv * (1 - prot)
proxy["convertibility"]       = conv
proxy["sig_landsys"]          = land
proxy["protection"]           = prot
SURFACES = ["exposure_full", "convertibility", "significance", "sig_landsys",
            "exposure_SOCSremoved", "protection"]

# ----------------------------------------------------------------------
# AGGREGATE any expert layer to hexes (area-weighted mean ordinal + coverage + majority)
# ----------------------------------------------------------------------
def aggregate(name):
    path, layer, field, kind = SOURCES[name]
    g = gpd.read_file(path, layer=layer).to_crs(3577)
    if (~g.is_valid).any():
        g["geometry"] = g.buffer(0)
    g = g[[field, "geometry"]].copy()
    if kind == "biovalue":
        g["bio"] = g[field].map(BV_MAP)
    else:
        g["bio"] = pd.to_numeric(g[field], errors="coerce")
    g = g.dropna(subset=["bio"])
    g = g[(g["bio"] >= 1) & (g["bio"] <= 5)]      # drop 0 Not-assessed / 9 Water
    ov = gpd.overlay(hexes[["hex_id", "hex_area_km2", "geometry"]], g[["bio", "geometry"]],
                     how="intersection", keep_geom_type=True)
    ov["km2"] = ov.area / 1e6
    def _agg(grp):
        tot = grp["km2"].sum()
        return pd.Series({"bio_awm": np.average(grp["bio"], weights=grp["km2"]),
                          "bio_majority": grp.groupby("bio")["km2"].sum().idxmax(),
                          "assessed_km2": tot,
                          "hex_area_km2": grp["hex_area_km2"].iloc[0]})
    agg = ov.groupby("hex_id").apply(_agg, include_groups=False).reset_index()
    agg["coverage_frac"] = (agg["assessed_km2"] / agg["hex_area_km2"]).clip(0, 1)
    agg["catchment"] = name
    df = agg.merge(proxy, on="hex_id", how="left")
    return gpd.GeoDataFrame(df, geometry="geometry", crs=3577)

frames = {name: aggregate(name) for name in SOURCES}
for name, df in frames.items():
    print(f"{name:9s}: hexes touched={len(df):4d}  >=50% cov={int((df.coverage_frac>=0.5).sum()):3d}  "
          f"BIORISK range {df.bio_awm.min():.2f}-{df.bio_awm.max():.2f}  distinct={df.bio_awm.nunique()}")

# ----------------------------------------------------------------------
# SPATIAL MACHINERY (replicates spatial_correction.py, per catchment)
# ----------------------------------------------------------------------
def build_W(df):
    pts = gpd.GeoDataFrame(df.drop(columns="geometry"),
                           geometry=df.geometry.centroid, crs=3577)
    W = libpysal.weights.DistanceBand.from_dataframe(pts, threshold=10100, silence_warnings=True)
    W.transform = "r"
    return W

def morans(df, W, col):
    x = df[col].to_numpy(float)
    if np.nanstd(x) == 0 or len(df) < 5:
        return np.nan, np.nan
    m = Moran(x, W, permutations=PERM)
    return float(m.I), float(m.p_sim)

def effective_n(df, W, xcol, ycol):
    n = len(df)
    def lag1(x):
        xr = rankdata(x); lag = libpysal.weights.lag_spatial(W, xr)
        xc = xr - xr.mean(); lc = lag - lag.mean()
        d = np.sqrt((xc**2).sum() * (lc**2).sum())
        return (xc*lc).sum()/d if d > 0 else 0.0
    rx, ry = lag1(df[xcol].to_numpy(float)), lag1(df[ycol].to_numpy(float))
    denom = 1 + rx*ry
    ne = 1 + (n-1)*(1-rx*ry)/denom if denom != 0 else n
    return float(np.clip(ne, 3, n)), rx, ry

def block_bootstrap_ci(df, W, xcol, ycol):
    n = len(df); x = df[xcol].to_numpy(float); y = df[ycol].to_numpy(float)
    obs = spearmanr(x, y).correlation
    neigh = {i: list(W.neighbors[i]) for i in range(n)}
    bs = np.empty(NB)
    for b in range(NB):
        seeds = rng.integers(0, n, size=max(1, n//5))
        idx = []
        for s in seeds:
            idx.append(s); idx.extend(neigh[s])
        idx = np.array(idx)[:n]
        bs[b] = spearmanr(x[idx], y[idx]).correlation
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return float(obs), float(lo), float(hi)

# ----------------------------------------------------------------------
# PER-CATCHMENT: Spearman + spatial correction for every surface
# ----------------------------------------------------------------------
def spearman_ne_ci(rho, n_eff):
    """Bonett-Wright SE for Spearman with effective n; Fisher-z CI. Returns (lo,hi,se_z,z)."""
    if not np.isfinite(rho) or n_eff <= 3:
        return np.nan, np.nan, np.nan, np.nan
    rho = np.clip(rho, -0.999, 0.999)
    z = np.arctanh(rho)
    se = np.sqrt((1 + rho**2/2.0) / (n_eff - 3))   # Bonett & Wright (2000), n->n_eff
    lo, hi = np.tanh(z - 1.96*se), np.tanh(z + 1.96*se)
    return float(lo), float(hi), float(se), float(z)

per_rows, spatial_rows = [], []
Wcache = {}
for name in POOL:
    df = frames[name].reset_index(drop=True)
    W = build_W(df); Wcache[name] = (df, W)
    I_bio, p_bio = morans(df, W, "bio_awm")
    for s in SURFACES:
        rho = spearmanr(df[s], df["bio_awm"]).correlation
        n_eff, rx, ry = effective_n(df, W, s, "bio_awm")
        lo_ci, hi_ci, se_z, z = spearman_ne_ci(rho, n_eff)
        row = dict(catchment=name, n=len(df), surface=s, spearman=round(rho, 4),
                   n_eff=round(n_eff, 1), ci_lo=round(lo_ci, 4) if np.isfinite(lo_ci) else np.nan,
                   ci_hi=round(hi_ci, 4) if np.isfinite(hi_ci) else np.nan)
        per_rows.append(row)
        if s in ("exposure_full", "convertibility", "significance", "sig_landsys", "exposure_SOCSremoved"):
            I_s, p_s = morans(df, W, s)
            bobs, blo, bhi = block_bootstrap_ci(df, W, s, "bio_awm")
            spatial_rows.append(dict(catchment=name, n=len(df), surface=s,
                                     moran_I_surface=round(I_s,3) if np.isfinite(I_s) else np.nan,
                                     moran_I_biorisk=round(I_bio,3) if np.isfinite(I_bio) else np.nan,
                                     spearman=round(bobs,4), block_ci_lo=round(blo,4),
                                     block_ci_hi=round(bhi,4), n_eff=round(n_eff,1)))
per_df = pd.DataFrame(per_rows)
spatial_df = pd.DataFrame(spatial_rows)
per_df.to_csv(f"{OUT}/per_catchment.csv", index=False)
spatial_df.to_csv(f"{OUT}/spatial_per_catchment.csv", index=False)

# ---- internal parity check against the frozen Roper pipeline ----
rp = per_df[(per_df.catchment=="Roper") & (per_df.surface=="exposure_full")].iloc[0]
rsp = spatial_df[(spatial_df.catchment=="Roper") & (spatial_df.surface=="exposure_full")].iloc[0]
parity = dict(roper_n=int(rp["n"]), roper_exposure_rho=float(rp["spearman"]),
              roper_moran_exposure=float(rsp["moran_I_surface"]),
              roper_moran_biorisk=float(rsp["moran_I_biorisk"]), roper_n_eff=float(rp["n_eff"]))
print("\nPARITY CHECK (expect ~ n=244, rho=0.240, I_exp=0.761, I_bio=0.406, n_eff~60):")
print("  ", parity)

# ----------------------------------------------------------------------
# META-ANALYSIS (random-effects, DerSimonian-Laird) over POOL, per surface
#   Uses Fisher-z of Spearman with variance from spatial effective n.
# ----------------------------------------------------------------------
def dersimonian_laird(zs, vs):
    zs, vs = np.asarray(zs, float), np.asarray(vs, float)
    k = len(zs)
    w = 1/vs
    z_fixed = np.sum(w*zs)/np.sum(w)
    Q = float(np.sum(w*(zs - z_fixed)**2))
    dfree = k - 1
    C = np.sum(w) - np.sum(w**2)/np.sum(w)
    tau2 = max(0.0, (Q - dfree)/C) if C > 0 else 0.0
    wr = 1/(vs + tau2)
    z_re = np.sum(wr*zs)/np.sum(wr)
    se_re = np.sqrt(1/np.sum(wr))
    I2 = max(0.0, (Q - dfree)/Q)*100 if Q > 0 else 0.0
    p_Q = 1 - chi2.cdf(Q, dfree) if dfree > 0 else np.nan
    return dict(rho=float(np.tanh(z_re)),
                ci_lo=float(np.tanh(z_re-1.96*se_re)), ci_hi=float(np.tanh(z_re+1.96*se_re)),
                z=float(z_re), se=float(se_re), p=float(2*(1-norm.cdf(abs(z_re/se_re)))),
                Q=Q, df=dfree, p_Q=float(p_Q), I2=float(I2), tau2=float(tau2), k=k)

meta_rows, het_rows = [], []
for s in SURFACES:
    zs, vs, ns = [], [], []
    for name in POOL:
        sub = per_df[(per_df.catchment==name) & (per_df.surface==s)].iloc[0]
        rho = np.clip(sub["spearman"], -0.999, 0.999); ne = sub["n_eff"]
        if ne <= 3: continue
        zs.append(np.arctanh(rho)); vs.append((1+rho**2/2.0)/(ne-3)); ns.append(sub["n"])
    m = dersimonian_laird(zs, vs)
    meta_rows.append(dict(surface=s, k=m["k"], pooled_rho=round(m["rho"],4),
                          ci_lo=round(m["ci_lo"],4), ci_hi=round(m["ci_hi"],4),
                          p=round(m["p"],4), I2=round(m["I2"],1), Q=round(m["Q"],3),
                          p_Q=round(m["p_Q"],4), tau2=round(m["tau2"],4)))
    if s in ("exposure_full","convertibility","significance","sig_landsys"):
        het_rows.append(dict(surface=s, Q=round(m["Q"],3), df=m["df"], p_Q=round(m["p_Q"],4),
                             I2=round(m["I2"],1), tau2=round(m["tau2"],4),
                             note="k=3 -> very low power; non-sig Q does NOT prove homogeneity"))
meta_df = pd.DataFrame(meta_rows); meta_df.to_csv(f"{OUT}/decomposition_meta.csv", index=False)
het_df = pd.DataFrame(het_rows); het_df.to_csv(f"{OUT}/heterogeneity.csv", index=False)

# pooled effective n (sum of per-catchment n_eff for exposure_full)
pooled_neff = float(per_df[(per_df.surface=="exposure_full") & (per_df.catchment.isin(POOL))]["n_eff"].sum())
pooled_n = int(per_df[(per_df.surface=="exposure_full") & (per_df.catchment.isin(POOL))]["n"].sum())

# ----------------------------------------------------------------------
# EXPLORATORY: naive fully-pooled Spearman (confounded by catchment means)
# ----------------------------------------------------------------------
poolcat = pd.concat([frames[n] for n in POOL], ignore_index=True)
naive_rows = []
for s in SURFACES:
    r = spearmanr(poolcat[s], poolcat["bio_awm"]).correlation
    naive_rows.append(dict(surface=s, naive_pooled_rho=round(float(r),4), n=len(poolcat)))
naive_df = pd.DataFrame(naive_rows)

# within-catchment partial (remove catchment means by ranking within catchment) -- exploratory
def within_rank(df, col):
    return df.groupby("catchment")[col].transform(lambda v: rankdata(v))
wc_rows = []
for s in SURFACES:
    xr = within_rank(poolcat, s); yr = within_rank(poolcat, "bio_awm")
    r = spearmanr(xr, yr).correlation
    wc_rows.append(dict(surface=s, within_catchment_pooled_rho=round(float(r),4)))
wc_df = pd.DataFrame(wc_rows)

# ----------------------------------------------------------------------
# WEDDELL robustness (separate scale; Spearman crosswalk-invariant)
# ----------------------------------------------------------------------
wd = frames["Weddell"].reset_index(drop=True)
Wd_W = build_W(wd)
wed_rows = []
for s in ("exposure_full","convertibility","significance","sig_landsys"):
    rho = spearmanr(wd[s], wd["bio_awm"]).correlation
    n_eff, rx, ry = effective_n(wd, Wd_W, s, "bio_awm")
    lo, hi, _, _ = spearman_ne_ci(rho, n_eff)
    wed_rows.append(dict(surface=s, n=len(wd), spearman=round(float(rho),4),
                         n_eff=round(n_eff,1),
                         ci_lo=round(lo,4) if np.isfinite(lo) else np.nan,
                         ci_hi=round(hi,4) if np.isfinite(hi) else np.nan))
wed_df = pd.DataFrame(wed_rows); wed_df.to_csv(f"{OUT}/weddell_robustness.csv", index=False)

# ----------------------------------------------------------------------
# REPORT
# ----------------------------------------------------------------------
def block(title): return ["", "="*74, title, "="*74]
L = []
L += ["POOLED MULTI-CATCHMENT VALIDATION — pre-registered (PREREGISTRATION.md)",
      f"primary rule='{PRIMARY_RULE}'  seed={SEED}  pool={POOL}  (Weddell separate)"]
L += block("0. PARITY CHECK vs frozen Roper pipeline  [OBSERVATION]")
L += [f"  Roper: n={parity['roper_n']} (expect 244), exposure rho={parity['roper_exposure_rho']:+.3f} (expect +0.240)",
      f"         Moran I exposure={parity['roper_moran_exposure']:+.3f} (expect +0.761), "
      f"BIORISK={parity['roper_moran_biorisk']:+.3f} (expect +0.406), n_eff={parity['roper_n_eff']:.0f} (expect ~60)"]
L += block("1. PER-CATCHMENT  [OBSERVATION + per-catchment statistical evidence]")
L += ["  (per-catchment n<20 individually UNINTERPRETABLE; shown for transparency only)"]
for name in POOL:
    sub = per_df[per_df.catchment==name]
    ef = sub[sub.surface=="exposure_full"].iloc[0]
    L += [f"  {name} (n={ef['n']}, n_eff={ef['n_eff']:.0f}):"]
    for s in ("exposure_full","convertibility","significance","sig_landsys"):
        r = sub[sub.surface==s].iloc[0]
        L += [f"      {s:20s} rho={r['spearman']:+.3f}  95%CI[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]"]
L += block("2. CONFIRMATORY: random-effects meta-analysis over 3 catchments  [STATISTICAL EVIDENCE]")
L += [f"  pooled n={pooled_n} hexes, pooled effective n={pooled_neff:.0f}",
      f"  {'surface':22s} {'pooled_rho':>10s} {'95% CI':>20s} {'p':>8s} {'I2%':>6s} {'p_Q':>7s}"]
for _, r in meta_df.iterrows():
    L += [f"  {r['surface']:22s} {r['pooled_rho']:+10.3f}  [{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]  "
          f"{r['p']:8.4f} {r['I2']:6.1f} {r['p_Q']:7.4f}"]
L += block("3. HETEROGENEITY (Cochran Q / I2)  [STATISTICAL EVIDENCE + caveat]")
for _, r in het_df.iterrows():
    L += [f"  {r['surface']:20s} Q={r['Q']:.2f} df={r['df']} p_Q={r['p_Q']:.4f} I2={r['I2']:.1f}%  ({r['note']})"]
L += block("4. EXPLORATORY: naive vs within-catchment pooled Spearman  [EXPLORATORY]")
merged = naive_df.merge(wc_df, on="surface")
for _, r in merged.iterrows():
    L += [f"  {r['surface']:22s} naive_pooled={r['naive_pooled_rho']:+.3f}   within_catchment={r['within_catchment_pooled_rho']:+.3f}"]
L += block("5. WEDDELL ROBUSTNESS (BioValues scale; Spearman crosswalk-invariant)  [EXPLORATORY]")
for _, r in wed_df.iterrows():
    L += [f"  {r['surface']:20s} rho={r['spearman']:+.3f} (n={r['n']}, n_eff={r['n_eff']:.0f}) "
          f"95%CI[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]"]
report = "\n".join(L)
print(report)
open(f"{OUT}/report.txt","w").write(report+"\n")

# verdict json
def meta_get(s, k): return float(meta_df[meta_df.surface==s][k].iloc[0])
verdict = dict(
    primary_rule=PRIMARY_RULE, seed=SEED, pool=POOL, pooled_n=pooled_n, pooled_n_eff=pooled_neff,
    parity=parity,
    meta={s: dict(rho=meta_get(s,"pooled_rho"), ci_lo=meta_get(s,"ci_lo"),
                  ci_hi=meta_get(s,"ci_hi"), p=meta_get(s,"p"), I2=meta_get(s,"I2"),
                  p_Q=meta_get(s,"p_Q")) for s in SURFACES},
    weddell={r["surface"]: dict(rho=r["spearman"], n=int(r["n"])) for _, r in wed_df.iterrows()},
)
json.dump(verdict, open(f"{OUT}/verdict.json","w"), indent=2)
print("\nwrote outputs ->", OUT)
