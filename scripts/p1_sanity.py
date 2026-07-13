#!/usr/bin/env python
"""
p1_sanity.py — EXPLORATORY milestone diagnostic (NOT confirmatory).
Reads the harmonized products and asks: does the polygon/fine-resolution reframe reveal
surrogate-vs-expert signal that the 10 km hex analysis hid? Reports Spearman across the
resolution ladder + native-polygon anchor.

CRITICAL CAVEAT (enforced in output): grid cells finer than the expert polygons are
PSEUDOREPLICATES of the same expert judgment. Cell-count is NOT an independent sample size.
No grid p-values are reported. The honest information ceiling = number of native expert
polygons and BIORISK classes, printed alongside.
"""
import os, sys, warnings
import numpy as np, pandas as pd
from scipy.stats import spearmanr
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

grid = pd.read_parquet(os.path.join(C.PROC, "harmonized_grid.parquet"))
poly = pd.read_parquet(os.path.join(C.PROC, "harmonized_polygon.parquet"))
SURR = ["sig_landsys", "convertibility", "protection"]

def rho(df, s):
    d = df[[s, "biorisk_awm"]].dropna()
    if len(d) < 5 or d[s].nunique() < 2 or d["biorisk_awm"].nunique() < 2:
        return np.nan, len(d)
    return spearmanr(d[s], d["biorisk_awm"]).correlation, len(d)

print("="*90)
print("EXPLORATORY P1 SANITY — Spearman(surrogate, area-weighted BIORISK). NOT confirmatory.")
print("Grid cells < expert-polygon size are pseudoreplicates; n_cells is NOT independent n.")
print("="*90)
for name in C.BENCHMARKS:
    npoly = int((poly.catchment == name).sum())
    nclass = int(poly.loc[poly.catchment == name, "biorisk_majority"].round().nunique())
    print(f"\n{name}  | native expert polygons={npoly}  | BIORISK classes present={nclass}  "
          f"<-- honest information ceiling")
    # polygon anchor
    pc = poly[poly.catchment == name]
    row = "  polygon : " + "  ".join(f"{s}={rho(pc,s)[0]:+.3f}" for s in SURR)
    print(row)
    # grid ladder (coverage>=0.5 to limit support mismatch)
    for res in C.RESOLUTIONS_M:
        gc = grid[(grid.catchment == name) & (grid.resolution == res) & (grid.coverage_frac >= 0.5)]
        parts = []
        for s in SURR:
            r, n = rho(gc, s)
            parts.append(f"{s}={r:+.3f}")
        print(f"  {res//1000:2d}km(cov>=.5, n_cells={len(gc):5d}) : " + "  ".join(parts))

print("\n" + "="*90)
print("READ: compare 'polygon' and fine-grid rows to the 10 km row. Where they diverge, the")
print("10 km hex (V1) was destroying signal by over-aggregation. Where the incumbent sig_landsys")
print("stays flat across grains, it is intrinsically coarse (550 land systems NT-wide) and cannot")
print("resolve fine expert detail -> motivates NVIS/SDM/DEA candidates. EXPLORATORY only.")
