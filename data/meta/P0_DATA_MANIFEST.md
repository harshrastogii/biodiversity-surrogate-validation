# Phase P0 — data manifest (NT surrogate-validation V2)

Status as of acquisition run. All paths relative to `v2/` unless noted. Workflow CRS = **EPSG:3577** (GDA94 / Australian Albers). Every layer below is reprojectable to 3577 with geopandas; LUMP is already 3577.

## Expert biodiversity benchmarks (response variable)

| Catchment | On disk | Layer | Field | CRS | n polys | Hex coverage (10km) | Notes / limitation |
|---|---|---|---|---|---|---|---|
| Roper | `../nt_exposure/data/roper_intersection.gpkg` | roper_intersection | BIORISK | 3577 | 6343 | 244 hexes (196 ≥50%) | Large; primary V1 benchmark. |
| Larrimah | `../datasets/Larrimah/.../Larrimah_BioRisk.gdb` | Larrimah_Biodiversity_Risk | BIORISK | 4283 | 19 | 18 hexes (4 ≥50%) | Small; arid. |
| Wadeye | `../datasets/Wadeye/.../Wadeye_Biodiversity.gdb` | Wadeye_BiodiversityRisk | BIORISK | 4283 | 412 | 8 hexes (2 ≥50%) | Small; coastal. |
| Weddell | `../datasets/Greater_Weddell/.../*.gdb` | Biodiversity_values | BV_OVERALL | 4283 | 20481 | 11 hexes (3 ≥50%) | **Different scheme** (BioValues) → crosswalk, keep separate. |
| **Gunn Point** (NEW) | `data/raw/benchmarks/GunnPoint/.../GunnPt_BioRisk.gdb` | GunnPt_BiodiversityRisk | BioRisk | 4283 | 23498 | 18 hexes (8 ≥50%) | **Full BIORISK gradient (cls 1–5 all present); best-balanced new benchmark.** 713 km². |
| **Deep Well / NTP3910** (NEW) | `data/raw/benchmarks/DeepWell/.../MTF_NTP3910.gdb` | NTP3910_biodiversity_risks_values | BIORISK | 4283 | 6 | 3 hexes (0 ≥50%) | **Negligible at hex resolution**; only usable at fine (~1 km) grid or as robustness. |

Benchmark verification outcome:
- **Katherine** and **Western Davenport**: NO spatial biodiversity-risk polygon layer on data.nt.gov.au (report/GDE only) → **cannot be gridded as a benchmark; excluded** (documented, not a loss of usable data).
- BIORISK scale is the identical NT "Mapping the Future" scheme across Roper/Larrimah/Wadeye/Gunn Point/Deep Well (1 Nil→5 High, 0 Not assessed, 9 Water). Confirm Gunn Point/Deep Well class-description tables at P1.
- All benchmarks come from the same MTF program → methodologically non-independent across catchments (handle with catchment random effects, not by pretending independence).

## Surrogate layers (predictors)

| Dataset | On disk | Layer | CRS | n | Purpose | Limitation |
|---|---|---|---|---|---|---|
| NT Land Systems | `data/raw/surrogates/NTLS/NTLS_1M/Datasets/ESRI/ntls_1m.gdb` | ntls_1m | 4283 | 16831 | Incumbent significance surrogate (land-system rarity) — the hypothesis under test | **Coarse (1:250k N / 1:1M S)** — likely why land-system rarity underperforms. Fields: LANDSYSTEM, MAPUNIT, CLASS, LANDFORM, SOIL, VEGETATION. |
| NT Land Use (LUMP 2016–2024) | `data/raw/surrogates/LUMP/.../LUMP_2016_2024.gdb` | LandUseMapping | **3577** | 103764 | Convertibility source, **independent of the biodiversity benchmark** | Land-use snapshot; ALUM codes (LU_CODE, PRIM_NO/SEC_NO). Convertibility = a *mapping* from LU class → convertibility (pre-register the mapping). CONFIDENCE field varies. |
| Protection (CAPAD) | `../nt_exposure/data/capad/` (in V1 repo) | CAPAD terrestrial | (check) | — | Protection (1−P) | Already in hand; optional refresh to latest CAPAD. |
| SOCS | `../nt_exposure/data/socs/` (in V1 repo) | Sites of Conservation Significance | — | — | Component of significance | Already in hand. |

## NOT downloaded (with reason)

- **NVIS v7 vegetation (100 m)** — *Essential, but pending MANUAL download.* Only reachable via the DCCEEW ArcGIS Hub JS portal (`fed.dcceew.gov.au`); data.gov.au holds HTML landing pages only, and the AGOL/Hub download endpoints returned 400/invalid to automated fetch. **Needed at the surrogate-comparison step (P1/P2), not to start P0** — so it does not block progress. See manual instructions in the P0 report.
- **ABARES ALUM national (50 m raster)** — *not downloaded (redundant).* NT LUMP already supplies NT land use at finer detail in the target CRS and is what ALUM ingests for NT. Download only if national-consistency is later required.
- **Optional layers** (DEA Fractional Cover, ALA/SDM, DEM landform, fire) — deferred to their phases (P2+), per instruction not to fetch Optional data prematurely.

## Compatibility verdict
All benchmark + surrogate layers load cleanly (geopandas/fiona), carry valid geometry, and reproject to EPSG:3577. No format or licence blockers (all CC-BY / attribution). V2 can begin against these once NVIS is manually retrieved for the surrogate-comparison step.
