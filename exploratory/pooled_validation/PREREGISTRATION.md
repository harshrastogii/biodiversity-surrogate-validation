# Pre-registration — pooled multi-catchment validation of the NT exposure index

**Status:** written and frozen BEFORE observing any spatially-corrected pooled result.
**Author process note:** the exploratory hex-level correlations already seen (session 1) are
treated as *hypothesis-generating only*. The analyses below are the *confirmatory* tests; any
result not listed here is labelled exploratory in the output.

## 0. Fixed parameters (locked)
- Significance-combination rule for the primary exposure = `mean` (matches the frozen Roper
  validation, `roper_validation.py` decision D4). All five rules reported as sensitivity.
- Exposure architecture = `significance * conv_score * (1 - prot_frac)` (locked, unchanged).
- Random seed = 42. Bootstrap draws = 5000. Moran permutations = 999.
- Unit of analysis = hex (86.6 km², EPSG:3577), matching the index resolution and the frozen
  Roper validation.
- Per-hex benchmark = area-weighted **mean ordinal** BIORISK over assessed area in the hex
  (matches Roper D3). Majority class used only for categorical checks.
- Primary sample = **all hexes touched** by an assessment; sensitivity sample = hexes with
  **≥50 % coverage** (matches Roper D2).

## 1. Datasets and pooling rule
- **Confirmatory pool = Roper + Larrimah + Wadeye.** Justification: the three assessments use
  the *identical* NT "Mapping the Future" BIORISK ordinal scale (verified: class-description
  tables match exactly — 1 Nil/highly-modified, 2 Low, 3 Mitigable, 4 Moderate, 5 High; 0 Not
  assessed, 9 Water). This makes the ordinal benchmark comparable across catchments.
- **Greater Weddell = separate robustness analysis.** It uses a different "BioValues" scheme
  (`BV_OVERALL`: Highly modified < Low < Medium < High < Very high). Because Spearman is
  rank-based, Weddell's *within-catchment* correlation is invariant to the exact crosswalk
  integers (only the monotone order matters, which is unambiguous). It is therefore reported
  as an independent validation, NOT pooled onto the BIORISK scale (pooling would require
  cross-programme interval comparability we cannot establish).

## 2. Confirmatory hypotheses (pre-specified)
- **C1 (primary).** Does the index track expert biodiversity value *within catchments*, on
  average? Estimand: random-effects (DerSimonian–Laird) meta-analytic pooled Spearman of
  `exposure_full` vs BIORISK across the 3 catchments, using Fisher-z with spatially-corrected
  effective sample sizes. Directional H1: pooled ρ > 0.
- **C2 (decomposition).** Repeat the meta-analysis for `convertibility`, `significance`,
  `sig_landsys` (land-system rarity only), and `exposure_SOCSremoved`. Pre-specified question
  carried from the manuscript: is the Roper ordering (convertibility ρ > significance ρ)
  preserved when generalised across catchments? This is the test that can confirm, weaken, or
  overturn the manuscript's central claim.
- **C3 (heterogeneity).** Cochran's Q and I² on the per-catchment Spearman estimates, to judge
  whether between-catchment differences exceed sampling noise. Pre-declared caveat: with k=3
  catchments the power of Q is very low; a non-significant Q does NOT prove homogeneity.

## 3. Spatial-autocorrelation correction (locked, replicates the frozen method)
Applied per catchment exactly as `spatial_correction.py`: distance-band contiguity graph
(≤10.1 km on hex centroids), row-standardised; Moran's I (999 permutations); spatial
block-bootstrap 95 % CIs (block = hex + neighbours, ~n/5 seeds, capped to n); Clifford–
Richardson effective sample size from lag-1 autocorrelation of the two rank fields. Pooled
effective n = sum of per-catchment n_eff. Meta-analytic variances use n_eff, not n.

## 4. Exploratory analyses (NOT confirmatory; labelled as such in output)
- Per-catchment point estimates and any sign reversals (esp. convertibility).
- Greater Weddell result (separate scale).
- Naive fully-pooled Spearman (confounded by between-catchment mean differences) — reported
  only as a contrast to the within-catchment meta-analytic estimate.
- Coverage-weighted and ≥50 %-coverage robustness variants.
- Categorical (BIORISK ≥ 4) agreement pooled.

## 5. Interpretation rules (fixed in advance)
- **Observation** = a computed quantity. **Statistical evidence** = a quantity with its
  spatially-corrected CI / p-value and n_eff. **Interpretation** = what the evidence implies
  for the index, bounded by the CIs. **Speculation** = anything beyond that (explicitly
  flagged).
- Decision on the manuscript's central claim:
  - If pooled significance ρ CI lies clearly below pooled convertibility ρ → manuscript claim
    holds; keep it.
  - If the two CIs overlap substantially and pooled significance ρ CI excludes 0 → manuscript
    claim is *catchment-specific*, not general; weaken/reframe.
  - If neither pooled ρ CI excludes 0 → the index is not validated at all across catchments;
    report honestly.
- Small-n honesty: any per-catchment n < 20 is treated as individually uninterpretable; such
  catchments contribute only through the n_eff-weighted meta-analysis, which down-weights them.

## 6. Documented assumptions
A1. Ordinal comparability of BIORISK across the 3 catchments (justified by identical scale
    definitions; still an assumption because field teams/years differ).
A2. Area-weighted mean of an ordinal scale is a usable continuous benchmark (matches Roper;
    defensible because classes are ordered and Spearman only needs monotonicity).
A3. Catchments are spatially disjoint, so cross-catchment contiguity is nil and per-catchment
    spatial graphs are independent (verified: bounding boxes do not overlap).
A4. Effective-n and block definitions are approximations (as in the frozen pipeline).
