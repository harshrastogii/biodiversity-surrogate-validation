# Pre-submission panel review — consolidated findings and plan

*Date: 2026-10-03. Reviewed state: commit `59b2de8` (Version 2, "supervisor review" draft).*

Five independent reviewers looked at the manuscript, code, frozen outputs and literature:

1. a statistical-methods reviewer;
2. a fact-checker covering every number, reference and figure;
3. a mock "Reviewer 2" (conservation biogeographer);
4. a literature and novelty reviewer;
5. a publishing strategist.

Every finding listed as **verified** below was re-computed directly from
`data/processed/harmonized_polygon.parquet`. The raw NT layers could not be downloaded in the
review environment, so anything that needs polygon coordinates has to be re-run locally (Section 5).

---

## 1. Bottom line

The project is careful, transparent and unusually self-critical. The research log is a real asset.
**But the current draft should not be submitted.** Three data-handling artefacts and two inference
problems change headline numbers. Several of the paper's conclusions do not survive defensible
alternative analysis choices:

| Headline claim in the draft | Status after review |
|---|---|
| Land-system rarity "fails per unit" (ρ = 0.085) | **Fragile.** Driven by sub-hectare sliver polygons. At polygons ≥ 1 ha, Gunn Point land-system ρ = 0.285 > NVIS 0.203, and Wadeye goes 0.02 → 0.20 |
| NVIS "genuine, circularity-robust improvement" | **Partly.** Robust per unit and as AUC for classes ≥ 4. But it is carried by a few rare vegetation groups: one tidal (likely mangrove) class is BIORISK 4 in 1,671 of 1,674 Gunn Point polygons. Dropping the rarest groups flips Gunn Point to −0.04 and Weddell to −0.04. NVIS is *worse* than land-system for class 5 at Gunn Point (AUC 0.46 vs 0.69). The circularity meta was k = 3, not 4 |
| Convertibility "validated under both estimands" | **Not supported.** Wadeye convertibility is a constant (0.1 ± 1e-17). Its ρ came from floating-point noise but entered the meta. In Roper the signal is entirely "already-modified land = BIORISK 1" (ρ 0.21 → 0.02 without class 1) |
| Combining "does not significantly beat" NVIS (Δρ = 0.074) | **Invalid CI.** The two bootstraps were unpaired, the samples differed, and 0.074 is a median, not the point difference (0.091). The paired re-test is in `p4_revision.py` and may flip this |
| DL random-effects CIs over k = 3–4 catchments | **Too narrow.** HKSJ / modified-HKSJ is the current standard. Approximate recomputation widens NVIS to about [0.02, 0.42] and pushes convertibility and the circularity partial across zero |
| "Pre-registered" (title, abstract) | **Not defensible.** The plan was written after an exploratory look at the same data, the inference method changed after the confirmatory run, and nothing was publicly time-stamped. Now changed to "pre-specified", with a deviations section |

**The opportunity.** These fragilities are themselves the most publishable result. *Which*
surrogate "wins" depends on several things:
- the analysis unit;
- the minimum polygon size;
- the weighting and rank definition;
- the decision threshold (class ≥ 4 versus class 5);
- a handful of vegetation classes.

Grantham et al. (2010) showed that surrogate effectiveness depends on the test *metric*, and Gould et
al. (2025) showed analytical flexibility in ecology generally. We found **no study that has run a
formal multiverse (specification-curve) validation of biodiversity surrogates against an independent
expert benchmark**. Section 3 explains how to reframe around it.

---

## 2. Verified findings (ranked)

### Fatal or major — change results

**F1. Floating-point ties manufacture correlations.**
- Area-weighted overlays store "0.1" as 0.0999999999999999, 0.1 and 0.1000000000000002.
- `nunique()` treats these as distinct and Spearman ranks them.
- Affected values:
  - Wadeye convertibility (constant): reported 0.096 and 0.267.
  - Deep Well NVIS: reported −0.254, true 0.000 (also discussed in Limitations and plotted in Figs 2–3).
  - Deep Well land-system and convertibility: variation is only 1e-5 slivers.
  - Gunn Point NVIS: 0.206 → 0.216.
  - Roper convertibility E-AREA: 0.179 → 0.090.
- **Fixed:** `config.load_polygons()` rounds every surrogate to 6 d.p. All analysis scripts now use it.

**F2. Sliver polygons dominate the per-unit estimand.**
- In Gunn Point the median polygon is 203 m², and 85% of polygons are smaller than one 100 m NVIS pixel.
- In Roper, 43% of polygons are smaller than 100 m².
- Restricting to polygons ≥ 1 ha changes the ranking (above).
- The draft's rationale that "E-UNIT protects small high-value units" does not hold for topology fragments.
- **Added:** minimum-mapping-unit sensitivity (0, 0.1, 1 ha) in the multiverse (R6).

**F3. Convertibility re-reads land modification.**
- The ALUM classes 3–5 (dryland, irrigated, intensive) score low, and those polygons are mostly expert class 1 ("nil / highly modified").
- Roper, without class 1: ρ 0.21 → 0.02. Gunn Point 0.20 → 0.18. Weddell 0.20 → 0.11.
- Water (ALUM 6 = no-data) removes about 34% of class-4 polygons in Roper and Gunn Point, so convertibility is tested on a wetland-depleted sample.
- **Added:** R4 (exclude class 1).
- **Text:** drop "land availability", and describe convertibility as a modification/intactness proxy.

**F4. NVIS signal is concentrated in rare vegetation groups.**
- These are coastal, wetland and riparian MVGs that the experts' own rules treat as sensitive.
- The partial correlation controls for land-system rarity and convertibility, but they are not proxies for those rules.
- The 3-vs-4 test is where the vegetation rule operates, so it cannot refute circularity. Gunn Point 3-vs-4 (0.42) exceeding raw ρ (0.21) is what circularity predicts.
- **Added:** R5, leave-one-rare-group-out.
- **Text:** reframe as "NVIS reproduces the experts' vegetation-sensitivity rules". That is useful for screening, but it is not independent evidence.

**F5. Joint-model Δρ CI was unpaired.**
- Independent bootstrap draws, different complete-case sets (23,966 vs 29,444 rows) and different CV folds per model.
- In addition, the pooled-across-catchment Spearman mixes between-catchment differences: Gunn Point is about 80% of rows.
- **Added:** R2, a paired comparison on the same rows and same folds, with stratified tile bootstrap, reported both pooled and within-catchment.

**F6. Small-k meta-analysis.**
- DerSimonian–Laird Wald CIs with k = 3–4 under-cover. Report HKSJ and modified-HKSJ (IntHout et al. 2014; Röver et al. 2015).
- Per-catchment variances were never saved; they are now (`analysis_p4/per_catchment_z.csv`).
- **Added:** R1.

**F7. Circularity meta silently dropped Larrimah (k = 3).**
- `partial_boot` did not filter NaN bootstrap replicates, so Larrimah's variance became NaN.
- Larrimah's partial (0.051) is the smallest, so dropping it inflated the pooled 0.200.
- **Fixed** in `p3_blockboot.py`.

**F8. Area-weighted "Spearman" used unweighted ranks.**
- With proper area-weighted mid-ranks, Gunn Point land-system E-AREA goes 0.309 → 0.006, and NVIS goes 0.737 → 0.570.
- **Added:** a weighted-ECDF rank correlation in R6.

**F9. Leverage guardrail applied asymmetrically.**
- It was used to demote land-system E-AREA only.
- The same rule flips NVIS E-AREA in Roper (−0.17 → +0.21) and Larrimah (−0.36 → +0.32), and collapses convertibility in Roper (0.18 → −0.02).
- **Text:** report it for every surrogate.

**F10. Single-surrogate LOCO is not a transfer test.**
- A linear one-predictor model gives held-out ρ = ± the raw within-catchment ρ.
- Only the joint model's weight transfer is tested by LOCO.
- **Text and R2** now say so.

### Minor and factual (fact-check)

**Fixed now:**
- Gunn Point area: 704 km² (not 713).
- DEA citation: Lymburner (2021), *GA Landsat Fractional Cover Percentiles Collection 3*, doi:10.26186/150570.
- "Transferred positively to every held-out landscape" was attributed to NVIS. Only the joint model did that; NVIS was 0 at Deep Well.
- "Six independent assessments": they come from one program, so they are not independent.
- README: removed "*et al.*", and corrected the reproducibility claim (the parquet has no coordinates).
- ORCID added to CITATION.cff.

**To fix during the rewrite:**
- Figure 1b uses the BIORISK legend for Weddell, which is on a different scheme.
- Figure 2 caption promises per-catchment CIs that are not drawn, and plots the Deep Well artefact.
- Figure 3 needs "n.e." labels and k = 3/4.
- Use 3 decimals throughout (Table 2 has "[−0.29, 0.77]").
- Out-of-sample protection was significantly *negative* (−0.156); report it.
- Gunn Point counts appear as 23,315, 23,236 and 23,498 in different places. Footnote which is which.
- Gunn Point has only one class-2 polygon, so "1–5" overstates the class range.
- `protection` and `iucn_frac` are identical columns.

**Unverified, check by hand:**
- **BIORISK class definitions** being identical across all five areas. This item is still open in the log, and it is needed to justify pooling.
- The **Gunn Point** dataset title and URL.
- The **Deep Well** URL slug ("…assessment-study-of…").
- The CAPAD vintage actually used.

---

## 3. Recommended reframing (decision for the author)

**Option A — corrected original.** Keep the framing, fix the artefacts, and soften the claims.

Expected outcome: a solid regional paper. The mock reviewer's verdict on the current framing was
"reject, resubmission encouraged / major revision" at *Diversity and Distributions*. Better fits are
*Ecological Indicators*, *Conservation Science and Practice* and *Global Ecology and Conservation*,
all Q1.

**Option B — recommended: "multiverse validation".** Make the analyst-choice dependence the
central result.
- **Working title:** *"Which surrogate wins depends on the analyst: a multiverse validation of open-data
  biodiversity surrogates against government expert assessments in northern Australia."*
- **Core:**
  1. R6 specification curve, with metric/estimand × minimum mapping unit × class-1 exclusion, extendable to tile size and NVIS group exclusion.
  2. Decision-relevant screening metrics (R3): threshold-specific AUC and top-20%-area capture.
  3. Mechanism analyses that explain *why* verdicts flip: slivers (F2), modification (F3) and vegetation rules (F4).
- **Message:** single-specification surrogate validations, which make up most of the literature, can
  reach opposite conclusions from the same data. Validation should report a specification curve and
  decision-threshold metrics.
- **Why it is stronger:**
  - It generalises beyond the NT.
  - It uses all the work already done.
  - It turns the review's criticisms into the contribution.
  - It speaks to the analytical-flexibility literature (Gould et al. 2025, *BMC Biology*), which is current in ecology.
- **Targets:** *Diversity and Distributions*, *Ecological Indicators*, *Methods in Ecology and Evolution* (if
  the template is packaged as a tool), and *Conservation Biology*.

**Option C — B plus global screening layers (highest impact, more work).** Add the open global and
national layers now used for corporate nature-risk screening under TNFD/SBTN:
- Jung et al. 2021 "areas of global importance" (Zenodo, CC-BY-SA).
- Human Footprint (Dryad).
- Venegas-Li et al. 2026 Australian industrial footprint / ecological intactness (ESSD, CC-BY).
- Biodiversity Intactness Index (BII; NHM, non-commercial use).
- CSIRO HCAS condition (CC-BY), which would replace single-year DEA.

The literature reviewer found **no precedent** for testing these layers against field-based government
expert polygons. STAR and KBAs have licensing limits. If you do this, **lodge a genuine OSF
secondary-data pre-registration before extracting the new layers**. That would make "pre-registered"
true for this part. It could also be a second paper.

Honest caveat: no reviewer or tool can guarantee Q1 acceptance. Desk-rejection rates at these
journals are about 30–40%. Option B materially improves the odds because the claim becomes general
and robust, rather than regional and fragile.

---

## 4. Literature to add (verified titles; resolve † DOIs by hand)

The draft has 22 references; Q1 papers typically have 40–60. Must-cites:

- **Surrogate effectiveness and congruence:**
  - Westgate et al. 2014 *Nat Commun* 5:3899 (10.1038/ncomms4899)
  - Grantham et al. 2010 *PLoS ONE* 5:e11430 (10.1371/journal.pone.0011430)
  - Ferrier 2002 *Syst Biol* 51:331 (10.1080/10635150252899806)
  - **Oliver et al. 2004 *Ecol Appl* 14:485, "Land systems as surrogates for biodiversity"** (10.1890/02-5181). This is the direct precedent for your incumbent surrogate.
  - Lindenmayer et al. 2015 *Sci Total Environ* 538:1029
  - Hess et al. 2006 *Biol Conserv* 132:448 †
  - Beier et al. 2015 and Lawler et al. 2015 *Conserv Biol* 29 ("conserving nature's stage")
  - Trakhtenbrot & Kadmon 2005
  - Barton et al. 2014 *J Appl Ecol*
  - Dreiss et al. 2024 *BioScience*
- **Scale and spatial methods:**
  - Dungan et al. 2002 *Ecography*
  - Warman et al. 2004 †
  - Dormann et al. 2007
  - Valavi et al. 2019 (blockCV)
  - Ploton et al. 2020 *Nat Commun*
  - Meyer & Pebesma 2022 *Nat Commun*
  - Wadoux et al. 2021 *Ecol Model*
- **Small-k meta-analysis:**
  - IntHout et al. 2014 *BMC Med Res Methodol* 14:25
  - Röver et al. 2015 *BMC Med Res Methodol* 15:99
- **Expert judgement:**
  - Martin et al. 2012 *Conserv Biol*
  - Burgman et al. 2011 *PLoS ONE*
  - Hemming et al. 2018 *MEE*
  - Johnson & Gillingham 2004 †
  - Pearce et al. 2001
- **Northern Australia:**
  - Woinarski et al. 2007 *The Nature of Northern Australia*
  - Woinarski et al. 2011 *Conserv Lett*
  - Stoeckl et al. 2015
  - **McGinley, Edwards & Garnett 2025 *Australas J Environ Manag*** (CDU; NT conservation-planning gaps)
  - CSIRO NAWRA 2018 and Roper River WRA 2023
- **Screening metrics, analytical flexibility and open science:**
  - Lobo et al. 2008
  - Gould et al. 2025 *BMC Biology* ("Same data, different analysts")
  - Simonsohn et al. 2020 (specification curve)
  - Steegen et al. 2016 (multiverse)
  - Parker et al. 2016/2019
  - Nosek et al. 2018
  - van den Akker et al. 2021 (pre-registering secondary data)
- **Global layers (Option C):**
  - Mair et al. 2021
  - Jung et al. 2021
  - Newbold et al. 2016
  - Venter et al. 2016
  - Williams et al. 2020
  - Venegas-Li et al. 2026 *ESSD*
  - Hawkins et al. 2024
  - Harwood et al. 2016 (HCAS)

---

## 5. What to run locally (raw data needed)

From the repository root, on the machine that has the raw NT layers:

```bash
python scripts/export_centroids.py   # once; then commit data/processed/polygon_centroids.parquet
python scripts/p3_confirmatory.py    # regenerates analysis_p3/ with rounding fix
python scripts/p3_blockboot.py       # regenerates hardened_* (now k=4 circularity if Larrimah estimable)
python scripts/p3_joint.py
python scripts/p4_revision.py        # analysis_p4/: R1 HKSJ, R2 paired joint, R3 screening,
                                     # R4 modification, R5 NVIS groups, R6 multiverse + spec-curve figure
```

Then commit `analysis_p3/`, `analysis_p4/` and `data/processed/polygon_centroids.parquet`, and push.
After that the whole analysis is re-runnable from the repository alone, and the manuscript can be
rewritten against the regenerated numbers.

---

## 6. Publishing roadmap (solo early-career author)

APCs and agreements were checked via web search, October 2026; confirm on the official pages.

1. **Authorship (now).**
   - CDU's *Authorship of Research Output Procedure* requires ≥ 2 of: conception/design; data with intellectual judgement; contribution of knowledge; analysis/interpretation; drafting/critical revision.
   - If your supervisor meets this, they must be a co-author. If not, acknowledge them with permission.
   - Get written supervisor sign-off either way, because CDU's name is on the paper.
   - Record CRediT roles.
   - Sole authorship is legitimate if the work is entirely yours.
2. **Decide the framing** (Section 3), then re-run (Section 5) and rewrite.
3. **Archive.**
   - Make the repository public.
   - Connect it to Zenodo, then create a GitHub release (e.g. `v2.0-submission`). That mints a citable DOI.
   - Put the DOI in Data/Code Availability.
   - Zenodo allows CC-BY. Dryad (free via D&D) is CC0 only.
4. **Optional:**
   - An EcoEvoRxiv preprint gives a dated priority claim and DOI, at the cost of slightly weaker anonymity.
   - An OSF project to hold materials. If you do Option C, lodge an OSF pre-registration *before* extracting the new layers.
5. **Format for the first-choice journal.**
   - *Diversity and Distributions* is double-anonymous: a separate title page plus an anonymised manuscript, with no name, ORCID or GitHub handle in the main file.
   - Structured abstract ≤ 300 words (Aim, Location, Methods, Results, Main conclusions).
   - Main text ≤ 6,000 words; the current text is about 2,500, so there is room for methods detail.
   - APA 7 references; use Zotero with the journal style.
   - Biosketch of 30–100 words.
   - Data Availability Statement is mandatory.
6. **Cost.**
   - D&D is gold open access, with an APC of about USD 3,770.
   - The CAUL–Wiley agreement covers CDU **staff/HDR** corresponding authors with an @cdu.edu.au address, under a consortium-wide cap.
   - **Ask the CDU Library whether your student address and status qualify.** If not, request the D&D no-funding waiver in the cover letter.
   - Hybrid journals (Biological Conservation, J Applied Ecology, Austral Ecology) are free to publish in under CAUL for eligible authors.
7. **Cover letter (1 page):**
   - The question and finding in two sentences.
   - Why it matters beyond the NT.
   - Fit to the journal.
   - Declarations, DOIs and any waiver request.
   - No hype.
8. **Suggested reviewers.**
   - Choose 3–5 active authors you cite, mixed in country and career stage.
   - Never your supervisor, CDU colleagues, recent co-authors or the NT data producers.
9. **Revisions.**
   - Reply point by point and politely.
   - Make every reasonable change; disagree only with evidence.
10. **Typical timeline.** 6–12 months to acceptance. Each rejection and resubmission adds 2–4 months.
11. **Courtesy.** Tell the NT Government *Mapping the Future* team (the data producers), and acknowledge them.

**Ranked targets.** All Q1 per SJR/Scopus (2025); verify quartile in your field's category.

| Option | Primary target | Backups |
|---|---|---|
| B | Diversity and Distributions | Ecological Indicators, Conservation Science and Practice, then Biological Conservation |
| A | Ecological Indicators or Conservation Science and Practice | Global Ecology and Conservation |

Q2 safety nets: Austral Ecology and Pacific Conservation Biology.

---

## Sources (web-verified during review)

- Grantham et al. 2010: https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0011430
- Gould et al. 2025, BMC Biology: https://eprints.gla.ac.uk/347669
- STAR vs expert questionnaire, 2025: https://link.springer.com/article/10.1007/s10531-025-03092-z
- Venegas-Li et al. 2026: https://essd.copernicus.org/articles/18/2179/2026/
- Jung et al. 2021 data: https://zenodo.org/records/5006332
- HCAS: https://research.csiro.au/biodiversity-knowledge/projects/hcas
- D&D author guidelines: https://onlinelibrary.wiley.com/page/journal/14724642/homepage/forauthors.html
- CAUL–Wiley agreement: https://caul.libguides.com/read-and-publish/wiley
- CDU open-access agreements: https://libguides.cdu.edu.au/openaccesspublishing/agreements
- CDU authorship procedure: https://policies.cdu.edu.au/view-current.php?id=34
- IntHout et al. 2014: https://pmc.ncbi.nlm.nih.gov/articles/PMC4015721/
- Röver et al. 2015: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4647507/
- McGinley et al. 2025 (CDU): https://www.cdu.edu.au/news/conservation-planning-good-biodiversity-business
