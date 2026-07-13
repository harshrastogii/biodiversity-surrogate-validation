#!/usr/bin/env python
"""
fetch_dea.py — acquire DEA Fractional Cover (condition/intactness surrogate).
For each catchment: pull ga_ls_fc_pc_cyear_3 bs_pc_50 (median bare-soil %) COGs from the
open DEA S3 bucket (via public HTTPS, no auth) for a reference year, mosaic clipped to the
catchment, and save veg_cover = 100 - bare_soil  (higher = more vegetated/intact),
EPSG:3577, 30 m.  Documented limitation: single reference year (rainfall-sensitive);
multi-year median is a later refinement.
"""
import os, sys, warnings
import numpy as np, geopandas as gpd, rasterio
from rasterio.merge import merge
from pystac_client import Client
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

YEAR = "2020"
DEA_DIR = os.path.join(C.RAW, "surrogates", "DEA"); os.makedirs(DEA_DIR, exist_ok=True)
S3 = "s3://dea-public-data/"; HTTPS = "https://data.dea.ga.gov.au/"
cat = Client.open("https://explorer.dea.ga.gov.au/stac")

def fetch(name):
    b = C.BENCHMARKS[name]
    g = gpd.read_file(b["path"], layer=b["layer"])
    bb4326 = list(g.to_crs(4326).total_bounds)
    minx, miny, maxx, maxy = g.to_crs(3577).total_bounds
    pad = 2000
    items = list(cat.search(collections=["ga_ls_fc_pc_cyear_3"], bbox=bb4326, datetime=YEAR).items())
    urls = [it.assets["bs_pc_50"].href.replace(S3, HTTPS) for it in items]
    if not urls:
        print(f"{name}: NO DEA tiles"); return None
    srcs = [rasterio.open(u) for u in urls]
    mosaic, tr = merge(srcs, bounds=(minx-pad, miny-pad, maxx+pad, maxy+pad), nodata=255)
    for s in srcs: s.close()
    bs = mosaic[0].astype(np.float32)
    veg = np.where(bs == 255, np.nan, 100.0 - bs)      # veg cover %
    out = os.path.join(DEA_DIR, f"dea_vegcover_{name}.tif")
    prof = dict(driver="GTiff", height=veg.shape[0], width=veg.shape[1], count=1,
                dtype="float32", crs="EPSG:3577", transform=tr, nodata=np.nan,
                compress="lzw", tiled=True)
    with rasterio.open(out, "w", **prof) as d:
        d.write(veg, 1)
    vv = veg[np.isfinite(veg)]
    print(f"{name}: {len(urls)} tiles -> {out}  vegcover mean={vv.mean():.1f}% range[{vv.min():.0f},{vv.max():.0f}]")
    return out

if __name__ == "__main__":
    for name in C.BENCHMARKS:
        fetch(name)
    print("DEA fetch done ->", DEA_DIR)
