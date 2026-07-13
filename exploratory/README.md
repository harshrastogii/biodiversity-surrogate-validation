# Exploratory work (superseded)

This folder preserves earlier **exploratory** analyses for the complete research record.
**Nothing here is part of the confirmed Version 2 results or the manuscript.** The final,
confirmatory framework lives in `../scripts/` with outputs in `../analysis_p3/`, and the
manuscript in `../paper/MANUSCRIPT.md`. Every numerical claim in the manuscript traces to
`../analysis_p3/`, not to this folder.

## `pooled_validation/` — first multi-catchment validation (hex resolution)

The initial attempt to extend the single-catchment validation to multiple catchments, run at
the **10 km hexagonal grid** resolution inherited from Version 1.

- `pooled_validation.py` — per-catchment Spearman + random-effects meta-analysis at hex level.
- `sensitivity_checks.py` — meta weights, leave-one-catchment-out, coverage checks.
- `self_review.py` — adversarial checks (spatial-support mismatch, encoding sensitivity, etc.).
- `PREREGISTRATION.md` — the pre-registration for that hex-level pooled analysis.
- `outputs/` — its result tables (decomposition, heterogeneity, per-catchment, Weddell).

### Why it was superseded
This exploratory pass exposed problems that the final framework was built to fix:
- at 10 km resolution the small catchments contribute too few, poorly-covered hexes
  (change-of-support), and gridding finer than the expert polygons induces **pseudoreplication**
  and spurious correlations;
- it did not yet use native expert-polygon units, co-primary (per-unit / per-area) estimands, a
  spatial block bootstrap, a circularity control, or out-of-sample cross-validation.

The final Version 2 (native expert-polygon unit, co-primary estimands, spatial block bootstrap,
circularity control, and a spatially cross-validated joint model) replaces it. The full rationale
and decision trail are in `../RESEARCH_LOG.md` (see the P1 milestone review and pre-registrations
P3.PR1/PR2).

**Treat all numbers in this folder as exploratory and not for citation.**
