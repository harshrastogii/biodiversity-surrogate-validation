#!/usr/bin/env python
"""
harmonize.py — build the V2 analysis dataset. PURE DATA BUILD (no statistics).

For every benchmark catchment and every grain in a resolution ladder (plus a native
expert-polygon anchor), produce a tidy table of analysis units carrying:
  unit_id, catchment, resolution, unit_km2, assessed_km2, coverage_frac,
  biorisk_awm, biorisk_majority, sig_landsys, convertibility, protection, iucn_frac

Surrogates are a REGISTRY (name -> extractor). Adding NVIS/SDM/DEA later = append one
registry entry; nothing else changes. Incumbent surrogate definitions reproduce V1
exactly (see RESEARCH_LOG D1.3).

Outputs (v2/data/processed/):
  harmonized_grid.parquet     — all catchments x grid resolutions
  harmonized_polygon.parquet  — native expert-polygon anchor
  build_report.txt            — provenance + unit counts (NO correlations)
"""
import os, sys, time, warnings
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import box, shape
from shapely import make_valid
import rasterio
from rasterio import features as rfeatures
from rasterio.windows import from_bounds
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

os.makedirs(C.PROC, exist_ok=True)
t0 = time.time()

# ---------------------------------------------------------------------------
# LOAD surrogate sources once (reproject, repair)
# ---------------------------------------------------------------------------
def load(path, layer, cols, repair=True):
    g = gpd.read_file(path, layer=layer) if layer else gpd.read_file(path)
    g = g.to_crs(C.CRS)
    if repair:
        g["geometry"] = make_valid(g.geometry)
    g = g[g.geometry.notna() & ~g.geometry.is_empty]
    return g[cols + ["geometry"]].copy()

print("loading surrogate sources ...", flush=True)
# ntls/capad are small enough to repair up front; LUMP (103k polys) is repaired lazily
# per-catchment after bbox clipping (repairing the whole national layer is the bottleneck).
ntls = load(C.NTLS["path"], C.NTLS["layer"], ["LANDSYSTEM"])
ntls = ntls[ntls["LANDSYSTEM"].notna()].copy()
lump = load(C.LUMP["path"], C.LUMP["layer"], ["PRIM_NO"], repair=False)
capad = load(C.CAPAD["path"], None, ["IUCN"])
capad["iucn_strict"] = capad["IUCN"].astype(str).str.upper().str.strip().isin(C.IUCN_STRICT)

# NT-wide land-system rarity (computed once on the full layer -> preserves V1 definition)
ntls["a"] = ntls.geometry.area / 1e6
A = ntls.groupby("LANDSYSTEM")["a"].sum()
la = np.log(A); rar = 1 - (la - la.min()) / (la.max() - la.min())
RARITY = rar.to_dict()
lump["conv"] = lump["PRIM_NO"].map(C.CONV_SCORE)          # NaN for water(6)/other
print(f"  land systems={len(A)}  rarity[{rar.min():.3f},{rar.max():.3f}] | lump polys={len(lump)} | capad polys={len(capad)}")

# NVIS MVG rarity (NT-wide, native-veg only) — direct analogue of land-system rarity
with rasterio.open(C.NVIS_MVG_TIF) as _r:
    _mvg = _r.read(1); _mvg_transform = _r.transform; _mvg_nodata = _r.nodata
_codes, _counts = np.unique(_mvg[_mvg > 0], return_counts=True)
_keep = np.array([c not in C.NVIS_EXCLUDE for c in _codes])
_vc = _codes[_keep]; _va = _counts[_keep] * 0.01                 # km2 per 100 m pixel
_lva = np.log(_va); _mvg_rar = 1 - (_lva - _lva.min()) / (_lva.max() - _lva.min())
NVIS_RARITY = dict(zip(_vc.tolist(), _mvg_rar.tolist()))          # MVG code -> rarity
print(f"  NVIS MVG native classes(NT)={len(_vc)}  rarity[{_mvg_rar.min():.3f},{_mvg_rar.max():.3f}]")

def nvis_polygons(bounds, pad=2000):
    """Polygonise the NVIS MVG raster within bounds -> vector rarity layer (EPSG:3577)."""
    minx, miny, maxx, maxy = bounds
    with rasterio.open(C.NVIS_MVG_TIF) as r:
        win = from_bounds(minx-pad, miny-pad, maxx+pad, maxy+pad, r.transform)
        arr = r.read(1, window=win); tr = r.window_transform(win)
    mask = np.isin(arr, list(NVIS_RARITY.keys()))                 # only native-veg codes
    geoms, codes = [], []
    for geom, val in rfeatures.shapes(arr.astype(np.int32), mask=mask, transform=tr):
        geoms.append(shape(geom)); codes.append(int(val))
    if not geoms:
        return gpd.GeoDataFrame({"nvis_rarity": []}, geometry=[], crs=C.CRS)
    g = gpd.GeoDataFrame({"nvis_rarity": [NVIS_RARITY[c] for c in codes]},
                         geometry=geoms, crs=C.CRS)
    return g

def clip_bbox(src, bounds, pad=20000, repair=False):
    minx, miny, maxx, maxy = bounds
    sub = src.cx[minx-pad:maxx+pad, miny-pad:maxy+pad].copy()
    if repair and len(sub):
        sub["geometry"] = make_valid(sub.geometry)
        sub = sub[sub.geometry.notna() & ~sub.geometry.is_empty]
    return sub

# ---------------------------------------------------------------------------
# SURROGATE REGISTRY — each extractor: (units gdf, clipped sources) -> Series by unit_id
#   area-weighted mean over the overlapping source area (no-data where absent)
# ---------------------------------------------------------------------------
def _awm(units, src, valcol, weight_denominator="valid"):
    """area-weighted mean of src[valcol] within each unit.
    weight_denominator='valid' -> denom = overlapped area with non-NaN val (matches V1
    convertibility/rarity); 'unit' -> denom = full unit area (matches V1 protection fraction)."""
    ov = gpd.overlay(units[["unit_id", "unit_km2", "geometry"]], src[[valcol, "geometry"]],
                     how="intersection", keep_geom_type=True)
    if len(ov) == 0:
        return pd.Series(dtype=float)
    ov["piece_km2"] = ov.geometry.area / 1e6
    if weight_denominator == "valid":
        ov = ov.dropna(subset=[valcol])
        ov["w"] = ov[valcol] * ov["piece_km2"]
        num = ov.groupby("unit_id")["w"].sum()
        den = ov.groupby("unit_id")["piece_km2"].sum()
        return num / den
    else:  # 'unit' -> fraction of unit area covered by (val==True)
        sel = ov[ov[valcol] == True] if ov[valcol].dtype == bool else ov.dropna(subset=[valcol])
        num = sel.groupby("unit_id")["piece_km2"].sum()
        unit_area = units.set_index("unit_id")["unit_km2"]
        return (num / unit_area).clip(0, 1)

def surr_sig_landsys(units, src):
    s = src["ntls"].copy(); s["rarity"] = s["LANDSYSTEM"].map(RARITY)
    return _awm(units, s, "rarity", "valid")

def surr_sig_nvis_mvg(units, src):
    if src["nvis"] is None or len(src["nvis"]) == 0:
        return pd.Series(dtype=float)
    return _awm(units, src["nvis"], "nvis_rarity", "valid")

def surr_cond_dea(units, src):
    """zonal-mean vegetation cover (DEA FC) per unit."""
    path = src.get("dea_path")
    if not path or not os.path.exists(path):
        return pd.Series(dtype=float)
    from rasterstats import zonal_stats
    zs = zonal_stats(units.geometry, path, stats=["mean"], nodata=float("nan"), all_touched=False)
    return pd.Series([z["mean"] for z in zs], index=units["unit_id"].values)

def surr_convertibility(units, src):
    return _awm(units, src["lump"], "conv", "valid")

def surr_protection(units, src):
    ov = gpd.overlay(units[["unit_id", "unit_km2", "geometry"]], src["capad"][["geometry"]],
                     how="intersection", keep_geom_type=True)
    if len(ov) == 0:
        return pd.Series(0.0, index=units["unit_id"])
    ov["piece_km2"] = ov.geometry.area / 1e6
    num = ov.groupby("unit_id")["piece_km2"].sum()
    frac = (num / units.set_index("unit_id")["unit_km2"]).clip(0, 1)
    return frac.reindex(units["unit_id"]).fillna(0.0)

def surr_iucn(units, src):
    cap = src["capad"]; strict = cap[cap["iucn_strict"]]
    if len(strict) == 0:
        return pd.Series(0.0, index=units["unit_id"])
    ov = gpd.overlay(units[["unit_id", "unit_km2", "geometry"]], strict[["geometry"]],
                     how="intersection", keep_geom_type=True)
    if len(ov) == 0:
        return pd.Series(0.0, index=units["unit_id"])
    ov["piece_km2"] = ov.geometry.area / 1e6
    num = ov.groupby("unit_id")["piece_km2"].sum()
    return (num / units.set_index("unit_id")["unit_km2"]).clip(0, 1).reindex(units["unit_id"]).fillna(0.0)

REGISTRY = {  # SDM gets appended here later — no other change needed
    "sig_landsys":    surr_sig_landsys,
    "sig_nvis_mvg":   surr_sig_nvis_mvg,   # NVIS v7 MVG rarity (added P2)
    "cond_dea":       surr_cond_dea,       # DEA fractional cover veg-cover (added P2)
    "convertibility": surr_convertibility,
    "protection":     surr_protection,
    "iucn_frac":      surr_iucn,
}

# ---------------------------------------------------------------------------
# BENCHMARK loader -> polygons with ordinal 'bio' in [1,5]
# ---------------------------------------------------------------------------
def load_benchmark(name):
    b = C.BENCHMARKS[name]
    g = gpd.read_file(b["path"], layer=b["layer"]).to_crs(C.CRS)
    g["geometry"] = make_valid(g.geometry)
    g = g[g.geometry.notna() & ~g.geometry.is_empty]
    if b["scheme"] == "biovalue":
        g["bio"] = g[b["field"]].map(C.BV_MAP)
    else:
        g["bio"] = pd.to_numeric(g[b["field"]], errors="coerce")
    g = g.dropna(subset=["bio"]); g = g[(g["bio"] >= 1) & (g["bio"] <= 5)]
    return g[["bio", "geometry"]].reset_index(drop=True)

def aggregate_bio(units, bench):
    ov = gpd.overlay(units[["unit_id", "unit_km2", "geometry"]], bench[["bio", "geometry"]],
                     how="intersection", keep_geom_type=True)
    ov["piece_km2"] = ov.geometry.area / 1e6
    def _a(grp):
        return pd.Series({"biorisk_awm": np.average(grp["bio"], weights=grp["piece_km2"]),
                          "biorisk_majority": grp.groupby("bio")["piece_km2"].sum().idxmax(),
                          "assessed_km2": grp["piece_km2"].sum()})
    return ov.groupby("unit_id").apply(_a, include_groups=False)

# ---------------------------------------------------------------------------
# GRID builder (equal-area square lattice aligned to global origin)
# ---------------------------------------------------------------------------
def make_grid(footprint, res_m):
    minx, miny, maxx, maxy = footprint.total_bounds
    x0 = np.floor(minx/res_m)*res_m; y0 = np.floor(miny/res_m)*res_m
    xs = np.arange(x0, maxx+res_m, res_m); ys = np.arange(y0, maxy+res_m, res_m)
    cells = [box(x, y, x+res_m, y+res_m) for x in xs[:-1] for y in ys[:-1]]
    g = gpd.GeoDataFrame(geometry=cells, crs=C.CRS)
    # keep only cells intersecting the assessed footprint
    fp = footprint.union_all()
    g = g[g.intersects(fp)].reset_index(drop=True)
    g["unit_id"] = [f"c{i}" for i in range(len(g))]
    g["unit_km2"] = g.geometry.area / 1e6
    return g

# ---------------------------------------------------------------------------
# BUILD one catchment at one "resolution" ('polygon' or metres)
# ---------------------------------------------------------------------------
def build(name, resolution):
    bench = load_benchmark(name)
    src = dict(ntls=clip_bbox(ntls, bench.total_bounds),
               lump=clip_bbox(lump, bench.total_bounds, repair=True),  # repair small subset only
               capad=clip_bbox(capad, bench.total_bounds),
               nvis=nvis_polygons(bench.total_bounds),
               dea_path=C.dea_tif(name))
    if resolution == "polygon":
        units = bench.copy().reset_index(drop=True)
        units["unit_id"] = [f"p{i}" for i in range(len(units))]
        units["unit_km2"] = units.geometry.area / 1e6
        # for polygon mode the expert value is the polygon's own bio (no aggregation needed)
        bio = pd.DataFrame({"unit_id": units["unit_id"], "biorisk_awm": units["bio"],
                            "biorisk_majority": units["bio"], "assessed_km2": units["unit_km2"]}
                           ).set_index("unit_id")
    else:
        units = make_grid(bench, int(resolution))
        bio = aggregate_bio(units, bench)
    df = units[["unit_id", "unit_km2"]].merge(bio, on="unit_id", how="inner")
    df["coverage_frac"] = (df["assessed_km2"] / df["unit_km2"]).clip(0, 1)
    for sname, fn in REGISTRY.items():
        vals = fn(units, src)
        df[sname] = df["unit_id"].map(vals)
    df.insert(0, "resolution", resolution)
    df.insert(0, "catchment", name)
    return df, units

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    grid_rows, poly_rows, report = [], [], []
    report.append("V2 HARMONIZATION BUILD (pure data; no statistics)")
    report.append(f"CRS={C.CRS}  resolutions={C.RESOLUTIONS_M}  + polygon anchor")
    report.append("")
    for name in C.BENCHMARKS:  # includes Weddell (kept, flagged as biovalue scheme)
        for res in ["polygon"] + C.RESOLUTIONS_M:
            df, _ = build(name, res)
            cov50 = int((df["coverage_frac"] >= 0.5).sum())
            report.append(f"{name:10s} res={str(res):8s} units={len(df):5d}  cov>=50%={cov50:5d}  "
                          f"bio[{df.biorisk_awm.min():.2f},{df.biorisk_awm.max():.2f}]  "
                          f"sig_landsys NaN={df.sig_landsys.isna().sum()}  conv NaN={df.convertibility.isna().sum()}")
            (poly_rows if res == "polygon" else grid_rows).append(df)
            print(report[-1], flush=True)

    grid = pd.concat(grid_rows, ignore_index=True)
    poly = pd.concat(poly_rows, ignore_index=True)
    grid.to_parquet(os.path.join(C.PROC, "harmonized_grid.parquet"))
    poly.to_parquet(os.path.join(C.PROC, "harmonized_polygon.parquet"))
    report.append(""); report.append(f"grid rows={len(grid)}  polygon rows={len(poly)}  elapsed={time.time()-t0:.0f}s")
    open(os.path.join(C.PROC, "build_report.txt"), "w").write("\n".join(report) + "\n")
    print("\nwrote:", C.PROC)


if __name__ == "__main__":
    main()
