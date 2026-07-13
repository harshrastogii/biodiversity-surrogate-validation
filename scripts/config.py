"""
config.py — locked paths, CRS, catchment registry, and surrogate scoring for V2.
Absolute paths anchored at the project root so scripts run from anywhere.
Nothing here is analysis; it is configuration + reproducibility constants.
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # NT_Conservation_Project
V1   = os.path.join(ROOT, "nt_exposure")
V2   = os.path.join(ROOT, "v2")
RAW  = os.path.join(V2, "data", "raw")
PROC = os.path.join(V2, "data", "processed")
CRS  = 3577                      # GDA94 / Australian Albers (equal-area)
SEED = 42
RESOLUTIONS_M = [1000, 2000, 5000, 10000]   # resolution ladder (metres); plus "polygon" mode

# ---- expert benchmarks -----------------------------------------------------
# scheme: 'biorisk' (ordinal 1..5, MTF) | 'biovalue' (Weddell BV_OVERALL, separate scale)
BENCHMARKS = {
 "Roper":     dict(path=os.path.join(V1, "data", "roper_intersection.gpkg"),
                   layer="roper_intersection", field="BIORISK", scheme="biorisk"),
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
BIORISK_POOL = ["Roper", "Larrimah", "Wadeye", "GunnPoint", "DeepWell"]  # identical scale
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
