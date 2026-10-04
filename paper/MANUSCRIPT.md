# Analytical choices decide which open-data surrogate agrees with expert biodiversity assessment: a multiverse validation in northern Australia

## Abstract

**Aim.** Conservation planning in data-poor regions uses open spatial layers as biodiversity
surrogates, and validations usually report one statistic from one set of analysis choices. We asked
whether the answer to "which surrogate agrees best with expert assessment?" holds when those choices
change within a defensible range.

**Location.** Northern Territory, Australia.

**Methods.** We compared five open-data surrogates (land-system rarity, vegetation-type rarity from
the National Vegetation Information System, satellite vegetation cover, land-use convertibility and
formal protection) with government expert biodiversity-risk classes for 26,831 polygons in five
assessment areas and 20,481 polygons in a sixth area on a separate scale. We evaluated 30
specifications (five agreement metrics × three minimum polygon sizes × with or without
already-modified land) using a 10 km spatial block bootstrap and small-sample random-effects
meta-analysis.

**Results.** The surrogate that scored highest changed with the specification. Vegetation-type rarity
led on per-polygon rank correlation (0.22–0.51 in the three large areas) and on separating high-risk
polygons (class ≥ 4) from the rest. Land-system rarity led under area weighting in two of four areas
and in identifying the highest class in the two most finely mapped assessments (AUC 0.69
and 0.61 versus 0.46 and 0.47). Vegetation-type rarity scored highest in 21 of 30 specifications and
land-system rarity in 9, but their paired difference excluded zero in only one. Three mechanisms
explained the reversals: 76–85% of polygons in the finely mapped assessments were under one hectare;
vegetation-type agreement came from a few rare groups, led by mangroves, that experts rate as
sensitive; and convertibility partly identified already-modified land.

**Main conclusions.** A single-specification validation can name a different best surrogate from
the same data, and with four usable areas, paired comparisons rarely separated the two candidates. Validations should report a specification curve, threshold-specific discrimination and
benchmark grain, and compare surrogates with paired tests.

**Keywords:** biodiversity surrogates; conservation planning; expert assessment; multiverse
analysis; northern Australia; spatial validation

---

## 1. Introduction

Systematic conservation planning needs maps of where biodiversity value lies (Margules & Pressey,
2000). Across most of northern Australia the species inventories and fine-scale vegetation mapping
those maps would ideally draw on do not exist at planning resolution (Woinarski et al., 2007), and
the region faces expanding agriculture, water development and energy projects (McGinley et al., 2026;
Woinarski et al., 2011). Planners therefore build priority layers from whatever open, wall-to-wall
data are available: land-system and landform maps, vegetation classifications, land-use and tenure
layers, and remote sensing. These layers act as surrogates for the biodiversity information that
direct survey would provide (Ferrier, 2002; Rodrigues & Brooks, 2007; Lindenmayer et al., 2015).

Surrogate performance is known to be modest and inconsistent. Land systems captured distinct plant,
invertebrate and microbial assemblages in arid New South Wales (Oliver et al., 2004), but a global
meta-analysis found that congruence between surrogates and the biodiversity they stand for is low
and varies widely among studies (Westgate et al., 2014). Part of that variation comes from how
effectiveness is measured: the same surrogates looked effective or ineffective in one study region
depending on which of five test methods was used (Grantham et al., 2010), and indicator performance
changed with extent, grain and region (Hess et al., 2006). Reserve selections built from different
planning units overlapped by only 40% (Warman et al., 2004). These are the spatial-statistics
problems of support and the modifiable areal unit (Openshaw, 1984; Jelinski & Wu, 1996; Dungan et
al., 2002).

Validation studies still tend to report one correlation for one unit, weighting and metric. Recent
work in ecology shows how much that can hide. When 174 analyst teams analysed the same two
ecological datasets, their effect sizes ranged from strongly negative to near zero for one question
and changed sign for the other (Gould et al., 2025). Multiverse and specification-curve analysis
address this by running every defensible combination of analysis choices and reporting the
distribution of results (Steegen et al., 2016; Simonsohn et al., 2020). We found no application of
these methods to biodiversity surrogate validation.

Northern Australia offers an unusual test bed. The Northern Territory Government's *Mapping the
Future* program has mapped expert biodiversity-risk classes, informed by field vegetation and fauna
survey, for several areas proposed for development, and five of these use the same five-level scale
with small differences in class wording.
The resulting polygons give an independent, field-informed benchmark of a kind rarely available in
the places where surrogates are used. Here we use six of these assessments to ask three questions.
(1) Which open-data surrogate agrees best with the expert classes? (2) Does that answer survive
defensible changes to the agreement metric, the minimum mapping unit and the treatment of
already-modified land? (3) Where it does not, which features of the benchmark and the surrogates
drive the reversals? We also test whether combining surrogates improves on the best single layer
and transfers to an assessment area it was not trained on.

## 2. Methods

### 2.1 Expert benchmarks

The benchmarks are biodiversity assessments made under the *Mapping the Future* program for six
Northern Territory areas (Figure 1; Table 1): the central Roper River catchment, Larrimah, Wadeye,
Gunn Point, the NTP 3910 Deep Well area and the Greater Weddell subregion (Northern Territory
Government, 2020, 2021a, 2021b, 2021c, 2024b, 2025). For brevity we call them catchments. Five use
the ordinal biodiversity-risk class BIORISK, coded in the same order in each dataset: 1, nil (highly
modified land); 2, low (no significant biodiversity value); 3, mitigable (land that may provide
habitat for broadly occurring threatened species, where retaining part of it may be required);
4, moderate (sensitive or significant vegetation under the NT Land Clearing Guidelines, or species of
conservation interest); 5, high (significant vegetation communities or threatened-species habitat).
The wording differs between datasets (Appendix S3). At Gunn Point, class 3 means "uncertain: requires
further biodiversity assessment", class 4 refers to vegetation types only, and class 5 requires
significant vegetation in combination with threatened-species records (Northern Territory
Government, 2020). Experts assigned a class to each mapped polygon from field survey and existing
mapping. The Roper assessors drew part of their linework from the NT land-use map that our
convertibility surrogate uses and from a land-system survey of the Roper catchment (Northern
Territory Government, 2024b). Greater Weddell uses a separate
five-level biodiversity-values scale (highly modified, low, medium, high, very high); we analysed it
the same way but never pooled it with the BIORISK catchments. Polygons coded 0 (not assessed) or 9
(water) were excluded. The pooled BIORISK set has 26,831 polygons; Greater Weddell has 20,481.

BIORISK records the risk that development poses to biodiversity, so it combines the value of a site,
its sensitivity to impact and its existing condition. We therefore treat it as an expert
biodiversity-risk benchmark, and Section 4.3 discusses what that means for interpretation.

### 2.2 Open-data surrogates

Each polygon was attributed five surrogates, all reprojected to GDA94 / Australian Albers
(EPSG:3577) and area-weighted within the polygon:

- **Land-system rarity**: one minus the min–max rescaled log of the Territory-wide area of each land
  system (NT land systems, 1:250,000 north and 1:1,000,000 south; Northern Territory Government,
  2013).
- **Vegetation-type rarity**: the same transformation applied to the Territory-wide area of each
  native Major Vegetation Group in the National Vegetation Information System (NVIS) v7 extant
  raster at 100 m (Department of Climate Change, Energy, the Environment and Water [DCCEEW],
  2024b). Cleared, bare, sea and unknown codes were treated as missing.
- **Vegetation cover**: 100 minus the median bare-soil fraction from Landsat Fractional Cover
  Percentiles (version 4.0.0) at 30 m for 2020 (Geoscience Australia, 2025).
- **Convertibility**: a score assigned to each Australian Land Use and Management primary class in
  the Northern Territory Land Use Mapping (Northern Territory Government, 2024a): conservation and
  natural environments 0.1; production from relatively natural environments 1.0; dryland agriculture
  and plantations 0.4; irrigated agriculture 0.2; intensive uses 0.0; water missing.
- **Protection**: the fraction of the polygon inside the terrestrial Collaborative Australian
  Protected Areas Database 2024 (DCCEEW, 2024a).

Land-system and vegetation-type rarity are the candidate biodiversity surrogates; vegetation cover is
a condition surrogate; convertibility and protection are reference layers that planners often
combine with the others. Area-weighted overlay leaves floating-point residue (for example, a
polygon wholly within one land-use class can score 0.0999999999999999 or 0.1000000000000002), so
all surrogate values were rounded to four decimal places before analysis. A surrogate that was
constant within a catchment after rounding was treated as not estimable there (convertibility at
Wadeye and Deep Well; protection at Larrimah, Wadeye and Deep Well, none of whose polygons are
protected).

### 2.3 Agreement metrics

We used five metrics, each answering a different practical question:

1. Spearman's ρ with each polygon weighted equally (per-polygon agreement).
2. Spearman's ρ with polygons weighted by area, using area-weighted mid-ranks (agreement per unit of
   land).
3. Kendall's τ-b with polygons weighted equally (rank agreement corrected for the heavy ties in a
   five-level scale).
4. The area under the ROC curve (AUC) for separating polygons in class 4 or 5 from the rest: how well
   a surrogate flags land the experts rated moderate or high risk.
5. The AUC for separating class 5 from the rest: how well it flags the highest-risk land.

AUC is the probability that a randomly chosen higher-class polygon scores higher on the surrogate
than a randomly chosen lower-class polygon (0.5 is no discrimination; Lobo et al., 2008). We also
report the area-capture enrichment: the share of high-risk area inside the 20% of land a surrogate
ranks highest, divided by 0.2. Tied surrogate values at the cut-off were included in proportion so
that coarse layers gain nothing from arbitrary tie order.

### 2.4 Specifications

The multiverse crossed the five metrics with three minimum polygon sizes (all polygons; ≥ 0.1 ha;
≥ 1 ha, the area of one NVIS pixel) and with the inclusion or exclusion of BIORISK class 1 (nil or
highly modified), giving 30 specifications. Each choice is defensible. Expert maps contain many very
small polygons (Table 1) that are below the resolution of every raster surrogate, and an analyst
could reasonably exclude them as mapping fragments or keep them as small, possibly high-value units.
Class 1 marks land that is already cleared or developed, which a land-use layer can detect directly
without any biodiversity information.

### 2.5 Statistical inference

Expert polygons are strongly spatially autocorrelated, so their number far exceeds the number of
independent observations (Clifford et al., 1989; Legendre, 1993; Dormann et al., 2007). Within each
catchment we assigned polygons to 10 km square blocks and resampled whole blocks with replacement
(2,000 replicates; 500 for the multiverse), so that neighbouring polygons moved together. The
variance of the bootstrap replicates (on the Fisher-z scale for correlations, the raw scale for AUC)
gave each catchment's sampling variance. Catchments with fewer than three blocks (Deep Well) were not
estimable.

Catchment estimates were pooled by random-effects meta-analysis (DerSimonian & Laird, 1986). With
only three or four catchments, Wald intervals from that method are too narrow (IntHout et al., 2014),
so we report the Hartung–Knapp–Sidik–Jonkman interval with t on k − 1 degrees of freedom and its
modified form, which never narrows below the fixed-effect interval (Röver et al., 2015). We report
the modified interval in the text; Table S4 gives all three and a leave-one-catchment-out range.

To compare vegetation-type and land-system rarity directly, each bootstrap replicate computed both
surrogates' metrics on the same resampled blocks and took the difference, and the per-catchment
differences were pooled as above. A specification counts as favouring one surrogate when the pooled
95% interval of the paired difference excludes zero.

### 2.6 Mechanism analyses

We ran three analyses to explain disagreements among specifications. (i) Polygon size: per-polygon ρ
for each surrogate as polygons below 0.01, 0.1, 0.5, 1 and 5 ha were removed. (ii) Vegetation groups:
per-polygon ρ for vegetation-type rarity after removing, in turn, each common rare vegetation group
(rarity ≥ 0.25 and ≥ 1% of polygons) and after removing all of them. (iii) Modification: per-polygon
ρ for every surrogate with class 1 excluded. We also repeated the circularity control specified
before the confirmatory analysis: the partial rank correlation of vegetation-type rarity with
BIORISK after removing the linear effect of land-system rarity and convertibility.

### 2.7 Joint model

A linear model of BIORISK on standardised land-system rarity, vegetation-type rarity, convertibility
and protection was evaluated out of sample. Vegetation cover was excluded because it is missing for
over half of the polygons, mostly small ones. All models were fitted on the same 21,655 complete-case
polygons with the same folds: ten folds of whole catchment-by-10 km blocks, repeated 20 times with
predictions averaged across repeats (Roberts et al., 2017; Valavi et al., 2019). Skill was Spearman's
ρ between out-of-sample predictions and observed classes, computed within each catchment and
averaged, because pooling across catchments mixes between-catchment differences in class balance
with agreement. The gain from combining was the paired difference between the joint model and
vegetation-type rarity alone, bootstrapped by resampling blocks within catchments. Leave-one-
catchment-out transfer fitted the model on four catchments and predicted the fifth. For a single
surrogate this test reduces to the within-catchment correlation, so it tests transfer only for the
joint model.

### 2.8 Analysis plan and departures from it

The co-primary per-polygon and area-weighted estimands, the surrogate set, the missing-data rule
(pairwise deletion), the meta-analytic pooling, a check of how far area-weighted estimates depended on the largest polygons and the
circularity control were written into a research log before the confirmatory analysis. The log was
first committed to version control together with the results, so its timing rests on the log itself.
It also followed an exploratory analysis of the same data in which vegetation-type rarity already
appeared to outperform land-system rarity, and it was not lodged in a public registry, so we call it
pre-specified rather than pre-registered (Nosek et al., 2018; Parker et al., 2016). We
departed from it in five ways:

- **Inference.** The block bootstrap replaced the pre-specified nearest-neighbour effective sample
  size after that method was found to miss long-range dependence. Results under the original method
  are in Table S6.
- **Joint model.** The joint model and its cross-validation were specified after the
  single-surrogate results.
- **Pre-submission audit additions.** A pre-submission audit found four problems with the earlier
  analysis:
  - floating-point residue in the overlay values;
  - an unpaired comparison of the joint and single models;
  - intervals too narrow for three or four catchments;
  - a Roper benchmark read from an earlier intersection with the land-use map, which had split expert
    polygons along land-use boundaries.

  Correcting these led to the rounding rule, the paired comparisons, the Hartung–Knapp–Sidik–Jonkman
  intervals and the use of the published Roper layer.
- **Area weighting.** Area weighting now uses area-weighted ranks.
- **Multiverse and mechanism analyses.** These were added at the same audit and are exploratory.

Code, data and a dated decision log are archived (Data Availability).

## 3. Results

### 3.1 The benchmark is dominated by very small polygons

The expert maps mixed a few very large polygons with many tiny ones (Table 1). Median polygon area was
0.02 ha at Gunn Point, 0.12 ha in Greater Weddell and 1.84 ha in the Roper. At Gunn Point, 85% of
polygons were smaller than one hectare, the area of a single NVIS pixel; the shares were 76% in
Greater Weddell and 42% in the Roper. Class balance was uneven: 82% of Roper polygons and 17 of 19
Larrimah polygons were class 4, and 73% of Wadeye polygons were class 5. Some polygons can only be
digitising fragments: 24 of the 3,079 Roper polygons, 178 at Gunn Point and 200 in Greater Weddell
are smaller than 1 m². The 26,831 BIORISK polygons fell into 200 blocks of 10 km: 168 in the Roper,
15 at Gunn Point, 9 at Larrimah, 6 at Wadeye and 2 at Deep Well.

### 3.2 The best surrogate depends on the metric

Per polygon, vegetation-type rarity agreed best in the three large catchments (Spearman's ρ = 0.218
in the Roper, 0.512 at Wadeye, 0.217 at Gunn Point), while land-system rarity stayed between −0.03 and
0.14 (Figure 2; Table 2). Pooled, these were 0.23 [0.08, 0.37] for vegetation-type rarity and
0.09 [−0.01, 0.19] for land-system rarity. Vegetation-type rarity also separated high-risk polygons
(class ≥ 4) best, with AUC from 0.56 (Larrimah) to 0.81 (Wadeye), compared with 0.38–0.55 for
land-system rarity; pooled, 0.67 [0.56, 0.76] against 0.53 [0.46, 0.60].

Under area weighting the order reversed in the Roper and at Larrimah. There land-system rarity
reached ρ = 0.268 and 0.508, whereas vegetation-type rarity was negative (−0.273 and −0.386). At
Wadeye the two were close (0.491 and 0.450), and at Gunn Point vegetation-type rarity led (0.570
against 0.006).

For the highest class the order reversed again in the two assessments with the most polygons. Land-system
rarity identified class 5 polygons better than vegetation-type rarity at Gunn Point (AUC 0.69 versus
0.46) and in Greater Weddell (0.61 versus 0.47), where vegetation-type rarity scored below the
chance level of 0.5. Vegetation-type rarity remained better in the Roper (0.85 versus 0.66) and at
Wadeye (0.83 versus 0.51). Vegetation cover was inconsistent: positive in the Roper (ρ = 0.197; AUC
for class ≥ 4 = 0.64, level with vegetation-type rarity at 0.63) but negative at Gunn Point (−0.057;
AUC 0.40) and in Greater Weddell (−0.033). Protection did not separate expert classes anywhere (AUC 0.48–0.52).

### 3.3 Across specifications

Across the 30 specifications, the paired difference favoured vegetation-type rarity in one,
favoured land-system rarity in none and was inconclusive in 29 (Figure 3; Table S1). The one
exception was AUC for class ≥ 4 with polygons of at least 1 ha and class 1 kept (difference 0.120
[0.019, 0.220]). The highest-scoring candidate surrogate was vegetation-type rarity in 21
specifications and land-system rarity in 9. The metric moved the point estimates most.
Vegetation-type rarity was ahead under per-polygon correlation (differences 0.106 to 0.208), Kendall's
τ-b (0.075 to 0.171) and AUC for class ≥ 4 (0.120 to 0.216), and behind under area-weighted
correlation (−0.126 to −0.100, with intervals spanning about −1.1 to 0.9). The minimum polygon size
moved the result next. For class 5 the difference fell from 0.095 with all polygons to between
−0.032 and −0.003 once polygons under 0.1 ha were removed, and land-system rarity then scored highest
in three of the four specifications. The per-polygon advantage of vegetation-type rarity also shrank
as small polygons were removed (0.208 with all polygons, 0.186 at ≥ 0.1 ha and 0.123 at ≥ 1 ha, with
class 1 kept). Excluding class 1 changed the differences little (per-polygon correlation 0.208 with
class 1 and 0.206 without).

### 3.4 Why the verdicts change

**Polygon size.** Removing sliver polygons raised the agreement of land-system rarity in every large
area (Figure 4a, b; Table S8). At Gunn Point, land-system rarity rose from ρ = 0.141 with all polygons
to 0.286 for polygons of at least 1 ha, overtaking vegetation-type rarity (0.217 to 0.204). At Wadeye
it rose from 0.022 to 0.203, in Greater Weddell from −0.096 to −0.032 and in the Roper from 0.081 to
0.096. Vegetation-type rarity changed little at Gunn Point and in the Roper (0.218 to 0.226) but rose
at Wadeye (0.512 to 0.569) and in Greater Weddell (0.233 to 0.382). Land systems are mapped at 1:250,000
or coarser and do not vary inside most sub-hectare polygons, so a per-polygon metric scores them
against thousands of fragments they cannot resolve.

**Rare vegetation groups.** The agreement of vegetation-type rarity came mostly from a few rare
groups that the experts consistently placed in high-risk classes (Figure 4c; Table S2). Mangroves
(NVIS Major Vegetation Group 23, Territory-wide rarity 0.477) were class 4 in 1,665 of 1,668 Gunn Point polygons and in 1,492 of
1,537 Greater Weddell polygons. Removing mangroves alone cut Greater Weddell's ρ from 0.233 to
0.068. Removing all groups with rarity ≥ 0.25 reversed the sign at Gunn Point (0.217 to −0.043) and
in Greater Weddell (0.233 to −0.034) and lowered the Roper estimate (0.218 to 0.127). Wadeye was the
exception: there agreement rose when the rare groups were removed (0.512 to 0.582). The circularity
control specified before the analysis left a positive partial correlation in each of the four
estimable BIORISK catchments (Roper 0.138, Larrimah 0.053, Wadeye 0.450, Gunn Point 0.136), but the pooled value, 0.17
[−0.02, 0.35], has an interval that includes zero, and Greater Weddell's was 0.013.

**Already-modified land.** Part of convertibility's agreement came from identifying land that was
already modified (Figure 4d; Table S3). Most class 1 polygons scored 0.4 or less on convertibility
(96% at Gunn Point, 95% in Greater Weddell and 74% in the Roper). Excluding class 1 lowered
convertibility's ρ from 0.197 to 0.106 in Greater Weddell and from 0.196 to 0.180 at Gunn Point. In
the Roper convertibility was negatively related to the expert classes with class 1 included
(ρ = −0.079) and more so without it (−0.132). Treating water as missing also removed about a third of class 4 polygons in
the Roper (32%) and at Gunn Point (35%) from the convertibility comparisons.

### 3.5 Combining surrogates

Out of sample, the joint model reached a within-catchment ρ of 0.23 [0.10, 0.37] against
0.15 [0.05, 0.29] for vegetation-type rarity alone, a paired gain of 0.08 [−0.09, 0.23] whose
interval includes zero (Table 3; Figure 5a). Pooled across catchments the gain was 0.18 [0.04, 0.29],
but that measure mixes between-catchment differences in class balance with agreement (Section 2.7).
When its weights were transferred to a catchment left out of fitting, the joint model agreed
positively with the experts in the four catchments with more than six polygons (Roper 0.168,
Larrimah 0.307, Wadeye 0.519, Gunn Point 0.244) and not at all at Deep Well (0.000; Figure 5b). On
the same polygons, vegetation-type rarity alone gave 0.163, 0.104, 0.503, 0.168 and 0.000.

## 4. Discussion

The same benchmark and the same five layers supported opposite conclusions about which surrogate is
best. Counted per polygon, or as the ability to flag moderate-to-high-risk land, vegetation-type
rarity led. Counted per unit of land, or as the ability to find the highest-risk class in the two
most finely mapped coastal assessments, land-system rarity led. Each of these specifications is one that a
careful analyst could choose and defend, and a single-specification validation of either layer would
have reached a confident conclusion. Compared directly on the same resampled blocks, the two
candidates differed beyond sampling error in only one of 30 specifications. This extends the finding that surrogate effectiveness depends on
the test method (Grantham et al., 2010) and on grain and extent (Hess et al., 2006) from
representation tests to validation against an expert benchmark, and it matches the analyst-to-analyst
variation documented for ecological data generally (Gould et al., 2025).

### 4.1 Three mechanisms

The reversals had identifiable causes, and each applies well beyond the Northern Territory.

First, the grain of the benchmark. Expert biodiversity maps are drawn at the scale of field
observation and contain many fragments. When most polygons are smaller than the pixel or map unit of
the surrogate, a per-polygon metric mostly measures whether the surrogate can resolve fragments.
Coarse layers such as land systems cannot, so they score poorly per polygon and well per unit of
area; removing sub-hectare polygons removed much of their disadvantage. Validation studies should
report the size distribution of benchmark units relative to the surrogate's resolution (Dungan et
al., 2002) and vary the minimum mapping unit as one of the analysis choices.

Second, shared rules. Vegetation-type rarity agreed with the experts largely because a few rare
vegetation groups, most clearly mangroves, were ones the experts consistently rated as sensitive.
The Gunn Point class 4 rule names "mangroves and salt flats" among its qualifying communities
(Northern Territory Government, 2020). The partial correlation we specified in advance did not detect this,
because land-system rarity and convertibility are poor proxies for the experts' vegetation rules.
For screening, a surrogate that reproduces expert rules is useful, because it flags the same places
the experts would. As evidence that open data can stand in for field assessment, it is weaker than
it first appears, because part of the agreement is built in. Vegetation-type surrogates should be
validated with leave-one-group-out checks like ours, and expert assessments should record which
vegetation types triggered a class.

Third, modification. Land-use layers can identify land that is already cleared, and benchmarks that
include a "highly modified" class reward them for doing so. Excluding class 1 cut convertibility's
agreement in Greater Weddell from 0.197 to 0.106. Processing the benchmark can add a further bias. An
earlier copy of the Roper benchmark had been intersected with the land-use map, which split expert
polygons along land-use boundaries, and convertibility agreed positively with that copy; on the
published layer it was negatively related to the expert classes. A surrogate meant to rank remaining natural areas
should be tested on remaining natural areas, against the benchmark as published.

### 4.2 Implications for screening

For planners, the metric that matches the decision matters most. Flagging land for closer survey
before clearing calls for discrimination of the higher classes at a fixed area budget, which our
AUC and area-capture results measure directly; a rank correlation over five tied classes does not.
In two of the four large assessments the layer best at flagging class ≥ 4 scored below chance at
flagging class 5, so a screen built on one layer would miss part of the land experts rated highest.
The joint model transferred positively to each of the four catchments with enough polygons to
test, but its within-catchment gain over vegetation-type rarity alone was not distinguishable from
zero. On this evidence open-data layers in the Northern
Territory can support a first-pass screen that directs field survey, provided its maps carry their
uncertainty; they cannot replace the survey.

The same tests apply to the global and national layers now used to screen biodiversity risk for
development finance and corporate disclosure, such as areas of global conservation importance (Jung
et al., 2021) and species threat-abatement metrics (Mair et al., 2021). These layers are coarser
than our surrogates, so the grain effects we report are likely to be larger for them, and to our
knowledge none has been validated against field-informed expert polygons.

### 4.3 Limitations

All benchmarks come from one government program in one jurisdiction, and only four BIORISK catchments
had enough spatial blocks for inference. With k = 4 the pooled intervals are wide and
between-catchment heterogeneity is poorly estimated; the per-catchment results and the specification
curve carry more of the evidence than any single pooled number. Larrimah (19 polygons) and Deep Well
(6 polygons) contribute little. The block bootstrap is approximate when a catchment has fewer than
about 20 blocks, as several do here.

BIORISK classifies the risk that development poses to biodiversity, so it mixes value, sensitivity
and existing condition, and expert judgements carry their own uncertainty and inconsistency
(Burgman et al., 2011; Martin et al., 2012). We treat the benchmark as the assessment planners would
otherwise commission, with its own errors. The five BIORISK datasets share an order but not
identical definitions: Gunn Point's class 3 means that further assessment is needed rather than that
impacts can be mitigated, and its classes 4 and 5 use narrower rules. Within-catchment metrics are
unaffected, but pooled estimates average over slightly different constructs. The Roper assessors also
built their map partly from our convertibility source and from a regional land-system survey, so
some Roper agreement for those two layers may come from shared input. Greater Weddell uses a different scale and was analysed
separately; it matched Gunn Point on the class 5 reversal, but its partial correlation for
vegetation-type rarity was close to zero.

The surrogates are coarse versions of what is available. NVIS Major Vegetation Groups are broad, the
vegetation-cover layer is one year, and a multi-year condition product such as the Habitat Condition
Assessment System (Harwood et al., 2016) may perform differently. Finer vegetation subgroups would
likely strengthen the vegetation signal and the circularity problem together. The multiverse covers
the analysis choices we judged most consequential, not every possible one, and was added after the
pre-specified analysis.

### 4.4 Recommendations

For validations of biodiversity surrogates against expert or survey benchmarks, we recommend five
practices, all of which our code implements:

1. Report a specification curve across metrics, minimum mapping units and the treatment of modified
   land.
2. Report discrimination at the decision threshold, such as the highest expert class.
3. Compare candidate surrogates with paired tests on the same resampled units.
4. Use small-sample random-effects intervals when pooling a handful of areas.
5. Test whether a surrogate's agreement depends on a few classes that the expert rules themselves
   single out.

## Tables

**Table 1. Expert benchmarks.**

| Area | Scale | Polygons | Area (km²) | Polygons per class (class: n) | Median polygon (ha) | Polygons < 1 ha (%) | 10 km blocks |
|---|---|---|---|---|---|---|---|
| Roper | BIORISK | 3,079 | 17,254 | 1:42, 3:437, 4:2529, 5:71 | 1.84 | 42 | 168 |
| Larrimah | BIORISK | 19 | 486 | 3:2, 4:17 | 48.84 | 0 | 9 |
| Wadeye | BIORISK | 412 | 178 | 2:76, 4:36, 5:300 | 2.78 | 31 | 6 |
| Gunn Point | BIORISK | 23,315 | 704 | 1:504, 2:1, 3:8168, 4:9847, 5:4795 | 0.02 | 85 | 15 |
| Deep Well | BIORISK | 6 | 22 | 2:2, 3:2, 4:2 | 321.82 | 0 | 2 |
| Greater Weddell | biodiversity values (separate) | 20,481 | 394 | 1:1254, 2:2176, 3:10860, 4:5394, 5:797 | 0.12 | 76 | 13 |

Counts are polygons with a valid class (1–5) after geometry repair. Analyses of each surrogate use the polygons where that surrogate is defined (pairwise deletion).

**Table 2. Pooled agreement with expert BIORISK under four metrics.**

| Surrogate | ρ per polygon | k | ρ area-weighted | AUC class ≥ 4 | AUC class 5 |
|---|---|---|---|---|---|
| Vegetation-type rarity (NVIS) | 0.231 [0.083, 0.369] | 4 | 0.245 [−0.635, 0.848] | 0.667 [0.559, 0.760] | 0.736 [0.101, 0.986] |
| Land-system rarity | 0.092 [−0.008, 0.189] | 4 | 0.262 [−0.037, 0.518] | 0.531 [0.458, 0.603] | 0.662 [0.467, 0.815] |
| Convertibility | 0.049 [−0.421, 0.499] | 3 | 0.049 [−0.376, 0.457] | 0.521 [0.291, 0.742] | 0.423 [0.000, 1.000] |
| Vegetation cover (DEA) | 0.091 [−0.168, 0.339] | 4 | −0.088 [−0.328, 0.163] | 0.546 [0.309, 0.764] | 0.618 [0.407, 0.793] |
| Protection | −0.017 [−0.235, 0.204] | 2 | −0.236 [−0.944, 0.861] | 0.497 [0.420, 0.574] | 0.481 [0.359, 0.605] |
| NVIS, partial (land-system, convertibility) | 0.168 [−0.022, 0.347] | 4 | — | — | — |

Random-effects meta-analysis over the estimable BIORISK catchments (k). Intervals are 95% modified Hartung–Knapp–Sidik–Jonkman intervals (t on k − 1 df) from spatial block-bootstrap variances (10 km blocks). Area-weighted ρ uses area-weighted mid-ranks. AUC: probability that a polygon in the higher class scores higher on the surrogate (0.5 = no discrimination). n.e. = not estimable.

**Table 3. Out-of-sample agreement of the joint model and single surrogates.**

| Model | Within-catchment ρ [95% CI] | Pooled ρ [95% CI] |
|---|---|---|
| Joint model (land-system + NVIS + convertibility + protection) | 0.230 [0.096, 0.374] | 0.196 [0.067, 0.301] |
| Vegetation-type rarity (NVIS) | 0.155 [0.049, 0.287] | 0.015 [−0.066, 0.158] |
| Land-system rarity | 0.109 [−0.009, 0.253] | 0.116 [0.002, 0.192] |
| Convertibility | −0.022 [−0.178, 0.183] | −0.014 [−0.188, 0.179] |
| Joint minus NVIS (paired) | 0.076 [−0.085, 0.229] | 0.181 [0.045, 0.295] |

Spatial-block cross-validation (10 km blocks, 10 folds, 20 repeats); all models fitted on the same 21,655 polygons with the same folds. The difference row is a paired block bootstrap stratified by catchment. Leave-one-catchment-out transfer of the joint model: Roper 0.168; Larrimah 0.307; Wadeye 0.519; Gunn Point 0.244; Deep Well 0.000.

## Figure legends

**Figure 1.** Study area. (a) Location of the six expert assessments in the Northern Territory; blue,
the five areas mapped on the BIORISK scale and pooled; pink, Greater Weddell, mapped on a separate
biodiversity-values scale. (b) Share of each area's assessed land in each expert class, with polygon
counts.

**Figure 2.** Pooled agreement of each surrogate with the expert classes under four metrics: (a)
per-polygon Spearman's ρ; (b) area-weighted Spearman's ρ; (c) AUC for class ≥ 4 against the rest;
(d) AUC for class 5 against the rest. Points are random-effects estimates over the estimable BIORISK
catchments, bars are modified Hartung–Knapp–Sidik–Jonkman 95% intervals, and the ring marks the
highest-scoring candidate surrogate under each metric; arrowheads mark intervals that continue
beyond the axis. The estimates are those in Table 2.

**Figure 3.** Specification curve for the paired difference between vegetation-type rarity and
land-system rarity across 30 specifications. Upper panel: pooled difference and 95% interval, green
where vegetation-type rarity is better, orange where land-system rarity is better, grey where the
interval includes zero. Lower panel: the analysis choices that define each specification.

**Figure 4.** Mechanisms behind the reversals. (a) Cumulative distribution of polygon area; the
vertical line marks one NVIS pixel (1 ha). (b) Per-polygon ρ of vegetation-type and land-system
rarity as polygons below a minimum area are removed, at Gunn Point and Wadeye. (c) Per-polygon ρ of
vegetation-type rarity with all polygons and with the rarest vegetation groups removed. (d)
Per-polygon ρ of convertibility with all classes and with class 1 (nil or highly modified) removed,
in the three areas that contain class 1 polygons.

**Figure 5.** Combining surrogates. (a) Out-of-sample within-catchment Spearman's ρ from spatial-block
cross-validation, with the paired difference between the joint model and vegetation-type rarity.
(b) Agreement in each catchment when the joint model is fitted on the other four, compared with
vegetation-type rarity alone on the same polygons.

## Data Availability Statement

All benchmark and surrogate layers are open Northern Territory and Australian Government datasets
listed in the References. The harmonised analysis table, polygon centroids, analysis code, decision
log and all output tables are archived at Zenodo [DOI added at the v2.0-submission release; an
anonymised copy is provided to reviewers].

## References

Burgman, M. A., McBride, M., Ashton, R., Speirs-Bridge, A., Flander, L., Wintle, B., Fidler, F.,
Rumpff, L., & Twardy, C. (2011). Expert status and performance. *PLoS ONE*, *6*(7), Article e22998.
https://doi.org/10.1371/journal.pone.0022998

Clifford, P., Richardson, S., & Hémon, D. (1989). Assessing the significance of the correlation
between two spatial processes. *Biometrics*, *45*(1), 123–134. https://doi.org/10.2307/2532039

Department of Climate Change, Energy, the Environment and Water. (2024a). *Collaborative
Australian Protected Areas Database (CAPAD) 2024 – Terrestrial* [Data set]. Australian Government.
https://www.dcceew.gov.au/environment/land/nrs/science/capad/2024

Department of Climate Change, Energy, the Environment and Water. (2024b). *National
Vegetation Information System (NVIS), Version 7.0* [Data set]. Australian Government.
https://www.dcceew.gov.au/environment/environment-information-australia/national-vegetation-information-system

DerSimonian, R., & Laird, N. (1986). Meta-analysis in clinical trials. *Controlled Clinical Trials*,
*7*(3), 177–188. https://doi.org/10.1016/0197-2456(86)90046-2

Dormann, C. F., McPherson, J. M., Araújo, M. B., Bivand, R., Bolliger, J., Carl, G., Davies, R. G.,
Hirzel, A., Jetz, W., Kissling, W. D., Kühn, I., Ohlemüller, R., Peres-Neto, P. R., Reineking, B.,
Schröder, B., Schurr, F. M., & Wilson, R. (2007). Methods to account for spatial autocorrelation in
the analysis of species distributional data: A review. *Ecography*, *30*(5), 609–628.
https://doi.org/10.1111/j.2007.0906-7590.05171.x

Dungan, J. L., Perry, J. N., Dale, M. R. T., Legendre, P., Citron-Pousty, S., Fortin, M.-J.,
Jakomulska, A., Miriti, M., & Rosenberg, M. S. (2002). A balanced view of scale in spatial
statistical analysis. *Ecography*, *25*(5), 626–640. https://doi.org/10.1034/j.1600-0587.2002.250510.x

Ferrier, S. (2002). Mapping spatial pattern in biodiversity for regional conservation planning:
Where to from here? *Systematic Biology*, *51*(2), 331–363. https://doi.org/10.1080/10635150252899806

Geoscience Australia. (2025). *DEA Fractional Cover Percentiles (Landsat), Version 4.0.0* (product
ga_ls_fc_pc_cyear_3) [Data set]. Commonwealth of Australia (Geoscience Australia).
https://doi.org/10.26186/150570

Gould, E., Fraser, H. S., Parker, T. H., Nakagawa, S., Griffith, S. C., Vesk, P. A., Fidler, F.,
Hamilton, D. G., Abbey-Lee, R. N., Abbott, J. K., Aguirre, L. A., Alcaraz, C., Aloni, I., Altschul,
D., Arekar, K., Atkins, J. W., Atkinson, J., Baker, C. M., Barrett, M., ... Zitomer, R. A. (2025).
Same data, different analysts: Variation in effect sizes due to analytical decisions in ecology and
evolutionary biology. *BMC Biology*, *23*(1), Article 35. https://doi.org/10.1186/s12915-024-02101-x

Grantham, H. S., Pressey, R. L., Wells, J. A., & Beattie, A. J. (2010). Effectiveness of biodiversity
surrogates for conservation planning: Different measures of effectiveness generate a kaleidoscope of
variation. *PLoS ONE*, *5*(7), Article e11430. https://doi.org/10.1371/journal.pone.0011430

Harwood, T. D., Donohue, R. J., Williams, K. J., Ferrier, S., McVicar, T. R., Newell, G., & White, M.
(2016). Habitat Condition Assessment System: A new way to assess the condition of natural habitats
for terrestrial biodiversity across whole regions using remote sensing data. *Methods in Ecology and
Evolution*, *7*(9), 1050–1059.
https://doi.org/10.1111/2041-210X.12579

Hess, G. R., Bartel, R. A., Leidner, A. K., Rosenfeld, K. M., Rubino, M. J., Snider, S. B., &
Ricketts, T. H. (2006). Effectiveness of biodiversity indicators varies with extent, grain, and
region. *Biological Conservation*, *132*(4), 448–457. https://doi.org/10.1016/j.biocon.2006.04.037

IntHout, J., Ioannidis, J. P. A., & Borm, G. F. (2014). The Hartung-Knapp-Sidik-Jonkman method for
random effects meta-analysis is straightforward and considerably outperforms the standard
DerSimonian-Laird method. *BMC Medical Research Methodology*, *14*(1), Article 25.
https://doi.org/10.1186/1471-2288-14-25

Jelinski, D. E., & Wu, J. (1996). The modifiable areal unit problem and implications for landscape
ecology. *Landscape Ecology*, *11*(3), 129–140. https://doi.org/10.1007/BF02447512

Jung, M., Arnell, A., de Lamo, X., García-Rangel, S., Lewis, M., Mark, J., Merow, C., Miles, L.,
Ondo, I., Pironon, S., Ravilious, C., Rivers, M., Schepaschenko, D., Tallowin, O., van Soesbergen, A.,
Govaerts, R., Boyle, B. L., Enquist, B. J., Feng, X., ... Visconti, P. (2021). Areas of global
importance for conserving terrestrial biodiversity, carbon and water. *Nature Ecology & Evolution*,
*5*(11), 1499–1509. https://doi.org/10.1038/s41559-021-01528-7

Legendre, P. (1993). Spatial autocorrelation: Trouble or new paradigm? *Ecology*, *74*(6),
1659–1673. https://doi.org/10.2307/1939924

Lindenmayer, D., Pierson, J., Barton, P., Beger, M., Branquinho, C., Calhoun, A., Caro, T., Greig,
H., Gross, J., Heino, J., Hunter, M., Lane, P., Longo, C., Martin, K., McDowell, W. H., Mellin, C.,
Salo, H., Tulloch, A., & Westgate, M. (2015). A new framework for selecting environmental surrogates.
*Science of the Total Environment*, *538*, 1029–1038. https://doi.org/10.1016/j.scitotenv.2015.08.056

Lobo, J. M., Jiménez-Valverde, A., & Real, R. (2008). AUC: A misleading measure of the performance of
predictive distribution models. *Global Ecology and Biogeography*, *17*(2), 145–151.
https://doi.org/10.1111/j.1466-8238.2007.00358.x

Mair, L., Bennun, L. A., Brooks, T. M., Butchart, S. H. M., Bolam, F. C., Burgess, N. D., Ekstrom,
J. M. M., Milner-Gulland, E. J., Hoffmann, M., Ma, K., Macfarlane, N. B. W., Raimondo, D. C.,
Rodrigues, A. S. L., Shen, X., Strassburg, B. B. N., Beatty, C. R., Gómez-Creutzberg, C., Iribarrem,
A., Irmadhiany, M., ... McGowan, P. J. K. (2021). A metric for spatially explicit contributions to
science-based species targets. *Nature Ecology & Evolution*, *5*(6), 836–844.
https://doi.org/10.1038/s41559-021-01432-0

Margules, C. R., & Pressey, R. L. (2000). Systematic conservation planning. *Nature*,
*405*(6783), 243–253. https://doi.org/10.1038/35012251

Martin, T. G., Burgman, M. A., Fidler, F., Kuhnert, P. M., Low-Choy, S., McBride, M., & Mengersen, K.
(2012). Eliciting expert knowledge in conservation science. *Conservation Biology*, *26*(1), 29–38.
https://doi.org/10.1111/j.1523-1739.2011.01806.x

McGinley, B., Edwards, A., & Garnett, S. T. (2026). Gaps in conservation planning in the Northern
Territory of Australia: Preparing for the energy transition. *Australasian Journal of Environmental
Management*, *33*(1), 30–47. https://doi.org/10.1080/14486563.2025.2575948

Northern Territory Government. (2013). *Northern Territory land systems (compilation of north_250 and
south_1M)* [Data set]. https://data.nt.gov.au/dataset/northern-territory-land-systems-compilation-of-north-250-and-south-1m

Northern Territory Government. (2020). *Risk to biodiversity in the Gunn Point area, 2020* [Data set].
https://data.nt.gov.au/dataset/risk-to-biodiversity-in-the-gunn-point-area-2020

Northern Territory Government. (2021a). *Biodiversity assessment study of NTP 3910 in the Deep Well
area, 2021* [Data set]. https://data.nt.gov.au/dataset/biodiversity-assessment-of-ntp-3910-in-the-deep-well-area-2021

Northern Territory Government. (2021b). *Risk to biodiversity in the Wadeye area, 2021* [Data set].
https://data.nt.gov.au/dataset/risk-to-biodiversity-in-the-wadeye-area-2021

Northern Territory Government. (2021c). *Risk to biodiversity of the Larrimah area, 2021* [Data set].
https://data.nt.gov.au/dataset/risk-to-biodiversity-of-the-larrimah-area-2021

Northern Territory Government. (2024a). *Land use mapping project of the Northern Territory,
2016–2024 (LUMP)* [Data set]. https://data.nt.gov.au/dataset/land-use-mapping-project-of-the-northern-territory-2016-current-lump

Northern Territory Government. (2024b). *Risk to biodiversity of the central Roper River catchment,
2024* [Data set]. https://data.nt.gov.au/dataset/risk-to-biodiversity-of-the-central-roper-river-catchment-2024

Northern Territory Government. (2025). *Biodiversity assessment of the Greater Weddell subregion*
[Data set]. https://data.nt.gov.au/dataset/biovalue_greater_weddell

Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). The preregistration
revolution. *Proceedings of the National Academy of Sciences*, *115*(11), 2600–2606.
https://doi.org/10.1073/pnas.1708274114

Oliver, I., Holmes, A., Dangerfield, J. M., Gillings, M., Pik, A. J., Britton, D. R., Holley, M.,
Montgomery, M. E., Raison, M., Logan, V., Pressey, R. L., & Beattie, A. J. (2004). Land systems as
surrogates for biodiversity in conservation planning. *Ecological Applications*, *14*(2), 485–503.
https://doi.org/10.1890/02-5181

Openshaw, S. (1984). *The modifiable areal unit problem* (Concepts and Techniques in Modern
Geography 38). Geo Books.

Parker, T. H., Forstmeier, W., Koricheva, J., Fidler, F., Hadfield, J. D., Chee, Y. E., Kelly, C. D.,
Gurevitch, J., & Nakagawa, S. (2016). Transparency in ecology and evolution: Real problems, real
solutions. *Trends in Ecology & Evolution*, *31*(9), 711–719. https://doi.org/10.1016/j.tree.2016.07.002

Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S.,
Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., &
Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or
phylogenetic structure. *Ecography*, *40*(8), 913–929. https://doi.org/10.1111/ecog.02881

Rodrigues, A. S. L., & Brooks, T. M. (2007). Shortcuts for biodiversity conservation planning: The
effectiveness of surrogates. *Annual Review of Ecology, Evolution, and Systematics*, *38*(1), 713–737.
https://doi.org/10.1146/annurev.ecolsys.38.091206.095737

Röver, C., Knapp, G., & Friede, T. (2015). Hartung-Knapp-Sidik-Jonkman approach and its modification
for random-effects meta-analysis with few studies. *BMC Medical Research Methodology*, *15*(1), Article 99.
https://doi.org/10.1186/s12874-015-0091-1

Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis. *Nature Human
Behaviour*, *4*(11), 1208–1214. https://doi.org/10.1038/s41562-020-0912-z

Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016). Increasing transparency through a
multiverse analysis. *Perspectives on Psychological Science*, *11*(5), 702–712.
https://doi.org/10.1177/1745691616658637

Valavi, R., Elith, J., Lahoz-Monfort, J. J., & Guillera-Arroita, G. (2019). blockCV: An R package for
generating spatially or environmentally separated folds for k-fold cross-validation of species
distribution models. *Methods in Ecology and Evolution*, *10*(2), 225–232.
https://doi.org/10.1111/2041-210X.13107

Warman, L. D., Sinclair, A. R. E., Scudder, G. G. E., Klinkenberg, B., & Pressey, R. L. (2004).
Sensitivity of systematic reserve selection to decisions about scale, biological data, and targets:
Case study from southern British Columbia. *Conservation Biology*, *18*(3), 655–666.
https://doi.org/10.1111/j.1523-1739.2004.00538.x

Westgate, M. J., Barton, P. S., Lane, P. W., & Lindenmayer, D. B. (2014). Global meta-analysis
reveals low consistency of biodiversity congruence relationships. *Nature Communications*, *5*(1),
Article 3899. https://doi.org/10.1038/ncomms4899

Woinarski, J., Mackey, B., Nix, H., & Traill, B. (2007). *The nature of northern Australia: Natural
values, ecological processes and future prospects*. ANU E Press. https://doi.org/10.22459/NNA.07.2007

Woinarski, J. C. Z., Legge, S., Fitzsimons, J. A., Traill, B. J., Burbidge, A. A., Fisher, A., Firth,
R. S. C., Gordon, I. J., Griffiths, A. D., Johnson, C. N., McKenzie, N. L., Palmer, C., Radford, I.,
Rankmore, B., Ritchie, E. G., Ward, S., & Ziembicki, M. (2011). The disappearing mammal fauna of
northern Australia: Context, cause, and response. *Conservation Letters*, *4*(3), 192–201.
https://doi.org/10.1111/j.1755-263X.2011.00164.x
