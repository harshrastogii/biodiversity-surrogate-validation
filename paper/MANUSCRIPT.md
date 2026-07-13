# Which open-data surrogates reproduce expert biodiversity assessment? A pre-registered multi-catchment validation in northern Australia

**Authors:** [to be completed] 
**Target journal:** *Diversity and Distributions* (Biodiversity Research / Methods)

---

## Abstract

**Aim.** Conservation planning in data-poor jurisdictions routinely substitutes open-access
spatial surrogates for direct biodiversity information, yet whether these surrogates reproduce
expert biodiversity judgement is seldom tested, and rarely against the analytical choices — spatial
unit, weighting, and scale — that can determine the answer. We ask which open-data surrogate best
reproduces independent expert biodiversity assessment, whether combining surrogates helps or
transfers to unsurveyed landscapes, and how robust the answers are to those choices.

**Location.** Northern Territory, Australia (six expert-assessed areas).

**Methods.** Using independent expert biodiversity assessments for six areas — five sharing an
identical ordinal biodiversity-risk scale (*BIORISK*, 1–5) and one (Greater Weddell) on a related
scheme analysed separately — as the benchmark, we validated five open-access surrogates —
land-system rarity, vegetation-type (NVIS) rarity, remotely-sensed vegetation cover (DEA Fractional
Cover), agricultural convertibility, and formal protection — at the native expert-polygon unit. The analysis was
pre-registered with two co-primary estimands (per-unit and per-area). Inference used a spatial
block bootstrap and random-effects meta-analysis; the leading surrogate was subjected to a
circularity control; and a joint multivariate model was evaluated out-of-sample by spatial-block
cross-validation and leave-one-catchment-out transfer.

**Results.** The commonly-used land-system-rarity surrogate did not reproduce expert value at the
per-unit level (pooled ρ = 0.085, 95% CI −0.003 to 0.172). Vegetation-type (NVIS) rarity showed the
strongest per-unit agreement (ρ = 0.244, 0.149–0.334) and retained an independent association after
controlling for land-system rarity and convertibility (partial ρ = 0.200, 0.079–0.314).
Agricultural convertibility was the only surrogate positive under both estimands; remotely-sensed
cover and protection carried no value signal. Which significance surrogate appeared to work depended
on the estimand — land-system rarity only under area-weighting, NVIS only per unit.
A joint model achieved only modest out-of-sample agreement (Spearman ≈ 0.22–0.27) and, although it
transferred positively to every held-out catchment, did not significantly outperform the single
best surrogate (incremental ρ = 0.074, −0.109 to 0.226).

**Main conclusions.** Open-data surrogates function as weak first-pass screens, not
biodiversity-value maps. At the level of expert-delineated units a vegetation-type surrogate
modestly outperforms the widely-used landform-rarity surrogate, but which surrogate appears best
depends on the analysis unit, weighting and scale — a caution for a large body of surrogate-based
planning.

**Keywords:** biodiversity surrogates; conservation planning; open data; expert assessment;
validation; modifiable areal unit problem; spatial cross-validation; northern Australia

---

## 1. Introduction

Spatial estimates of where biodiversity value is concentrated underpin systematic conservation
planning, but across much of the world's land surface — including most of northern Australia — the
species inventories, fine-scale vegetation mapping and expert assessment that such estimates ideally
draw on do not exist at the resolution planning requires. The pragmatic response has been to build
priority layers from whatever open, wall-to-wall spatial data are available — land-system and
landform maps, vegetation classifications, land-use and tenure layers, remote sensing — as
surrogates for the biodiversity information that direct survey would provide.

Two assumptions underlie this practice, and both are rarely tested. The first is that a chosen
surrogate actually reproduces the biodiversity priorities that expert assessment would assign. The
second, more subtle, is that the answer to the first does not depend on arbitrary analytical
choices — the spatial unit of analysis, whether units are weighted by area, and the grain at which
the comparison is made. Independent expert benchmarks are, by definition, scarce in the places
surrogates are used, so validations are few; and where they exist they typically report a single
correlation at a single unit and scale, leaving the robustness of the conclusion unexamined.

Here we test both assumptions directly. Northern Australia offers an unusual opportunity: the
Northern Territory Government's *Mapping the Future* program has produced independent, field-based
expert biodiversity assessments for several catchments — five on a common ordinal risk scale —
embedded in a landscape where open-data surrogates are widely proposed for development screening.
Using six such assessments, we ask a deliberately practical and testable question:

> *In a data-poor jurisdiction, how well — and via which surrogate — can open-access spatial data
> reproduce independent expert biodiversity assessment; does combining surrogates help or transfer
> to unsurveyed landscapes; and are these answers robust to the analysis unit, weighting and
> spatial scale?*

We pre-registered the analysis, adopted two co-primary estimands so that unit/weighting sensitivity
is reported rather than hidden, used spatial inference appropriate to strongly autocorrelated expert
polygons, and evaluated the multivariate combination out-of-sample and under landscape transfer.
The result is both an empirical answer for northern Australia and a transferable, honest template
for validating biodiversity surrogates elsewhere.

## 2. Materials and Methods

The full pre-registration, code and per-number provenance are archived (Data and code
availability); we summarise the confirmed design here.

### 2.1 Study area and expert benchmarks

The benchmarks are expert biodiversity assessments produced under the *Mapping the Future* program
for six Northern Territory areas (referred to as catchments for brevity): the central Roper River
catchment, Larrimah, Wadeye, Gunn Point, the NTP 3910 Deep Well area, and the Greater Weddell
subregion. Five of these (Roper, Larrimah,
Wadeye, Gunn Point, Deep Well) carry an identical ordinal *biodiversity risk* classification
(`BIORISK`: 1 = nil/highly modified; 2 = low; 3 = mitigable; 4 = moderate/sensitive-or-significant;
5 = high), assigned to expert-delineated polygons from field vegetation and fauna survey, and form
the primary pool (Table 1). The sixth, Greater Weddell, uses a distinct "biodiversity values" scheme
and is reported separately as a robustness check, never pooled.

The analysis unit is the **native expert polygon** — the polygon at which the expert assigned a
`BIORISK` class — which preserves the benchmark at its own spatial support and avoids the
change-of-support distortions that arise when expert judgement is re-aggregated to an imposed grid.

### 2.2 Open-data surrogates

Each polygon was attributed five open-access surrogates (all reprojected to GDA94 / Australian
Albers, EPSG:3577; Table 1):

- **Land-system rarity** (`sig_landsys`): the incumbent significance surrogate — the
  log-inverse of the Territory-wide area of each land system (NT Land Systems, 1:250,000/1:1,000,000),
  rescaled to [0,1] and area-weighted per unit.
- **Vegetation-type rarity** (`sig_nvis_mvg`): the direct vegetation analogue — the log-inverse
  Territory-wide area of each National Vegetation Information System v7 Major Vegetation Group
  (100 m; 22 native classes; non-vegetation classes treated as no-data).
- **Vegetation cover** (`cond_dea`): a condition/intactness proxy — 100 minus the median bare-soil
  fraction from Digital Earth Australia Fractional Cover Percentiles (Landsat, 30 m, 2020).
- **Agricultural convertibility** (`convertibility`): an area-weighted score derived from the
  Northern Territory Land Use Mapping (ALUM primary classes); water treated as no-data.
- **Formal protection** (`protection`): the fraction of the unit within the Collaborative
  Australian Protected Areas Database.

`sig_landsys`, `sig_nvis_mvg`, `cond_dea` are candidate biodiversity-value surrogates;
`convertibility` and `protection` are included as reference predictors.

### 2.3 Analysis unit and co-primary estimands (pre-registered)

Because a surrogate can agree with expert judgement per delineated unit yet not per unit area (small
high-value polygons carry equal weight in the former, negligible weight in the latter), we
pre-registered **two co-primary estimands**: **E-UNIT** (each expert polygon weighted equally) and
**E-AREA** (polygons weighted by area). Both are always reported; a surrogate is judged validated
only if positive under both, null if null under both, and *estimand-dependent* otherwise. Neither
is treated as a significance gate when they disagree; their divergence is itself a result.

### 2.4 Statistical inference

Agreement was measured by Spearman rank correlation between each surrogate and the expert `BIORISK`
class assigned to each polygon, weighting polygons either equally (E-UNIT) or by area (E-AREA).
Because expert polygons are strongly spatially autocorrelated — so their count far exceeds the
number of independent observations — we used a **spatial block bootstrap**: polygons were assigned
to contiguous 10 km tiles (with 5 km and 20 km sensitivity), and tiles were resampled with
replacement (2,000 iterations) so that whole neighbourhoods move together. Per-catchment Fisher-z
variances from the bootstrap fed a DerSimonian–Laird random-effects meta-analysis. The Deep Well
area yields only two 10 km blocks and was not estimable in the block bootstrap, so the pooled
meta rests on four catchments (and, for protection, on the two in which protected areas overlapped
the benchmark).

The leading candidate surrogate was subjected to a **circularity control**, because expert classes
4–5 are partly defined by significant vegetation and the vegetation surrogate could re-read that
criterion: (a) a partial rank correlation controlling for land-system rarity and convertibility,
and (b) restriction to the mitigable-versus-moderate (class 3-vs-4) contrast.

Finally, a **joint multivariate model** (a linear combiner of the surrogates) was evaluated
**out-of-sample** to test whether combining adds predictive value beyond the best single surrogate,
using (i) spatial-block cross-validation (holding out whole catchment × 10 km tiles) and (ii)
leave-one-catchment-out (LOCO) transfer (training on four catchments and predicting the fifth). No
catchment identifiers entered the transfer model, so it reflects application to an unsurveyed area.
Out-of-sample skill was Spearman(predicted, observed) on held-out data; incremental value (joint
minus best single) carried a block-bootstrap confidence interval; the train–test gap indexed
overfitting. All analyses used fixed seeds and are reproducible from the archived scripts.

## 3. Results

### 3.1 The incumbent land-system-rarity surrogate does not reproduce expert value

At the per-expert-unit estimand, land-system rarity showed no meaningful agreement with expert
`BIORISK` (pooled ρ = 0.085, 95% CI −0.003 to 0.172; Table 2, Figure 2), and this was stable across
tile sizes (ρ = 0.071–0.085 at 5–20 km). It was positive under area-weighting (ρ = 0.280,
0.161–0.390), but this apparent signal was substantially leverage-driven: dropping the largest 5%
of polygons by area roughly halved it in most catchments (Roper 0.24→0.13; Gunn Point 0.31→0.16;
Larrimah 0.52→0.10; the exception was Wadeye, which fell only from 0.40 to 0.33). Land-system rarity
is therefore, at best, an area-scaled correlate rather than a per-unit predictor of expert
biodiversity value.

### 3.2 Vegetation-type (NVIS) rarity is a modest but genuine improvement

Vegetation-type rarity showed the strongest per-unit agreement of any candidate surrogate (pooled
ρ = 0.244, 0.149–0.334; positive in four of five catchments), robust to tile size (0.244–0.270).
Critically, it survived the circularity control: after partialling out land-system rarity and
convertibility it retained an independent association (partial ρ = 0.200, 0.079–0.314, p = 0.001;
positive in every estimable catchment though heterogeneous in magnitude, I² ≈ 70%), and it
discriminated `BIORISK` within the pure class-3-vs-4 contrast (e.g. Roper 0.15; Gunn Point 0.42). Its advantage over land-system rarity is thus not a definitional artefact. However, its agreement
was estimand-dependent: under area-weighting it was heterogeneous and indistinguishable from zero
(ρ = 0.348, −0.29 to 0.77; I² = 91%) — the mirror image of land-system rarity, which was positive
only under area-weighting.

### 3.3 Convertibility is the most robust reference predictor; cover and protection carry no signal

Agricultural convertibility was the only surrogate positive under both estimands (E-UNIT ρ = 0.178,
0.063–0.288; E-AREA ρ = 0.174, 0.041–0.301), consistent with land availability tracking much of the
apparent surrogate–expert agreement. Remotely-sensed vegetation cover did not reproduce expert value
(E-UNIT ρ = 0.141, −0.098 to 0.364; highly heterogeneous, I² = 83%; strongly positive only in
Roper), and formal protection carried no value signal (ρ ≈ 0, as expected given the benchmark
contains no protection information; protection was estimable in only the two catchments where
protected areas overlapped the benchmark).

### 3.4 Conclusions depend on unit, weighting and scale

The three candidate significance/condition surrogates changed rank and even sign between the two
co-primary estimands (Figure 3): NVIS rarity was best per-unit but null per-area; land-system rarity
was null per-unit but positive (leverage-driven) per-area; vegetation cover was null under both.
Point estimates were stable across 5–20 km blocks, but the honest replication scale is
small — Gunn Point's ~23,000 expert polygons correspond to only 15 independent 10 km blocks, Wadeye
to 6 — so per-catchment inference is weak and the multi-catchment meta is the appropriate level.

### 3.5 Combining surrogates: modest transfer, no confirmed gain over the best single surrogate

Out-of-sample (spatial-block cross-validation, E-UNIT), the joint model was a valid but weak screen
(ρ = 0.218, 0.08–0.33), exceeding the best single surrogate (NVIS: ρ = 0.127, 0.05–0.26) in point
estimate only; the incremental value of combining was not distinguishable from zero (Δρ = 0.074,
−0.109 to 0.226). Adding vegetation cover reduced skill. Overfitting was modest (train–test gap
≈ 0.08). Under leave-one-catchment-out transfer the joint model predicted every held-out landscape
positively (mean ρ = 0.271; range 0.14–0.54) and slightly more consistently than NVIS alone (mean
0.207, which failed on Deep Well). The strongest out-of-sample agreement we obtained between open-data
surrogates and expert assessment was therefore modest (ρ ≈ 0.22–0.27), and combining did not
demonstrably improve on a single well-chosen surrogate.

The Greater Weddell area (separate scheme; not pooled) was consistent with the pooled pattern: NVIS
rarity showed the strongest agreement (ρ = 0.23), convertibility next (0.19), land-system rarity
none (−0.10), vegetation cover none (−0.03).

## 4. Discussion

Across six independent expert assessments, open-access spatial surrogates reproduced expert
biodiversity judgement only weakly, and which surrogate did best depended on how the question was
posed. Three findings are robust. First, the **land-system/landform-rarity surrogate — among the
most widely used low-cost biodiversity proxies — did not reproduce expert value at the level of
expert-delineated units**; its area-weighted signal was driven by a few large polygons. Second, a
**vegetation-type-rarity surrogate (NVIS) did modestly better and, unlike the incumbent, carried an
association that persisted after controlling for land-system rarity and convertibility and that
discriminated expert classes even within the mitigable-versus-moderate contrast** — so its advantage
is not merely a restatement of the incumbent surrogates or of land availability, though the control
is indirect (Section 4.1). Third,
**agricultural convertibility remained the most consistent correlate**, suggesting that part of any
surrogate's apparent success may reflect where land is available as much as where biodiversity is.

Two cautions follow. The first is methodological: **conclusions were estimand- and scale-dependent.**
A surrogate that appears predictive when landscape area is the currency can be uninformative when
each expert unit is the currency, and vice versa. Because small, high-value units (riparian zones,
groundwater-dependent and significant-vegetation patches) are often precisely those a screen must
not miss, the per-unit estimand is the more conservative and, we argue, the more appropriate default
for biodiversity screening — but reporting both is essential, and single-estimand validations should
be read with this in mind. The second is practical: **the agreement achieved was weak
(ρ ≈ 0.2–0.3), and combining surrogates did not reliably improve it.** Open-data surrogate layers
are defensible as first-pass screening tools with mapped uncertainty; they are not biodiversity-value
maps and should not be presented as such.

That said, the news is not wholly negative. A better-grounded, still-cheap surrogate (vegetation-type
rarity) outperformed the incumbent and transferred positively to every held-out landscape, indicating
that surrogate *choice* matters and that open data can support cautious cross-landscape screening
where no survey exists.

### 4.1 Limitations

Our inference is bounded in three ways. (i) **Effective replication is small**: although the expert
benchmarks contain tens of thousands of polygons, strong spatial autocorrelation reduces these to a
few independent blocks per catchment and to five `BIORISK` catchments overall (four in the pooled
meta), so effect sizes are estimated with wide uncertainty and between-catchment heterogeneity is
poorly resolved. Larrimah is
individually uninformative (19 polygons, two classes), and Deep Well — with only two 10 km blocks —
is not estimable in the block bootstrap and drops out of the pooled meta entirely; the pooled
estimates therefore rest on four catchments (two for protection). This exclusion is driven by block
count, not by result, and applies uniformly to all surrogates; we note nonetheless that Deep Well
(six polygons) is the one catchment in which the NVIS estimate is negative and the land-system
estimate positive, so its removal modestly favours the NVIS–land-system contrast — a contrast that,
however, is anchored by the two large catchments (Roper, Gunn Point) in which NVIS also leads.
(ii) **Single jurisdiction**: all benchmarks are from one program in the Northern Territory; external
validity to other regions, biomes and assessment protocols is untested. (iii) **Surrogate and
benchmark constraints**: the vegetation surrogate is thematically coarse (major groups); the cover
surrogate is a single year; the circularity control, lacking a direct significant-vegetation
covariate, used related predictors as proxies. None of these bounds the direction of the conclusions,
but each bounds their strength.

### 4.2 Future work

The improvement path is clear and was deliberately not pursued here to keep claims within the
confirmed evidence: finer vegetation subgroups, modelled threatened-species habitat from occurrence
data, and multi-year condition composites are natural next candidate surrogates; and replication in
a second jurisdiction would test the one assumption this study cannot — geographic generality.

## 5. Conclusion

Open-access spatial surrogates reproduce independent expert biodiversity assessment only weakly in
data-poor northern Australia, and the conclusion one draws depends on the spatial unit, weighting and
scale of analysis. At the level of expert-delineated units, a vegetation-type-rarity surrogate
modestly and genuinely outperforms the widely used land-system-rarity surrogate and survives
circularity controls, but no surrogate — alone or combined, and under either weighting — rises above
the level of a weak first-pass screen. Transparent, pre-registered,
multi-benchmark validation with explicit estimands is what makes these limits visible, and we
recommend it as standard before open-data surrogates are used to guide conservation decisions.

## Tables

**Table 1. Expert benchmarks and open-data surrogates.**

| Expert benchmark (BIORISK) | Approx. area (km²) | Expert polygons | Classes present |
|---|---|---|---|
| Roper | 17,254 | 6,342 | 1,3,4,5 |
| Gunn Point | 713 | 23,315 | 1–5 |
| Larrimah | 486 | 19 | 3,4 |
| Wadeye | 178 | 412 | 2,4,5 |
| Deep Well (NTP 3910) | 22 | 6 | 2,3,4 |
| Greater Weddell (separate scheme) | 394 | 20,481 | 1–5 |

| Surrogate | Source | Native resolution | Definition |
|---|---|---|---|
| Land-system rarity | NT Land Systems | 1:250k / 1:1M | log-inverse NT-wide land-system area |
| Vegetation-type rarity | NVIS v7 MVG | 100 m | log-inverse NT-wide MVG area (native classes) |
| Vegetation cover | DEA Fractional Cover | 30 m | 100 − median bare-soil % (2020) |
| Convertibility | NT Land Use (ALUM) | polygon | area-weighted ALUM-class score |
| Protection | CAPAD (terrestrial) | polygon | fraction protected |

**Table 2. Pooled hardened agreement (spatial block bootstrap, DerSimonian–Laird meta over the
estimable BIORISK catchments — four; Deep Well, with two 10 km blocks, was not estimable, and
protection was estimable in two), both co-primary estimands.** ρ = Spearman; 95% CI from the block
bootstrap.

| Surrogate | E-UNIT ρ [95% CI] | E-AREA ρ [95% CI] | Co-primary verdict |
|---|---|---|---|
| Vegetation-type (NVIS) rarity | 0.244 [0.149, 0.334] | 0.348 [−0.29, 0.77] | estimand-dependent (per-unit only) |
| Land-system rarity | 0.085 [−0.003, 0.172] | 0.280 [0.161, 0.390] | per-unit null; area leverage-driven |
| Convertibility | 0.178 [0.063, 0.288] | 0.174 [0.041, 0.301] | validated (both) |
| Vegetation cover (DEA) | 0.141 [−0.098, 0.364] | −0.044 [−0.166, 0.079] | not validated |
| Protection | −0.015 [−0.073, 0.043] | −0.228 [−0.489, 0.070] | not validated |
| NVIS partial (\| land-system, convertibility) | 0.200 [0.079, 0.314] | — | independent signal retained |

**Table 3. Joint multivariate model, out-of-sample (spatial-block cross-validation, E-UNIT) and
leave-one-catchment-out transfer.**

| Model | Block-CV ρ [95% CI] | Train ρ | LOCO transfer (mean; range) |
|---|---|---|---|
| Core joint (land-system + NVIS + convertibility + protection) | 0.218 [0.08, 0.33] | 0.30 | 0.271 (0.14–0.54) |
| Full joint (+ vegetation cover) | 0.196 [0.05, 0.31] | 0.28 | — |
| NVIS only (best single) | 0.127 [0.05, 0.26] | 0.22 | 0.207 (0.00–0.51) |
| Convertibility only | 0.061 [−0.11, 0.23] | 0.20 | 0.182 |
| Incremental value (core joint − best single) | Δρ = 0.074 [−0.109, 0.226] | — | inconclusive |

## Figure captions

**Figure 1.** Study area: the six *Mapping the Future* expert biodiversity assessments within the
Northern Territory, with their extents and `BIORISK` class composition.

**Figure 2.** Surrogate benchmarking. Per-catchment and pooled (random-effects meta) Spearman
agreement of each surrogate with expert `BIORISK` at the per-expert-unit estimand, with spatial
block-bootstrap 95% intervals. Vegetation-type rarity is highest; land-system rarity overlaps zero.

**Figure 3.** Estimand and scale sensitivity. (a) Pooled agreement under the two co-primary
estimands (per-unit vs per-area) for each surrogate, showing rank/sign changes; (b) robustness of
the per-unit estimates to block size (5, 10, 20 km).

**Figure 4.** NVIS circularity control. Per-catchment raw agreement, partial agreement controlling
for land-system rarity and convertibility, and agreement restricted to the class-3-vs-4 contrast;
the independent signal is retained.

**Figure 5.** Joint model and transfer. Out-of-sample (spatial-block CV) agreement of single vs
joint models, and leave-one-catchment-out transfer skill per held-out catchment; combining does not
significantly exceed the best single surrogate.

## Data and code availability

The full pre-registration, analysis scripts (harmonisation, block-bootstrap meta, circularity
control, joint model with spatial cross-validation), and a per-number provenance log regenerate every
reported value from the archived inputs; seeds are fixed. Expert benchmarks and open-data surrogates
are open Northern Territory and Australian Government layers (Table 1); sources and licences are
documented in the repository.

## References

*[To be completed with co-authors. Confirmed benchmark source: Buckley, K., Leiper, I., Nano, C.,
Wedd, D. & Wilson, D. (2024) Mapping the Future — Biodiversity assessment of the central Roper River
catchment. Technical Report 14/2024, DEPWS, NT Government, Darwin; plus the five further Mapping the
Future assessments (Larrimah, Wadeye, Gunn Point, NTP 3910/Deep Well, Greater Weddell). Standard
methodological citations to be added: systematic conservation planning; biodiversity surrogacy;
modifiable areal unit problem; spatial cross-validation / spatial autocorrelation; DerSimonian–Laird
meta-analysis; NVIS; Digital Earth Australia Fractional Cover. Placeholders flagged for co-author
input.]*
