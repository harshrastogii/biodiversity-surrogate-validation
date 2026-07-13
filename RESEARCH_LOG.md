# RESEARCH_LOG — NT surrogate-validation, Version 2

Living record of scientific decisions: each entry gives the decision, alternatives
considered, evidence, and remaining limitations. V1 (`../nt_exposure/`) is untouched.
Confirmatory vs exploratory status is tracked explicitly.

---

## P1 — fine-resolution rebuild + resolution-ladder scaffolding

### D1.1 — Study framing (carried from planning; recorded here for provenance)
**Decision:** validation-first, surrogate-benchmarking design. Expert BIORISK = ordinal
response; open-data surrogates = competing predictors, tested across a spatial-resolution
ladder. **Not** an index-construction paper.
**Why:** V1 established (i) weak overall agreement, (ii) non-identifiable component
attribution at 10 km, (iii) a fatal change-of-support problem for small catchments. Making
resolution a first-class variable converts V1's biggest weakness into the contribution.
**Status:** framing (not a statistical claim).

### D1.2 — Analysis unit: equal-area square grid ladder + native-polygon anchor
**Options:**
- (a) Regular equal-area **square grid** at multiple grains (1, 2, 5, 10 km).
- (b) **Hexagonal** grid (as V1 used for the NT product).
- (c) **Native expert-polygon** units (each BIORISK polygon = 1 row; surrogates area-weighted in).
**Decision:** build (a) as the core MAUP ladder AND (c) as the finest "maximal-information"
anchor. Defer (b).
**Why:** squares nest cleanly across grains and align with the raster surrogates coming later
(NVIS 100 m, DEA 25–30 m), making zonal aggregation trivial and consistent; hexagons add
geometry cost with no scientific gain here (the grid is a measurement instrument, not a
delivered product). Native-polygon units (c) eliminate change-of-support on the *response*
entirely and maximise n (e.g. Gunn Point = 23,498 polygons), giving a support-mismatch-free
anchor the V1 hex analysis lacked.
**Limitation:** square grids are not rotation-invariant (a MAUP zoning effect); we test grain
(scale) systematically but zoning only lightly (origin offset as a later robustness). Native
polygons are unequal-area → correlations/models must area-weight.

### D1.3 — Incumbent surrogate definitions reproduced faithfully from V1
Rebuilt exactly as V1 so resolution is the *only* thing that changes (a fair scale test):
- **Significance = land-system rarity.** NT-wide area per `LANDSYSTEM` (from `ntls_1m`),
  `rarity = 1 − (log A − min log A)/(max log A − min log A)`, area-weighted per unit. Rarity
  lookup computed once from the full NT layer, then applied within catchments (preserves the
  NT-wide definition). Source: `attribute_landsys.py`.
- **Convertibility.** Area-weighted mean over non-water land of `PRIM_NO → {1:0.1, 2:1.0,
  3:0.4, 4:0.2, 5:0.0}` (LUMP ALUM primary class); class 6 (water) = no-data. Source:
  `attribute_convertibility.py`.
- **Protection.** Fraction of unit under CAPAD terrestrial (`prot_frac`); IUCN Ia–VI strict
  fraction (`iucn_frac`). Source: `attribute_protection.py` (V1 used an NT-Parks MVP layer not
  in the repo; **we substitute CAPAD**, the tracked national-standard layer — documented change).
**Limitation:** the convertibility `PRIM_NO→score` map and the rarity normalisation are locked
*construction choices*, not measurements; both are pre-registered as sensitivity axes for later
phases. Land systems are coarse (1:250k N / 1:1M S) — the very limitation under test.

### D1.4 — Surrogate registry (NVIS-ready architecture)
**Decision:** surrogates are entries in a registry (`name → extractor(cells)->Series`). The
harmonizer calls every registered extractor and writes one column each. Adding NVIS / SDM / DEA
later = appending a registry entry; no change to grid, aggregation, or downstream code.
**Why:** satisfies "NVIS can be added later without major changes"; keeps the incumbent test and
future candidates on identical footing.

### D1.5 — BIORISK aggregation to units
**Decision:** area-weighted **mean ordinal** BIORISK per unit (primary, matches V1), plus
area-**majority** class and `coverage_frac`. No coverage filtering in P1 (kept as a column;
filtering is an analysis-phase decision, P3/P4).
**Limitation:** area-weighted mean of an ordinal scale assumes interval spacing — a known
assumption inherited from V1; the majority class is retained as the interval-free alternative
(V1 self-review showed the two can differ materially).

### Open items entering P2+
- NVIS (manual download pending) → add as a significance-candidate registry entry.
- Class-description tables for Gunn Point / Deep Well to confirm identical BIORISK semantics.
- Weddell held separate (BioValues scheme) with a documented crosswalk; Spearman anchoring.

---

## P1 MILESTONE REVIEW (self-review as a top-tier reviewer) — a course correction

Build succeeded (6 catchments × {polygon, 1/2/5/10 km}; products in `data/processed/`). Fine
gridding hugely increases unit counts (Larrimah 19→593 at 1 km, Wadeye→230, Gunn Point→797).
**But the exploratory sanity check (`p1_sanity.py`) exposed a trap that would have wrecked the
paper, so the naive "resolution ladder reveals signal" direction is REJECTED.**

### Finding R1 — fine-grid correlations are an ARTEFACT, not rescued signal. [statistical evidence]
For land-system rarity vs BIORISK, the grain matters enormously and in a misleading way:

| Catchment | per-expert-polygon (unweighted) | area-weighted polygon | 1 km grid |
|---|---|---|---|
| Larrimah (19 polys) | −0.031 | +0.517 | +0.585 |
| Wadeye (407) | +0.021 | +0.404 | +0.591 |
| Gunn Point (23,236) | +0.140 | +0.307 | +0.169 |
| Roper (6,342) | +0.028 | +0.244 | +0.059 |

Mechanism check: the 1 km-grid value ≈ the **area-weighted** polygon value, not the unweighted
one. So the "signal at fine resolution" is **area-weighting + pseudoreplication** (grid cells
finer than expert polygons are not independent; n_cells ≠ independent n), driven by a few LARGE
polygons — NOT new information. Reporting fine-grid p-values would be pseudoreplicated and
indefensible. **The seductive Larrimah 1 km ρ=+0.59 is spurious.**

### Finding R2 — two legitimate but different estimands, and the answer flips between them.
- **Per-expert-unit (unweighted):** "does an expert-delineated unit's rarity predict its assessed
  value?" → weak/none across all six (−0.03…+0.14). This *reaffirms and GENERALISES V1's negative*
  to six catchments — now WITHOUT the small-n excuse: Gunn Point alone has 23,236 expert polygons
  and a full 1–5 gradient, yet land-system rarity reaches only ρ≈0.14.
- **Per-landscape-area (area-weighted):** rarity looks moderately predictive (+0.24…+0.52), but
  this is fragile (few large polygons) and grain-dependent.

### Decision D1.6 — course correction for V2's primary design
1. **Primary analysis unit = native expert polygon** (honest support; no change-of-support on the
   response; maximal independent expert judgments). The regular-grid ladder is DEMOTED from
   "primary evidence" to a **MAUP/estimand-sensitivity demonstration** (a cautionary result), never
   a source of inflated n or p-values.
2. **Report BOTH estimands explicitly** (unweighted per-unit AND area-weighted per-landscape).
   Their divergence is itself a headline methodological result: *conclusions about open-data
   biodiversity surrogates are contingent on analysis unit and weighting — a MAUP/estimand
   sensitivity most validation studies ignore.*
3. **Inference must use spatial-autocorrelation-corrected effective n** (as V1), computed among
   the expert polygons — the cell count is never the sample size.
4. The incumbent land-system-rarity surrogate carries little per-unit signal even where expert
   data is abundant → strong motivation for the finer/more-direct candidates (NVIS, SDM, DEA).
   This is the constructive core, unchanged.

**Why this is stronger, not weaker:** it replaces a fragile "finer=better" story (which a good
reviewer would destroy on pseudoreplication grounds) with (a) a robust, generalised negative on
the cheap surrogate across six catchments, and (b) a rigorous estimand/MAUP-sensitivity result —
both fully defensible.

### Remaining limitations logged
- Per-unit vs per-area estimand choice must be pre-registered before confirmatory runs (P3).
- `convertibility` no-data (water/intensive polygons: Roper 28%, Gunn Point 15% at polygon level)
  needs a declared policy (exclude vs impute) — pre-register in P3.
- Land-system rarity is intrinsically coarse (550 NT-wide land systems); it cannot resolve fine
  expert detail regardless of grid — a structural cap, not a tuning issue.
- Deep Well (6 polygons) and Larrimah (19 polygons, 2 classes) remain individually uninformative
  even at native support; they enter only via pooled/meta with spatial-corrected weights.

---

## PRE-REGISTRATION P3.PR1 — co-primary estimands (LOCKED before confirmatory runs)

**Decision (user-approved):** two **co-primary** estimands for surrogate validity, each a distinct
pre-stated question. Analysis unit = native expert polygon (D1.6).
- **E-UNIT (unweighted):** each expert polygon counts once. Question: *classification fidelity* —
  does the surrogate reproduce expert judgment unit-by-unit (protects small high-value units)?
- **E-AREA (area-weighted by unit_km2):** Question: *spatial allocation* — does the surrogate
  track value across the landscape by area?

**Multiplicity / interpretation (intersection–union; fixed in advance):**

| E-UNIT | E-AREA | Pre-registered conclusion |
|---|---|---|
| + (CI>0) | + (CI>0) | Surrogate validated (robust across estimands). |
| null | null | Surrogate not validated (robust across estimands). |
| null | + | Validity is **area-driven** (few large units); classification fidelity absent → estimand-dependent, report as the MAUP/estimand-sensitivity headline. |
| + | null | Validity is per-unit but not area-dominant (rare here). |

Rules: (i) BOTH estimands reported in every table regardless of outcome; (ii) no post-hoc
selection of a "lead" number; (iii) inference uses spatial-autocorrelation-corrected effective n
among expert polygons (V1 method), never cell counts; (iv) E-AREA additionally requires leverage/
influence diagnostics + a drop-largest-k-polygons sensitivity — if its signal is a ≤3-polygon
leverage artefact with no stability, it is demoted to a cautionary secondary (pre-specified).
Not a significance gate: when the two disagree, the conclusion is "estimand-dependent," not a win.

**Still to pre-register before P3 confirmatory runs:** convertibility no-data policy
(exclude vs impute); Weddell crosswalk handling; the spatial-CV / mixed-model specification;
the surrogate candidate set once NVIS (and later SDM/DEA) are in.

---

## P2 — NVIS v7 acquired, integrated, and critically tested

### D2.1 — NVIS acquisition + tooling
Auto-downloaded NVIS v7.0 extant MVG/MVS raster FGDB (148 MB) from the ArcGIS Online item
`/data` endpoint. The base rasterio wheel lacks the OpenFileGDB **raster** driver; rather than
destabilise the base env, warped the authoritative **v7** MVG subdataset to an NT GeoTIFF
(EPSG:3577, 100 m) using an existing conda env's GDAL 3.13 (`envs/geo`). Fully reproducible.
- **Limitation:** NVIS MVG is thematically coarse (22 native classes NT-wide). Non-vegetation
  codes {25 cleared, 27 bare, 28 sea, 99 unknown} excluded as no-data (config `NVIS_EXCLUDE`).
- **Integration:** `sig_nvis_mvg` = NT-wide MVG rarity (log-inverse native-veg area), added as a
  registry surrogate via per-catchment raster→polygon (`rasterio.features.shapes`) then the same
  area-weighted machinery as land-system rarity — identical footing, no new dependency. 96% unit
  coverage. Products rebuilt.

### Finding R2.1 — NVIS MVG rarity is a MATERIALLY BETTER significance surrogate than land-system rarity. [exploratory, strong]
Per-expert-polygon (E-UNIT), pooled over the 5 identical-scale BIORISK catchments:
**land-system rarity ρ=+0.124 → NVIS MVG rarity ρ=+0.214** (n≈29k), and NVIS wins in 5/6
catchments individually (Roper +0.03→+0.24, Wadeye +0.02→+0.51, Gunn Point +0.14→+0.21,
Weddell −0.10→+0.23; only tiny Deep Well n=6 disagrees). NVIS even edges convertibility
(+0.188) pooled. This is the **constructive counterpart to V1's negative**: a better, still-cheap
open-data significance surrogate does improve agreement with expert biodiversity value — the core
V2 hypothesis, supported.

### Finding R2.2 — but the estimand divergence is real and must be carried. [exploratory]
Under E-AREA (area-weighted) NVIS **flips sign** in Roper (−0.17), Larrimah (−0.36), Deep Well
(−0.60) while staying strongly positive in Wadeye/Gunn Point/Weddell (+0.61/+0.74/+0.43). Coherent
reading (speculation, to be tested): NVIS rarity captures the many *small* high-value units
(riparian/monsoon/wetland veg) that dominate the per-UNIT signal but are negligible by area —
which is exactly why the co-primary design (P3.PR1) is needed. NVIS is NOT a clean win under both
estimands; report both.

### Threat T2.1 — vegetation-based circularity (MUST control in P3). [flagged]
Expert BIORISK classes 4/5 are partly defined by *significant vegetation types*; NVIS is a
vegetation-type map. The NVIS–BIORISK correlation may be partly definitional (analogous to V1's
SOCS-circularity). Before any confirmatory claim, add a circularity control (e.g. partial the
significant-veg component, or test NVIS rarity within a single expert class). Do NOT claim NVIS
"works" until this is done.

### Verdict entering DEA
NVIS earns its place as a co-candidate significance surrogate (clear per-unit improvement),
carried with two honest caveats (estimand divergence R2.2; circularity T2.1). Neither confirmed
nor oversold — a strong exploratory signal that motivates the P3 confirmatory test.

### D2.2 — DEA Fractional Cover acquired + integrated
Auto-fetched `ga_ls_fc_pc_cyear_3` (median bare-soil %, 30 m, EPSG:3577, 2020) from the open DEA
S3 bucket via public HTTPS (no auth) using the DEA STAC API; mosaicked per catchment to
`veg_cover = 100 − bare_soil` (`cond_dea`, higher = more vegetated). Integrated via a rasterstats
zonal-mean registry extractor. **Limitations:** (i) single reference year (rainfall-sensitive);
(ii) 30 m cannot resolve sub-30 m expert polygons → only 47% polygon coverage (and the missing
small polygons are often the high-value ones = a value-relevant bias); (iii) it is a *condition/
greenness* proxy, not a biodiversity-*value* proxy.

### Finding R2.3 — DEA veg-cover is a POOR value surrogate. [exploratory, honest negative]
Pooled per-expert-polygon: **cond_dea ρ=+0.035** (≈ null), vs NVIS +0.214, convertibility +0.188,
land-system +0.124. It is strong only in Roper (+0.381) and reverses elsewhere (Gunn Point −0.057,
Weddell −0.033). **Reported as a negative, not salvaged.** Scientifically expected: high vegetation
cover ≠ high biodiversity value; dense common woodland scores high cover, rare sparse communities
low. DEA may still contribute as a *condition modifier* in the multivariate P3 model (rare veg *in
good condition*), but as a standalone significance surrogate it does not work. Its Roper-only
success is a cautionary catchment-specific artefact, exactly the pattern V1 warned about.

### P2 surrogate benchmarking — honest ranking (pooled E-UNIT, exploratory)
1. **NVIS MVG rarity +0.214** — beats the incumbent; the constructive positive of V2.
2. convertibility +0.188 (reference floor; not a significance surrogate).
3. land-system rarity +0.124 — the incumbent V1 significance proxy.
4. **DEA veg-cover +0.035** — null as a value surrogate; honest negative.
Carried caveats: co-primary estimand divergence (R2.2), NVIS vegetation-circularity (T2.1),
DEA single-year + coverage + condition-not-value (D2.2). None confirmed until P3 (mixed model +
spatial CV + circularity control + both estimands).

---

## PRE-REGISTRATION P3.PR2 — confirmatory spec (LOCKED before running p3_confirmatory.py)

Extends P3.PR1 (co-primary estimands). Unit = native expert polygon (D1.6). Surrogate set FROZEN
to: `sig_landsys` (incumbent), `sig_nvis_mvg` (candidate), `cond_dea` (condition modifier),
`convertibility`, `protection`. SDM deferred (only added if P3 shows a gap these cannot fill).

**PR2.1 Missing-data policy.** Pairwise deletion per surrogate (drop units with NaN in that
surrogate); NO imputation. Reported: n and coverage% for every estimate. Rationale: imputation
would fabricate surrogate values; pairwise keeps each estimand on its valid support. Convertibility
water/no-data and DEA sub-30 m gaps are therefore excluded per-surrogate, transparently.

**PR2.2 Spatial-autocorrelation correction (per catchment).** Centroid KNN(k=8) graph
(libpysal), row-standardised; Clifford–Richardson effective n from lag-1 autocorrelation of the
RANK fields of surrogate and BIORISK (V1 method, `spatial_correction.py`), clipped to [3, n_poly].
Meta-analysis variances use n_eff, never polygon counts. Rationale: expert polygons are strongly
autocorrelated; n_poly is not independent n.

**PR2.3 Pooling.** Per catchment, per surrogate, per estimand → Fisher-z of Spearman with
Bonett–Wright variance at n_eff → DerSimonian–Laird random-effects meta over the 5 BIORISK
catchments → pooled ρ, 95% CI, p, I², Q. Both estimands always reported.

**PR2.4 Co-primary verdict** per surrogate via the P3.PR1 intersection–union table (both +, both
null, or estimand-dependent). Surrogate comparison (NVIS vs incumbent land-systems): report whether
NVIS's pooled-ρ CI excludes the incumbent's point estimate under each estimand; NVIS is judged
"better" only if it does so WITHOUT relying on the circularity-suspect signal (PR2.6).

**PR2.5 E-AREA leverage guardrail.** For every E-AREA estimate, recompute after dropping the
largest 5% of polygons by area; if the sign/significance depends on ≤3 polygons, that E-AREA
result is demoted to cautionary (pre-specified in PR1).

**PR2.6 NVIS vegetation-circularity control (challenges the positive).** Two pre-specified tests,
both must be reported: (a) partial Spearman of NVIS vs BIORISK controlling for {land_sys,
convertibility} (does NVIS retain INDEPENDENT signal?); (b) restrict to the mitigable-vs-moderate
core contrast (biorisk_majority ∈ {3,4}) and re-test NVIS (does it discriminate WITHIN the range
where "significant vegetation" is the expert's own criterion, i.e. is the signal just re-reading
the expert's veg rule?). If NVIS's advantage vanishes under (a) AND (b), it is declared
circularity-driven and demoted; if it survives either, it is a genuine independent surrogate.

**PR2.7 Weddell.** Reported SEPARATELY (BioValues scheme), Spearman only; per-catchment E-UNIT is
crosswalk-invariant, E-AREA carries an interval assumption (flagged). Never pooled onto BIORISK.

**PR2.8 Interpretation discipline.** Positive results (NVIS) challenged as hard as negatives (DEA):
NVIS must survive BOTH the estimand divergence (PR2.4) and the circularity control (PR2.6) to be
called a genuine improvement. DEA's null stands unless it shows partial signal in the multivariate
control. No result is "confirmed" from a single estimand or without spatial correction.

---

## P3 MILESTONE REVIEW (top-tier reviewer hat) — results + a spatial-inference caveat

Ran `p3_confirmatory.py` → `analysis_p3/`. Headline, with positives challenged as hard as negatives:

### Confirmatory results (pooled RE meta over 5 BIORISK catchments)
| Surrogate | E-UNIT ρ [95% CI] | E-AREA ρ [95% CI] | Co-primary verdict |
|---|---|---|---|
| **NVIS MVG rarity** | **+0.265 [0.185, 0.341]** | +0.282 [−0.44, +0.78] I²=100% | **ESTIMAND-DEPENDENT** (per-unit + ; area not) |
| land-system (incumbent) | +0.071 [−0.020, +0.162] | +0.294 [0.232, 0.354] | area + but LEVERAGE-DRIVEN; per-unit null |
| convertibility | +0.198 [0.148, 0.247] | +0.059 [−0.17, +0.28] | per-unit + ; area not |
| **cond_dea (DEA)** | +0.145 [−0.169, +0.432] I²=98% | −0.036 (trivial) | **NOT VALIDATED** (honest negative confirmed) |
| protection | −0.017 (null) | −0.396 (unstable) | not validated (benchmark has no protection info) |

### Finding R3.1 — NVIS is a genuine per-unit improvement AND survives circularity. [confirmatory, defensible]
E-UNIT: NVIS +0.265 (CI excludes 0 and excludes the incumbent's +0.071), positive in 4/5 catchments
(Roper 0.24, Larrimah 0.06, Wadeye 0.51, Gunn Point 0.21; only tiny Deep Well negative).
**Circularity control (PR2.6):** partial NVIS | {land-systems, convertibility} POOLED = **+0.201
[0.112, 0.286], p<0.001**, positive per-catchment; and it discriminates within the 3-vs-4 core
(Roper 0.15, Gunn Point 0.42). So NVIS's advantage is NOT purely definitional — it carries
independent signal. This is V2's genuine constructive positive.

### Finding R3.2 — but it is ESTIMAND-DEPENDENT, and the incumbent's area-signal is a leverage artefact.
NVIS E-AREA is uninterpretable (I²=100%, sign flips Roper −0.17 / Gunn Point +0.74). The incumbent
land-system E-AREA (+0.294) looks strong but the **leverage guardrail (PR2.5) roughly halves it**
when the largest 5% of polygons are dropped (Roper 0.24→0.13, Gunn Point 0.31→0.16, Larrimah
0.52→0.10) — it is driven by a few large polygons. So neither surrogate is robust under
area-weighting. The co-primary framing earns its keep: NVIS wins per-unit, nobody wins per-area.

### Finding R3.3 — DEA null confirmed; protection null (expected).
cond_dea E-UNIT CI spans 0 with I²=98% (all-over-the-place); the tiny E-AREA −0.04 is reliable but
meaningless. DEA is not a value surrogate. Not salvaged.

### THREAT T3.1 — effective-n is OVERESTIMATED (challenge to my own positive). [important limitation]
KNN(k=8) captures only micro-scale autocorrelation among dense small polygons, so n_eff stays large
(Roper 6342→1988; Gunn Point 23236→2635) and the within-catchment p-values (0.0000) are TOO SMALL —
true long-range dependence in BIORISK is under-captured. **I do not trust the within-catchment
p-values.** The honest inference is the BETWEEN-catchment level: NVIS E-UNIT is positive in 4/5
independent landscapes and survives the circularity control — that consistency, not the tiny p, is
the evidence. Pre-registered fix for the confirmatory: replace/augment n_eff with a spatial BLOCK
BOOTSTRAP (resample contiguous polygon blocks) or a distance-band graph at an ecological range, and
treat catchment (k=5) as the replication unit. Until then, CIs are provisional.

### Other limitations logged
- Meta k=4–5 catchments → I² unstable; Deep Well (n_eff 3) and Larrimah (19) near-uninformative.
- Circularity control uses land-systems/convertibility as proxies for "significant vegetation";
  no direct significant-veg covariate available → control is reasonable but imperfect.
- Weddell (separate scheme): NVIS +0.23, convertibility +0.19, land-systems −0.10 — consistent with
  the BIORISK pattern (NVIS best), but not pooled.

### Verdict
V2 now has a defensible confirmatory story: **at the expert-unit estimand, NVIS MVG rarity is a
validated significance surrogate that beats the incumbent and survives circularity controls, but the
result is estimand-dependent and the spatial inference needs hardening (block bootstrap).** This is
a real, nuanced, publishable finding — neither oversold nor a fragile single-catchment claim.

---

## P3 HARDENED — spatial block bootstrap (T3.1 resolved). Narrative NOT overturned.

Ran `p3_blockboot.py` (10 km tiles resampled with replacement; 5/20 km sensitivity; B=2000).
The honest replication scale is now visible: **Gunn Point's 23,236 polygons = only 15 independent
10 km blocks; Wadeye 6; Larrimah 9; Deep Well 2** (dropped). Meta is effectively k=4.

### Hardened meta (10 km; robust across 5–20 km):
| Surrogate | E-UNIT ρ [95% CI] | E-AREA ρ [95% CI] | Co-primary verdict |
|---|---|---|---|
| **NVIS MVG rarity** | **+0.244 [0.149, 0.334]** | +0.348 [−0.29, +0.77] | **estimand-dependent** (per-unit ✅) |
| land-system (incumbent) | +0.085 [−0.003, +0.172] | +0.280 [0.161, 0.390] | area-only (per-unit null) |
| **convertibility** | +0.178 [0.063, 0.288] | +0.174 [0.041, 0.301] | **VALIDATED (both estimands)** |
| cond_dea (DEA) | +0.141 [−0.098, +0.364] | −0.044 (null) | NOT validated |
| protection | −0.015 (null) | −0.228 (null) | not validated |

### Effect of hardening (challenge outcome):
- **Nothing overturned.** NVIS E-UNIT held (+0.265→+0.244, CI still excludes 0, stable 5–20 km),
  and its **circularity partial held: +0.200 [0.079, 0.314], p=0.001** — NVIS's independent
  signal survives honest inference. I² dropped to 18% (block-bootstrap variances are more
  consistent than the KNN ones).
- **One result strengthened honestly:** convertibility went from E-AREA-null (KNN, I²=97%) to
  **validated under BOTH estimands** (I²=0). So convertibility is the single most robust predictor —
  echoing V1's "convertibility carries it," now shown per-unit too.
- Incumbent land-system rarity: per-unit null confirmed; its E-AREA positive persists but was
  already shown leverage-driven (R3.2).
- DEA null confirmed.

### Revised, honest confirmatory conclusion (final for P3):
Across up to 6 NT expert catchments, at the biodiversity-relevant per-expert-unit estimand:
(1) the incumbent **land-system-rarity significance proxy fails** (ρ≈0.09, CI incl. 0) — V1's
negative, generalised and hardened; (2) a **vegetation-type-rarity surrogate (NVIS) is a genuine,
circularity-robust improvement** (ρ≈0.24; partial ρ≈0.20) — V2's constructive positive; (3)
**agricultural convertibility is the most robust single predictor** (validated under both
estimands), i.e. land availability still does much of the work; (4) **remotely-sensed vegetation
cover fails** as a value surrogate; (5) all significance results are **estimand-dependent** — a
methodological caution. Effect sizes remain modest (best ρ≈0.24): open-data surrogates are
first-pass screens, not biodiversity-value maps. No narrative change was required by the hardening.

---

## P3 JOINT MODEL — final confirmatory (spatially cross-validated). Improvement challenged.

`p3_joint.py`: linear combiner of surrogates, evaluated OUT-OF-SAMPLE by spatial-block CV
(hold out catchment×10 km tiles) and leave-one-catchment-out (LOCO) transfer. Guards against
overfitting (train vs test) and pseudoreplication (block CV).

### Results (E-UNIT primary, out-of-sample):
| Model | block-CV test ρ [CI] | train ρ | overfit gap |
|---|---|---|---|
| **CORE joint** (landsys+nvis+conv+prot) | **+0.218 [0.08, 0.33]** | +0.30 | +0.08 |
| FULL joint (+DEA) | +0.196 [0.05, 0.31] | +0.28 | +0.08 |
| NVIS only (best single) | +0.127 [0.05, 0.26] | +0.22 | +0.09 |
| convertibility only | +0.061 [−0.11, +0.23] | +0.20 | +0.14 |
| land-system only | +0.066 [−0.04, +0.15] | +0.12 | +0.06 |

### Finding R3.4 — combining does NOT significantly beat the single best surrogate. [confirmatory, disciplined negative on the improvement]
Incremental value (joint − best single, block-bootstrap CI): CORE **Δρ = +0.074 [−0.109, +0.226]**
= INCONCLUSIVE; FULL +0.055 [−0.128, +0.199]. The joint model's point estimate is higher and it is
itself a validated out-of-sample screen (CI excludes 0), but with only ~4 independent catchments the
ADDED value of combining is within noise. DEA in the FULL model *reduces* skill. Overfitting is
modest (gaps ~0.08), not severe. **The improvement from combining is not confirmed — reported as
inconclusive, not as a win.**

### Finding R3.5 — best achievable out-of-sample agreement is ρ≈0.22–0.27, and it TRANSFERS.
LOCO (predict a held-out landscape): CORE joint mean +0.271, positive in ALL 5 held-out catchments
(Roper .16, Larrimah .14, Wadeye .54, Gunn Point .28, Deep Well .24); NVIS-only +0.207 (fails Deep
Well); convertibility +0.182. So the joint model generalises marginally more consistently than any
single surrogate, but the ceiling is a MODEST screening-level agreement — not a biodiversity-value
map. NVIS is the best/most-transferable single significance surrogate.

### P3 COMPLETE. Confirmatory analysis finalised; no further statistical analysis is essential.
