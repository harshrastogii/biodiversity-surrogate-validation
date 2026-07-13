#!/usr/bin/env python
"""
self_review.py — adversarial checks on pooled_validation.py. Each check targets a
specific threat to validity and reports evidence, not assertions.
"""
import numpy as np, pandas as pd, geopandas as gpd, warnings
from scipy.stats import spearmanr, rankdata, norm, chi2
import libpysal
from esda.moran import Moran
warnings.filterwarnings("ignore")
import os
HERE=os.path.dirname(os.path.abspath(__file__)); REPO=os.path.abspath(os.path.join(HERE,"..",".."))
ROOT=os.path.abspath(os.path.join(REPO,".."))
HEX=os.path.join(REPO,"data","hex_master.gpkg")
SRC={
 "Roper":(os.path.join(REPO,"data","roper_intersection.gpkg"),"roper_intersection","BIORISK","biorisk"),
 "Larrimah":(os.path.join(ROOT,"datasets/Larrimah/BioRisk_Larrimah/Datasets/ESRI/Larrimah_BioRisk.gdb"),"Larrimah_Biodiversity_Risk","BIORISK","biorisk"),
 "Wadeye":(os.path.join(ROOT,"datasets/Wadeye/BioRisk_Wadeye/Datasets/ESRI/Wadeye_Biodiversity.gdb"),"Wadeye_BiodiversityRisk","BIORISK","biorisk"),
 "Weddell":(os.path.join(ROOT,"datasets/Greater_Weddell/BioValues_GreaterWeddell/Datasets/ESRI/Greater_Weddell_biodiversity_assessment.gdb"),"Biodiversity_values","BV_OVERALL","biovalue"),
}
BV_MAP={"Highly modified area":1,"Low":2,"Medium":3,"High":4,"Very high":5}
BV_MAP_UNEQUAL={"Highly modified area":1,"Low":2,"Medium":3,"High":6,"Very high":10}  # alt spacing
POOL=["Roper","Larrimah","Wadeye"]

hexes=gpd.read_file(HEX).to_crs(3577)
for c in ["conv_score","sig_socs","sig_landsys","prot_frac"]: hexes[c]=hexes[c].fillna(0.0)
hexes["hex_area_km2"]=hexes.area/1e6
socs=hexes.sig_socs.to_numpy(); land=hexes.sig_landsys.to_numpy()
conv=hexes.conv_score.to_numpy(); prot=hexes.prot_frac.to_numpy()
def surfaces(rule):
    if rule=="mean": sig=0.5*(socs+land)
    elif rule=="max": sig=np.maximum(socs,land)
    p=hexes[["hex_id","geometry"]].copy()
    p["exposure_full"]=sig*conv*(1-prot); p["significance"]=sig
    p["convertibility"]=conv; p["sig_landsys"]=land; p["protection"]=prot
    return p

def aggregate(name, bmap=BV_MAP):
    path,layer,field,kind=SRC[name]
    g=gpd.read_file(path,layer=layer).to_crs(3577)
    if (~g.is_valid).any(): g["geometry"]=g.buffer(0)
    g=g[[field,"geometry"]].copy()
    g["bio"]=g[field].map(bmap) if kind=="biovalue" else pd.to_numeric(g[field],errors="coerce")
    g=g.dropna(subset=["bio"]); g=g[(g.bio>=1)&(g.bio<=max(bmap.values()) if kind=="biovalue" else 9)]
    ov=gpd.overlay(hexes[["hex_id","hex_area_km2","geometry"]],g[["bio","geometry"]],how="intersection",keep_geom_type=True)
    ov["km2"]=ov.area/1e6
    def _a(grp):
        return pd.Series({"bio_awm":np.average(grp.bio,weights=grp.km2),
                          "bio_majority":grp.groupby("bio").km2.sum().idxmax(),
                          "assessed_km2":grp.km2.sum(),"hex_area_km2":grp.hex_area_km2.iloc[0]})
    agg=ov.groupby("hex_id").apply(_a,include_groups=False).reset_index()
    agg["coverage_frac"]=(agg.assessed_km2/agg.hex_area_km2).clip(0,1); agg["catchment"]=name
    return gpd.GeoDataFrame(agg,geometry=hexes.set_index("hex_id").loc[agg.hex_id,"geometry"].values,crs=3577)

def build_W(df):
    pts=gpd.GeoDataFrame(df.drop(columns="geometry"),geometry=df.geometry.centroid,crs=3577)
    W=libpysal.weights.DistanceBand.from_dataframe(pts,threshold=10100,silence_warnings=True); W.transform="r"; return W

print("="*74); print("CHECK 1 — spatial graph validity for small catchments (isolates, Moran defined?)"); print("="*74)
for name in ["Roper","Larrimah","Wadeye","Weddell"]:
    df=aggregate(name).reset_index(drop=True); W=build_W(df)
    card=list(W.cardinalities.values()); iso=sum(1 for c in card if c==0)
    print(f"  {name:9s} n={len(df):3d}  mean_neighbours={np.mean(card):.2f}  isolates={iso}  "
          f"span_km≈{(df.geometry.centroid.x.max()-df.geometry.centroid.x.min())/1000:.0f}x{(df.geometry.centroid.y.max()-df.geometry.centroid.y.min())/1000:.0f}")

print(); print("="*74); print("CHECK 2 — spatial support mismatch (coverage of the hexes we compare)"); print("="*74)
for name in POOL+["Weddell"]:
    df=aggregate(name)
    q=df.coverage_frac.quantile([0,.25,.5,.75,1.0]).round(2).tolist()
    print(f"  {name:9s} coverage min/Q1/med/Q3/max = {q}   frac<0.25: {(df.coverage_frac<0.25).mean():.0%}")

print(); print("="*74); print("CHECK 3 — benchmark encoding sensitivity: area-weighted-mean vs MAJORITY class"); print("="*74)
p=surfaces("mean")
for enc in ["bio_awm","bio_majority"]:
    rr=[]
    for name in POOL:
        d=aggregate(name).merge(p.drop(columns="geometry"),on="hex_id")
        rr.append((name,spearmanr(d["exposure_full"],d[enc]).correlation,
                        spearmanr(d["convertibility"],d[enc]).correlation,
                        spearmanr(d["significance"],d[enc]).correlation))
    print(f"  [{enc}]  " + "  ".join(f"{n}: exp={a:+.2f} conv={b:+.2f} sig={c:+.2f}" for n,a,b,c in rr))

print(); print("="*74); print("CHECK 4 — Weddell crosswalk spacing sensitivity (equal vs unequal intervals)"); print("="*74)
p=surfaces("mean")
for tag,bmap in [("equal 1-5",BV_MAP),("unequal 1,2,3,6,10",BV_MAP_UNEQUAL)]:
    d=aggregate("Weddell",bmap).merge(p.drop(columns="geometry"),on="hex_id")
    print(f"  [{tag}] exp={spearmanr(d.exposure_full,d.bio_awm).correlation:+.3f} "
          f"conv={spearmanr(d.convertibility,d.bio_awm).correlation:+.3f} "
          f"sig={spearmanr(d.significance,d.bio_awm).correlation:+.3f} "
          f"landsys={spearmanr(d.sig_landsys,d.bio_awm).correlation:+.3f}")

print(); print("="*74); print("CHECK 5 — does the primary composite result depend on the significance rule?"); print("="*74)
for rule in ["mean","max"]:
    p=surfaces(rule); rr=[]
    for name in POOL:
        d=aggregate(name).merge(p.drop(columns="geometry"),on="hex_id")
        rr.append(spearmanr(d.exposure_full,d.bio_awm).correlation)
    print(f"  rule={rule:5s}  per-catchment exposure rho: " + "  ".join(f"{n}={r:+.2f}" for n,r in zip(POOL,rr)))

print(); print("="*74); print("CHECK 6 — coverage-restricted (>=50%) per-catchment n and rho (support-matched)"); print("="*74)
p=surfaces("mean")
for name in POOL:
    d=aggregate(name).merge(p.drop(columns="geometry"),on="hex_id")
    d50=d[d.coverage_frac>=0.5]
    r_all=spearmanr(d.exposure_full,d.bio_awm).correlation
    r_50=spearmanr(d50.exposure_full,d50.bio_awm).correlation if len(d50)>=4 else float('nan')
    print(f"  {name:9s} all n={len(d):3d} rho={r_all:+.3f}   >=50% n={len(d50):3d} rho={r_50:+.3f}")

print(); print("="*74); print("CHECK 7 — hidden circularity: BIORISK class-1 (land-use-defined) presence in new catchments"); print("="*74)
for name in POOL:
    path,layer,field,kind=SRC[name]
    g=gpd.read_file(path,layer=layer).to_crs(3577); g["bio"]=pd.to_numeric(g[field],errors="coerce")
    g["km2"]=g.area/1e6
    share1=g.loc[g.bio==1,"km2"].sum()/g["km2"].sum()*100
    print(f"  {name:9s} class-1 share of assessed area = {share1:.1f}%  (Roper ref: 0.5%)")
