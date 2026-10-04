# P4 data checks (run 2026-10-04)

Checks made before the final run. Every number below was computed from the files named, with the
code in this repository and the environment listed in section 1.

## 1. Environment

Python 3.13.1 virtual environment (`.venv/`, not committed), packages from `requirements.txt`:

| Package | Version |
|---|---|
| numpy | 2.3.5 |
| pandas | 2.3.3 |
| scipy | 1.16.3 |
| geopandas | 1.1.3 |
| shapely | 2.1.2 |
| fiona | 1.10.1 |
| pyarrow | 21.0.0 |
| rasterio | 1.5.0 |
| rasterstats | 0.21.0 |
| libpysal | 4.15.0 |
| esda | 2.10.0 |
| matplotlib | 3.10.6 |
| pystac-client | 0.9.0 |
| openpyxl | 3.1.5 (added only to read the class-description spreadsheets for this check) |

GDAL bundled with the pip wheels: rasterio 3.12.1, fiona 3.9.2.

**NVIS raster geodatabase.** The pip rasterio build cannot open
`NVIS_V7_0_AUST_EXT.gdb` (no OpenFileGDB raster driver: "not recognized as being in a supported
file format"). The conda environment `geo` (GDAL 3.13.1) opens it and lists the subdatasets
`NVIS7_0_AUST_EXT_MVG_ALB` and `NVIS7_0_AUST_EXT_MVS_ALB`, as RESEARCH_LOG P2 describes. The
pipeline reads the GeoTIFF warped from the MVG subdataset
(`data/raw/surrogates/NVIS_tif/nvis7_mvg_nt_100m.tif`), which the pip build reads without problems.

## 2. Roper benchmark source

`scripts/config.py` read Roper from `../nt_exposure/data/roper_intersection.gpkg`, a product of the
earlier project. The original NT dataset "Risk to Biodiversity of the Central Roper River Catchment,
2024" was downloaded on 2026-10-04 from the resource listed by
`https://data.nt.gov.au/api/3/action/package_show?id=risk-to-biodiversity-of-the-central-roper-river-catchment-2024`
(`BioRisk_CentralRoper.zip`, 7,978,584 bytes, CC BY) into `data/raw/benchmarks/Roper/`. The polygon
layer is `Roper_biodiversity_risks` in `Datasets/ESRI/MTF_Roper.gdb` (EPSG:4283), class field `BIORISK`.

Both layers reprojected to EPSG:3577 and geometries repaired with `shapely.make_valid`:

| | Original NT layer | Intersection product |
|---|---|---|
| Polygons | 3,079 | 6,343 |
| BIORISK codes present | 1, 3, 4, 5 | 1, 3, 4, 5 |
| Total area | 17,254.1 km² | 17,254.1 km² |
| Polygons < 1 m² | 24 | 2,264 |
| Polygons < 1 ha | 1,290 (42%) | 4,221 (67%) |
| Median polygon area | 1.844 ha | 0.090 ha |

Area and polygon count by class:

| BIORISK | Original: polygons | Intersection: polygons | Area (km², both) | Share of area |
|---|---|---|---|---|
| 1 | 42 | 437 | 78.3 | 0.5% |
| 3 | 437 | 1,207 | 13,262.0 | 76.9% |
| 4 | 2,529 | 4,582 | 3,898.8 | 22.6% |
| 5 | 71 | 117 | 15.0 | 0.1% |

The two layers cover the same land with the same class areas. The intersection product carries
the land-use fields `PRIM_NO` and `PRIM_DESC`: it is the expert layer cut along the boundaries of
the NT land-use map, which is also the source of the convertibility surrogate. That split doubled
the polygon count and created the sub-square-metre fragments. From P5, `config.BENCHMARKS["Roper"]`
points at the original layer.

## 3. BIORISK class definitions

Taken from each dataset's own attribute fields (`BIODESC1`, `BIODESC2`, `BIODESC3`; Gunn Point
`BioDesc1–3`) and, for Larrimah and Wadeye, the class-description spreadsheets shipped with the data
(`MTF_*_Class_Descriptions.xlsx`). All five datasets use codes 1–5 in the same order, 0 for not
assessed and 9 for water.

| Class | Roper (2024) | Larrimah (2021) | Wadeye (2021) | Gunn Point (2020) | Deep Well (2021) |
|---|---|---|---|---|---|
| 1 | NIL – Highly modified | NIL – Highly modified (sheet only) | NIL – Highly modified (sheet only) | NIL – Highly modified | not present |
| 2 | not present | LOW – No significant biodiversity value (sheet only) | LOW – No significant value | LOW – No significant biodiversity value | LOW – No significant biodiversity value |
| 3 | MITIGABLE – Apply the mitigation hierarchy | MITIGABLE – Apply land management strategies | MITIGABLE (sheet only) | **UNCERTAIN – Requires further biodiversity assessment** | MITIGABLE – Apply land management strategies |
| 4 | MODERATE – Sensitive and/or significant vegetation | MODERATE – Sensitive and/or significant vegetation | MODERATE – Sensitive and/or significant biodiversity | MODERATE – Sensitive and/or significant vegetation | MODERATE – Sensitive and/or significant biodiversity |
| 5 | HIGH – High biodiversity value | HIGH (sheet only) | HIGH – High biodiversity value | HIGH – High biodiversity value | not present |

Full definitions where they differ:

- **Class 3.** Roper, Larrimah, Deep Well: "Land that may provide habitat for broadly-occurring
  threatened species or other biodiversity values. Retention of a proportion of this habitat (e.g.
  through application of the NT Land Clearing Guidelines) may be required." Gunn Point: "Land that
  may require further biodiversity assessment before any development approval, dependent on the
  likelihood of occurrence of threatened species. Some land may require management or protection."
- **Class 4.** Roper adds "(including groundwater-dependent ecosystems)"; Roper, Larrimah, Wadeye and
  Deep Well add "and/or occurrence of species of conservation interest"; Gunn Point lists vegetation
  types only ("as identified in the NT Land Clearing Guidelines").
- **Class 5.** Roper, Larrimah, Wadeye: "significant vegetation community type and/or habitat for
  threatened species". Gunn Point: "significant vegetation community type in combination with
  threatened species occurrence records".

**Conclusion.** The scales share order and labels for classes 1, 2, 4 and 5, but are not identical:
Gunn Point's class 3 is a different category (uncertain, needs survey), and its classes 4 and 5 use
narrower or conjunctive rules. The Methods and Limitations say so.

**Greater Weddell** uses `BV_OVERALL` with five levels: Highly modified area, Low, Medium, High,
Very high, plus component value fields (`BV_RAIN`, `BV_SSH`, `BV_MANG`, `BV_RIPWET`, `BV_LGETREES`
and threatened-species fields).

**Inputs used by the assessors** (dataset lineage documents and attribute fields):

- **Roper** (lineage, 29 Oct 2025; Buckley et al. 2024 technical report): linework derived from the
  Melaleuca Survey of the NT, Monsoon Vine-Forest distribution, vegetation communities of southern
  Flying Fox Station, **Land Systems of the Roper River Catchment**, the **Land Use Mapping Project of
  the NT 2016–2024**, the Australian Hydrological Geospatial Fabric v3.2 and Sites of Conservation
  Significance; attributes `SOCS`, `SSV` (sensitive/significant vegetation), `MODIF`. Some source data
  were mapped at 1:250,000.
- **Larrimah**: significant vegetation (`SIGVEG`), groundwater-dependent ecosystems (`GDE*`), land
  units from land-resource survey (`LAND_UNIT`, `LU_SURVEY`).
- **Wadeye**: vegetation community (`VCOMM`) and class-specific rule flags (`C5_COMPLEX`,
  `C5_WETRF`, `C5_DRYRF` for class 5; `C4_SENSIG`, `C4_WETLAND`, `C4_GDE`, `C4_GREV_HD` for class 4;
  `C2_GMYOSOD` for class 2), land unit.
- **Gunn Point**: per-class rule fields `C1_Class`–`C5_Class`. Class 4 and 5 vegetation from Napier
  (2020) vegetation mapping at 1:25,000 (14,630 and 4,751 polygons), class 5 threatened-species
  records from Cuff (2019). Class 4 communities: wetland (8,038 polygons), mangroves and salt flats
  (3,417), dry rainforest (1,559), sandsheet heath (1,130), wet rainforest (489). Class 3 sources
  flag *Cycas*, *Typhonium* and *Stylidium* habitat.
- **Deep Well** (lineage, 17 Oct 2025; Stokeld et al. 2021): linework, map units and landform classes
  from the Mapping the Future land-resource survey of NTP 3910 at 1:100,000; attributes `SSV`,
  `FAUNA`, `FLORA`.
- **Greater Weddell** (lineage, 14 May 2025): vegetation map, threatened flora and fauna records,
  habitat models for *Cycas armstrongii*, *Stylidium ensatum* and critical-weight-range mammals,
  stands of large hollow trees, *Typhonium praetermissum* priority areas.

The Roper benchmark therefore shares sources with two surrogates (land systems and land-use
mapping). The Methods and Limitations state this.

## 4. Dataset references

Checked against the CKAN API (`package_show`) on 2026-10-04. Every URL resolved.

| Reference | Catalogue title | Catalogue record created | Status |
|---|---|---|---|
| Land systems | Northern Territory Land Systems (compilation of north_250 and south_1M) | 2019-12-09 | URL correct. Dataset citation date 2013-10-18 (NTLIS metadata: creation; currency 2011-01-01 to 2013-10-18; status completed); the shapefile metadata gives the same date. Year changed from n.d. to 2013. |
| Gunn Point 2020 | Risk to Biodiversity in the Gunn Point Area, 2020 | 2020-07-17 | Title and URL correct. |
| Deep Well 2021 | Biodiversity Assessment Study of NTP 3910 in the Deep Well Area, 2021 | 2025-10-20 | Title and URL correct. |
| Wadeye 2021 | Risk to Biodiversity in the Wadeye Area, 2021 | 2021-06-30 | Correct. |
| Larrimah 2021 | Risk to Biodiversity of the Larrimah Area, 2021 | 2022-06-06 | Correct. |
| LUMP | Land Use Mapping Project of the Northern Territory, 2016 - 2024 (LUMP) | 2020-05-07 | Correct. |
| Roper 2024 | Risk to Biodiversity of the Central Roper River Catchment, 2024 | 2025-10-29 | Correct. |
| Greater Weddell | Biodiversity Assessment of the Greater Weddell Subregion | 2025-05-27 | Correct. |

**CAPAD.** The layer used (`../nt_exposure/data/capad/Collaborative_Australian_Protected_Areas_Database_(CAPAD)_–_Terrestrial.shp`,
14,492 features) is **CAPAD 2024 – Terrestrial**: its metadata names CAPAD 2024 and lists 2022 among
the previous releases, and the latest gazettal date in the attributes is 2024-07-25. The manuscript
cited CAPAD 2022; the reference now cites CAPAD 2024
(`https://www.dcceew.gov.au/environment/land/nrs/science/capad/2024`, HTTP 200).

## 5. The tidal vegetation group

`NVIS_RARITY` recomputed exactly as in `harmonize.py` from `nvis7_mvg_nt_100m.tif` (codes 25, 27,
28 and 99 excluded): 22 native Major Vegetation Groups. The group with Territory-wide rarity ≈ 0.477
is **MVG 23, Mangroves** (rarity 0.4766, 4,045.3 km² in the NT). The name comes from the raster's
value attribute table (`VAT_NVIS7_0_AUST_EXT_MVG_ALB`, field `MVG_NAME`), read with GDAL 3.13.1.

Rarities of the rarest groups, for reference: MVG 14 Mallee Woodlands and Shrublands 1.000; MVG 32
Mallee Open Woodlands and Sparse Mallee Shrublands 0.785; MVG 1 Rainforests and Vine Thickets 0.517;
MVG 8 Casuarina Forests and Woodlands 0.511; MVG 23 Mangroves 0.477; MVG 24 Inland aquatic 0.437.
