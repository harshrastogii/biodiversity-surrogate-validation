"""
centroids.py — polygon centroids aligned to harmonized_polygon.parquet unit_id ('p{i}').
Reads the committed data/processed/polygon_centroids.parquet when present (see
export_centroids.py); otherwise re-derives them from the raw benchmark geodatabases exactly as
harmonize.load_benchmark does.
"""
import os
import pandas as pd
import config as C

CENTROIDS_PATH = os.path.join(C.PROC, "polygon_centroids.parquet")

def centroids_from_raw(name):
    import geopandas as gpd
    from shapely import make_valid
    b = C.BENCHMARKS[name]
    g = gpd.read_file(b["path"], layer=b["layer"]).to_crs(C.CRS)
    g["geometry"] = make_valid(g.geometry)
    g = g[g.geometry.notna() & ~g.geometry.is_empty]
    g["bio"] = (g[b["field"]].map(C.BV_MAP) if b["scheme"] == "biovalue"
                else pd.to_numeric(g[b["field"]], errors="coerce"))
    g = g.dropna(subset=["bio"]); g = g[(g["bio"] >= 1) & (g["bio"] <= 5)].reset_index(drop=True)
    c = g.geometry.centroid
    return pd.DataFrame({"unit_id": [f"p{i}" for i in range(len(g))], "cx": c.x.values, "cy": c.y.values})

def centroids(name):
    if os.path.exists(CENTROIDS_PATH):
        c = pd.read_parquet(CENTROIDS_PATH)
        return c[c.catchment == name][["unit_id", "cx", "cy"]].reset_index(drop=True)
    return centroids_from_raw(name)
