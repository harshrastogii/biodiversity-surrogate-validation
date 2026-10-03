#!/usr/bin/env python
"""
export_centroids.py — write polygon centroids (EPSG:3577) for every benchmark polygon, aligned
to the unit_id used in harmonized_polygon.parquet, to data/processed/polygon_centroids.parquet.

Why: the spatial analyses (block bootstrap, block CV, revision analyses) need polygon locations.
Previously these were re-derived from the raw benchmark geodatabases on every run, so the
committed processed data alone could not reproduce the confirmatory results. Committing this
small file (~50k rows x 4 columns) makes every spatial analysis re-runnable from the repository.

Needs the raw benchmarks (data/raw, ../datasets, ../nt_exposure) — run once, locally.
"""
import os, sys, warnings
import pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
from centroids import centroids_from_raw, CENTROIDS_PATH

poly = pd.read_parquet(os.path.join(C.PROC, "harmonized_polygon.parquet"))
out = []
for name in C.BENCHMARKS:
    c = centroids_from_raw(name)
    n_poly = int((poly.catchment == name).sum())
    if len(c) != n_poly:  # alignment guard: unit_id p{i} must index the same polygons
        raise SystemExit(f"{name}: {len(c)} centroids vs {n_poly} harmonised polygons — misaligned")
    c.insert(0, "catchment", name)
    out.append(c)
    print(f"{name:10s} {len(c):6d} centroids")
pd.concat(out, ignore_index=True).to_parquet(CENTROIDS_PATH, index=False)
print("wrote", CENTROIDS_PATH)
