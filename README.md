# Validating open-data biodiversity surrogates against expert assessment (Northern Territory)

A pre-specified, multi-catchment validation of open-access spatial **biodiversity surrogates**
against independent **expert biodiversity assessments** in the Northern Territory, Australia.
This repository contains the complete, reproducible analysis pipeline, the confirmed results, the
figures, and the manuscript draft (target journal: *Diversity and Distributions*).

> **Central question.** In a data-poor jurisdiction, how well — and via which surrogate — can
> open-access spatial data reproduce independent expert biodiversity assessment; does combining
> surrogates help or transfer to unsurveyed landscapes; and are these answers robust to the
> analysis unit, weighting and spatial scale?

## Key findings (P3 version — under revision, see `paper/PANEL_REVIEW.md`)

- The commonly-used **land-system / landform-rarity** surrogate did **not** reproduce expert value
  at the level of expert-delineated units (pooled Spearman ρ = 0.085, 95% CI −0.003 to 0.172).
- A **vegetation-type-rarity** surrogate (NVIS) performed best per unit (ρ = 0.244, 0.149–0.334)
  and retained an independent association after a circularity control (partial ρ = 0.200,
  0.079–0.314).
- **Agricultural convertibility** was the only surrogate positive under both estimands;
  remotely-sensed **vegetation cover** and formal **protection** carried no value signal.
- Conclusions were **estimand- and scale-dependent**; a joint model reached only modest
  out-of-sample agreement (ρ ≈ 0.22–0.27) and did **not** significantly beat the single best
  surrogate.

**In short:** open-data surrogates are weak first-pass screens, not biodiversity-value maps — and
which surrogate looks best depends on the analysis unit, weighting and scale.

## Repository structure

```
.
├── README.md               This file
├── LICENSE                 MIT licence (code); see "Licensing" for text/figures/data
├── requirements.txt        Python dependencies (pinned)
├── RESEARCH_LOG.md         Full decision log + pre-specified analysis plans (P3.PR1/PR2)
├── scripts/                Reproducible pipeline
│   ├── config.py           Paths, catchment registry, locked surrogate scoring
│   ├── harmonize.py        Build analysis dataset (plug-in surrogate registry)
│   ├── fetch_dea.py        Acquire DEA Fractional Cover (condition surrogate)
│   ├── p3_confirmatory.py  Per-catchment + meta-analysis, circularity control
│   ├── p3_blockboot.py     Spatial block-bootstrap hardened inference
│   ├── p3_joint.py         Joint model: spatial-block CV + leave-one-catchment-out
│   ├── p1_sanity.py        Exploratory milestone diagnostic (not confirmatory)
│   └── make_figures.py     Publication figures from frozen outputs
├── analysis_p3/            Frozen confirmatory outputs (csv/json/txt)
├── data/
│   ├── processed/          Harmonised analysis products (native-polygon + grid ladder)
│   └── meta/               P0_DATA_MANIFEST.md (data provenance and licences)
├── paper/
│   ├── MANUSCRIPT.md       Complete Diversity and Distributions draft
│   └── figures/            Figures 1–5 (PDF vector + 300 dpi PNG)
└── exploratory/            Preserved earlier work (superseded); see its README
```

> **Note.** The raw source layers (~0.9 GB of downloaded government data) are **not** stored here.
> They are reproducible from the public sources documented in
> [`data/meta/P0_DATA_MANIFEST.md`](data/meta/P0_DATA_MANIFEST.md); the ignore rules are in
> `.gitignore`. The harmonised attribute tables in `data/processed/` are included, but the spatial
> analyses also need polygon locations: run `scripts/export_centroids.py` once (with the raw
> benchmarks present) and commit `data/processed/polygon_centroids.parquet`; after that every
> analysis re-runs from this repository alone.

## Reproducing the analysis

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Reading the NVIS v7 raster geodatabase requires a GDAL build with the **OpenFileGDB raster**
driver (GDAL ≥ 3.7); see `scripts/config.py` and the research log for the conversion step.

Run order (seeds are fixed; every reported number is regenerated):

```bash
# 1. Acquire raw layers per data/meta/P0_DATA_MANIFEST.md into data/raw/  (+ scripts/fetch_dea.py for DEA)
python scripts/harmonize.py        # -> data/processed/harmonized_{grid,polygon}.parquet
python scripts/p3_confirmatory.py  # -> analysis_p3/ (per-catchment, meta, circularity)
python scripts/p3_blockboot.py     # -> analysis_p3/hardened_* (spatial block bootstrap)
python scripts/p3_joint.py         # -> analysis_p3/joint_* (cross-validated joint model)
python scripts/export_centroids.py # -> data/processed/polygon_centroids.parquet (once; needs raw benchmarks)
python scripts/p4_revision.py      # -> analysis_p4/ (panel-review robustness + multiverse; ~1-3 h)
python scripts/make_figures.py     # -> paper/figures/
```

Figures 2–5 regenerate from the committed `analysis_p3/` outputs alone; Figure 1 additionally
requires the benchmark geometries and an NT boundary layer.

## Analysis plan and research log

The analysis plan was fixed in the research log before the confirmatory runs (after an exploratory
phase; not lodged in a public registry, so we call it *pre-specified*). The full decision trail —
including the plans (`P3.PR1` co-primary estimands; `P3.PR2` confirmatory spec), the
milestone self-reviews, and every design choice with its alternatives — is in
[`RESEARCH_LOG.md`](RESEARCH_LOG.md). Exploratory precursor analyses are preserved under
[`exploratory/`](exploratory/) and are **not** used in the manuscript.

## Data sources and licensing

All inputs are open Northern Territory and Australian Government layers (full provenance in
`data/meta/P0_DATA_MANIFEST.md`): NT *Mapping the Future* biodiversity assessments (benchmarks),
NT Land Systems, NT Land Use Mapping (ALUM), National Vegetation Information System v7,
Digital Earth Australia Fractional Cover, and CAPAD. These remain under their original licences
(CC-BY / attribution) and are **not** redistributed here.

### Licensing of this repository
- **Code** (`scripts/`, `exploratory/*.py`): MIT — see [`LICENSE`](LICENSE).
- **Manuscript, figures, and documentation** (`paper/`, `README.md`, `RESEARCH_LOG.md`):
  Creative Commons Attribution 4.0 International (CC-BY-4.0).
- **Derived data products** (`data/processed/`): CC-BY-4.0, with attribution to the upstream
  NT/Australian Government sources listed above.

## Citation

If you use this work, please cite the manuscript (in preparation) and this repository:

> Rastogi, H. (2026). *Which open-data surrogates reproduce expert biodiversity
> assessment? A pre-specified multi-catchment validation in northern Australia.* Manuscript in
> preparation. Code and data: https://github.com/harshrastogii/biodiversity-surrogate-validation.

*(Author list, DOI, and journal to be finalised.)*

## Disclaimer

This repository accompanies a manuscript under preparation. Results are bounded by the stated
limitations (small effective replication, single jurisdiction, modest effect sizes) and should be
read together with the manuscript's Limitations section.
