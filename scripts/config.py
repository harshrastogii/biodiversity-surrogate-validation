"""
config.py — locked paths, CRS, catchment registry, and surrogate scoring for V2.
Absolute paths anchored at the project root so scripts run from anywhere.
Nothing here is analysis; it is configuration + reproducibility constants.
"""
import os

# V2 = this repository's root, wherever it is cloned. ROOT = the parent project folder that
# holds the V1 repo (nt_exposure/) and the shared raw datasets/ (override with NT_PROJECT_ROOT).
V2   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT = os.path.abspath(os.environ.get("NT_PROJECT_ROOT", os.path.join(V2, "..")))  # NT_Conservation_Project
V1   = os.path.join(ROOT, "nt_exposure")
RAW  = os.path.join(V2, "data", "raw")
PROC = os.path.join(V2, "data", "processed")
CRS  = 3577                      # GDA94 / Australian Albers (equal-area)
SEED = 42
RESOLUTIONS_M = [1000, 2000, 5000, 10000]   # resolution ladder (metres); plus "polygon" mode

# ---- expert benchmarks -----------------------------------------------------
# scheme: 'biorisk' (ordinal 1..5, MTF) | 'biovalue' (Weddell BV_OVERALL, separate scale)
BENCHMARKS = {
 # Original NT dataset (data.nt.gov.au, "Risk to biodiversity of the central Roper River catchment,
 # 2024"). P5: replaces the V1 intersection product, which split expert polygons along land-use lines.
 "Roper":     dict(path=os.path.join(RAW, "benchmarks/Roper/Datasets/ESRI/MTF_Roper.gdb"),
                   layer="Roper_biodiversity_risks", field="BIORISK", scheme="biorisk"),
 "Larrimah":  dict(path=os.path.join(ROOT, "datasets/Larrimah/BioRisk_Larrimah/Datasets/ESRI/Larrimah_BioRisk.gdb"),
                   layer="Larrimah_Biodiversity_Risk", field="BIORISK", scheme="biorisk"),
 "Wadeye":    dict(path=os.path.join(ROOT, "datasets/Wadeye/BioRisk_Wadeye/Datasets/ESRI/Wadeye_Biodiversity.gdb"),
                   layer="Wadeye_BiodiversityRisk", field="BIORISK", scheme="biorisk"),
 "GunnPoint": dict(path=os.path.join(RAW, "benchmarks/GunnPoint/BioRisk_GunnPoint/ESRI/GunnPt_BioRisk.gdb"),
                   layer="GunnPt_BiodiversityRisk", field="BioRisk", scheme="biorisk"),
 "DeepWell":  dict(path=os.path.join(RAW, "benchmarks/DeepWell/Datasets/ESRI/MTF_NTP3910.gdb"),
                   layer="NTP3910_biodiversity_risks_values", field="BIORISK", scheme="biorisk"),
 "Weddell":   dict(path=os.path.join(ROOT, "datasets/Greater_Weddell/BioValues_GreaterWeddell/Datasets/ESRI/Greater_Weddell_biodiversity_assessment.gdb"),
                   layer="Biodiversity_values", field="BV_OVERALL", scheme="biovalue"),
}
BIORISK_POOL = ["Roper", "Larrimah", "Wadeye", "GunnPoint", "DeepWell"]  # same 1-5 order; class wording differs (P4_DATA_CHECKS.md)
BV_MAP = {"Highly modified area": 1, "Low": 2, "Medium": 3, "High": 4, "Very high": 5}

# ---- surrogate sources -----------------------------------------------------
NTLS = dict(path=os.path.join(RAW, "surrogates/NTLS/NTLS_1M/Datasets/ESRI/ntls_1m.gdb"),
            layer="ntls_1m", field="LANDSYSTEM")
LUMP = dict(path=os.path.join(RAW, "surrogates/LUMP/LandUseMapping/LUMP_2016_2024/Datasets/LUMP_2016_2024.gdb"),
            layer="LandUseMapping", field="PRIM_NO")
CAPAD = dict(path=os.path.join(V1, "data", "capad",
             "Collaborative_Australian_Protected_Areas_Database_(CAPAD)_–_Terrestrial.shp"),
             field="IUCN")

# ---- locked scoring (reproduced from V1) -----------------------------------
CONV_SCORE = {1: 0.1, 2: 1.0, 3: 0.4, 4: 0.2, 5: 0.0}   # PRIM_NO -> convertibility; 6=water=no-data
IUCN_STRICT = {"IA", "IB", "II", "III", "IV", "V", "VI"}

# ---- NVIS v7 Major Vegetation Groups (candidate significance surrogate) -----
# Source: NVIS v7.0 extant MVG raster (FGDB), warped to NT/EPSG:3577/100 m GeoTIFF.
# 'MVG rarity' is the direct NVIS analogue of land-system rarity: log-inverse of NT-wide
# native-vegetation area per MVG class, in [0,1]. Non-vegetation / no-data MVG codes are
# EXCLUDED (treated as no-data), so rarity is defined only over genuine native veg:
#   25=cleared/non-native/built, 27=naturally bare, 28=sea/estuary, 99=unknown.
NVIS_MVG_TIF = os.path.join(RAW, "surrogates", "NVIS_tif", "nvis7_mvg_nt_100m.tif")
NVIS_EXCLUDE = {25, 27, 28, 99}

# ---- DEA Fractional Cover (condition/intactness surrogate) ------------------
# Per-catchment veg_cover = 100 - median bare-soil% (ga_ls_fc_pc_cyear_3, 30 m, EPSG:3577).
# Higher = more vegetated/intact. Limitation: single reference year (rainfall-sensitive);
# multi-year median is a later refinement. NOTE: this is a CONDITION proxy, not a value proxy.
DEA_DIR = os.path.join(RAW, "surrogates", "DEA")
def dea_tif(catchment):
    return os.path.join(DEA_DIR, f"dea_vegcover_{catchment}.tif")

# ---- analysis-ready polygon table (P4 audit fix) ----------------------
# Area-weighted overlays leave floating-point residue (e.g. Wadeye convertibility is constant
# at 0.1 but stored as 0.0999999999999999/0.1/0.1000000000000002; Deep Well NVIS rarity varies
# only at ~1e-6). Ranking that residue manufactures spurious correlations, so every surrogate
# is rounded to 4 d.p. (differences < 1e-4 on a 0-1 score are overlay residue) before analysis;
# a surrogate constant after rounding is non-estimable.
SURR_COLS = ["sig_landsys", "sig_nvis_mvg", "cond_dea", "convertibility", "protection", "iucn_frac"]
SURR_DECIMALS = 4
def load_polygons():
    import pandas as pd
    poly = pd.read_parquet(os.path.join(PROC, "harmonized_polygon.parquet"))
    poly[SURR_COLS] = poly[SURR_COLS].round(SURR_DECIMALS)
    return poly
