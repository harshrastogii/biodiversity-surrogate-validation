# Supporting Information

**Table S1. Every specification: paired NVIS minus land-system difference.**

| Metric | Min. polygon (ha) | Class 1 excluded | Difference [mHKSJ 95% CI] | DL 95% CI | k | Highest-scoring surrogate |
|---|---|---|---|---|---|---|
| spearman_unit | 0.0 | False | 0.208 [−0.092, 0.509] | [0.027, 0.389] | 4 | Vegetation-type rarity (NVIS) |
| spearman_unit | 0.0 | True | 0.206 [−0.119, 0.530] | [0.006, 0.406] | 4 | Vegetation-type rarity (NVIS) |
| spearman_unit | 0.1 | False | 0.186 [−0.170, 0.542] | [−0.022, 0.393] | 4 | Vegetation-type rarity (NVIS) |
| spearman_unit | 0.1 | True | 0.167 [−0.205, 0.540] | [−0.048, 0.383] | 4 | Vegetation-type rarity (NVIS) |
| spearman_unit | 1.0 | False | 0.123 [−0.206, 0.452] | [−0.077, 0.323] | 4 | Vegetation-type rarity (NVIS) |
| spearman_unit | 1.0 | True | 0.106 [−0.237, 0.449] | [−0.097, 0.309] | 4 | Vegetation-type rarity (NVIS) |
| spearman_area | 0.0 | False | −0.100 [−1.081, 0.881] | [−0.705, 0.504] | 4 | Land-system rarity |
| spearman_area | 0.0 | True | −0.120 [−1.109, 0.870] | [−0.729, 0.490] | 4 | Land-system rarity |
| spearman_area | 0.1 | False | −0.108 [−1.101, 0.885] | [−0.720, 0.503] | 4 | Land-system rarity |
| spearman_area | 0.1 | True | −0.116 [−1.093, 0.861] | [−0.718, 0.486] | 4 | Land-system rarity |
| spearman_area | 1.0 | False | −0.109 [−1.117, 0.899] | [−0.729, 0.512] | 4 | Land-system rarity |
| spearman_area | 1.0 | True | −0.126 [−1.102, 0.850] | [−0.727, 0.475] | 4 | Land-system rarity |
| auc_ge4 | 0.0 | False | 0.158 [−0.003, 0.320] | [0.059, 0.258] | 4 | Vegetation-type rarity (NVIS) |
| auc_ge4 | 0.0 | True | 0.162 [−0.023, 0.346] | [0.048, 0.275] | 4 | Vegetation-type rarity (NVIS) |
| auc_ge4 | 0.1 | False | 0.216 [−0.051, 0.482] | [0.051, 0.380] | 4 | Vegetation-type rarity (NVIS) |
| auc_ge4 | 0.1 | True | 0.215 [−0.079, 0.508] | [0.034, 0.395] | 4 | Vegetation-type rarity (NVIS) |
| auc_ge4 | 1.0 | False | 0.120 [0.019, 0.220] | [0.058, 0.182] | 4 | Vegetation-type rarity (NVIS) |
| auc_ge4 | 1.0 | True | 0.130 [−0.022, 0.282] | [0.037, 0.223] | 4 | Vegetation-type rarity (NVIS) |
| auc_eq5 | 0.0 | False | 0.095 [−0.794, 0.983] | [−0.310, 0.499] | 3 | Vegetation-type rarity (NVIS) |
| auc_eq5 | 0.0 | True | 0.094 [−0.788, 0.976] | [−0.308, 0.496] | 3 | Vegetation-type rarity (NVIS) |
| auc_eq5 | 0.1 | False | −0.003 [−1.218, 1.213] | [−0.556, 0.551] | 3 | Vegetation-type rarity (NVIS) |
| auc_eq5 | 0.1 | True | −0.006 [−1.259, 1.248] | [−0.577, 0.565] | 3 | Land-system rarity |
| auc_eq5 | 1.0 | False | −0.031 [−1.180, 1.118] | [−0.554, 0.493] | 3 | Land-system rarity |
| auc_eq5 | 1.0 | True | −0.032 [−1.174, 1.110] | [−0.552, 0.488] | 3 | Land-system rarity |
| kendall_tau_b | 0.0 | False | 0.171 [−0.068, 0.410] | [0.026, 0.317] | 4 | Vegetation-type rarity (NVIS) |
| kendall_tau_b | 0.0 | True | 0.164 [−0.087, 0.415] | [0.010, 0.318] | 4 | Vegetation-type rarity (NVIS) |
| kendall_tau_b | 0.1 | False | 0.148 [−0.143, 0.439] | [−0.024, 0.320] | 4 | Vegetation-type rarity (NVIS) |
| kendall_tau_b | 0.1 | True | 0.127 [−0.175, 0.429] | [−0.045, 0.299] | 4 | Vegetation-type rarity (NVIS) |
| kendall_tau_b | 1.0 | False | 0.093 [−0.189, 0.375] | [−0.081, 0.266] | 4 | Vegetation-type rarity (NVIS) |
| kendall_tau_b | 1.0 | True | 0.075 [−0.211, 0.361] | [−0.097, 0.247] | 4 | Vegetation-type rarity (NVIS) |

**Table S2. NVIS agreement after removing rare vegetation groups.**

| Area | Removed | Polygons removed | ρ per polygon |
|---|---|---|---|
| Roper | none | 0 | 0.218 |
| Roper | rarity=0.319 (share BIORISK>=4: 0.90) | 206 | 0.207 |
| Roper | rarity=0.420 (share BIORISK>=4: 0.96) | 70 | 0.214 |
| Roper | all rarity>=0.25 | 928 | 0.127 |
| Larrimah | none | 0 | 0.064 |
| Larrimah | all rarity>=0.25 | 2 | 0.000 |
| Wadeye | none | 0 | 0.512 |
| Wadeye | rarity=0.262 (share BIORISK>=4: 0.99) | 77 | 0.520 |
| Wadeye | rarity=0.477 (share BIORISK>=4: 1.00) | 7 | 0.509 |
| Wadeye | all rarity>=0.25 | 189 | 0.582 |
| Gunn Point | none | 0 | 0.217 |
| Gunn Point | rarity=0.477 (share BIORISK>=4: 1.00) | 1668 | 0.199 |
| Gunn Point | rarity=0.383 (share BIORISK>=4: 0.74) | 1454 | 0.219 |
| Gunn Point | rarity=0.517 (share BIORISK>=4: 0.94) | 1181 | 0.179 |
| Gunn Point | rarity=0.319 (share BIORISK>=4: 0.85) | 650 | 0.206 |
| Gunn Point | rarity=0.262 (share BIORISK>=4: 1.00) | 284 | 0.214 |
| Gunn Point | all rarity>=0.25 | 7421 | −0.043 |
| Deep Well | none | 0 | 0.000 |
| Deep Well | all rarity>=0.25 | 0 | 0.000 |
| Greater Weddell | none | 0 | 0.233 |
| Greater Weddell | rarity=0.477 (share BIORISK>=4: 0.98) | 1537 | 0.068 |
| Greater Weddell | all rarity>=0.25 | 2828 | −0.034 |

Groups are identified by their NT-wide rarity value (rounded to 3 d.p.); share of BIORISK ≥ 4 in brackets.

**Table S3. Pooled per-polygon ρ after excluding class 1 (nil or highly modified).**

| Surrogate | ρ [mHKSJ 95% CI] | k |
|---|---|---|
| Land-system rarity | 0.088 [−0.013, 0.187] | 4 |
| Vegetation-type rarity (NVIS) | 0.220 [0.057, 0.371] | 4 |
| Vegetation cover (DEA) | 0.076 [−0.176, 0.318] | 4 |
| Convertibility | 0.021 [−0.506, 0.537] | 3 |
| Protection | −0.015 [−0.222, 0.193] | 2 |

**Table S4. Pooled estimates under three random-effects interval methods.**

| Quantity | Estimand | ρ | DerSimonian–Laird | HKSJ | Modified HKSJ | I² (%) | k | Leave-one-out range | Catchments |
|---|---|---|---|---|---|---|---|---|---|
| Land-system rarity | E-UNIT | 0.092 | [0.031, 0.152] | [0.030, 0.153] | [−0.008, 0.189] | 0 | 4 | [0.076, 0.118] | Roper;Larrimah;Wadeye;GunnPoint |
| Land-system rarity | E-AREA | 0.262 | [0.080, 0.427] | [0.017, 0.477] | [−0.037, 0.518] | 0 | 4 | [0.228, 0.305] | Roper;Larrimah;Wadeye;GunnPoint |
| Vegetation-type rarity (NVIS) | E-UNIT | 0.231 | [0.147, 0.312] | [0.083, 0.369] | [0.083, 0.369] | 18 | 4 | [0.216, 0.279] | Roper;Larrimah;Wadeye;GunnPoint |
| Vegetation-type rarity (NVIS) | E-AREA | 0.245 | [−0.350, 0.700] | [−0.504, 0.784] | [−0.635, 0.848] | 90 | 4 | [0.067, 0.538] | Roper;Larrimah;Wadeye;GunnPoint |
| Vegetation cover (DEA) | E-UNIT | 0.091 | [−0.069, 0.248] | [−0.100, 0.276] | [−0.168, 0.339] | 81 | 4 | [0.008, 0.191] | Roper;Larrimah;Wadeye;GunnPoint |
| Vegetation cover (DEA) | E-AREA | −0.088 | [−0.239, 0.067] | [−0.182, 0.007] | [−0.328, 0.163] | 0 | 4 | [−0.106, −0.069] | Roper;Larrimah;Wadeye;GunnPoint |
| Convertibility | E-UNIT | 0.049 | [−0.176, 0.269] | [−0.351, 0.434] | [−0.421, 0.499] | 63 | 3 | [−0.075, 0.194] | Roper;Larrimah;GunnPoint |
| Convertibility | E-AREA | 0.049 | [−0.152, 0.246] | [−0.124, 0.219] | [−0.376, 0.457] | 0 | 3 | [−0.046, 0.078] | Roper;Larrimah;GunnPoint |
| Protection | E-UNIT | −0.017 | [−0.051, 0.018] | [−0.032, −0.001] | [−0.235, 0.204] | 0 | 2 | n.e. | Roper;GunnPoint |
| Protection | E-AREA | −0.236 | [−0.444, −0.003] | [−0.908, 0.777] | [−0.944, 0.861] | 0 | 2 | n.e. | Roper;GunnPoint |
| NVIS, partial (land-system, convertibility) | E-UNIT | 0.168 | [0.075, 0.259] | [−0.022, 0.347] | [−0.022, 0.347] | 49 | 4 | [0.137, 0.241] | Roper;Larrimah;Wadeye;GunnPoint |

**Table S5. Greater Weddell (biodiversity-values scale; not pooled).**

| Quantity | Estimand | ρ | Polygons | 10 km blocks |
|---|---|---|---|---|
| Land-system rarity | E-UNIT | −0.096 | 20437 | 13 |
| Land-system rarity | E-AREA | −0.123 | 20437 | 13 |
| Vegetation-type rarity (NVIS) | E-UNIT | 0.233 | 19251 | 13 |
| Vegetation-type rarity (NVIS) | E-AREA | 0.434 | 19251 | 13 |
| Vegetation cover (DEA) | E-UNIT | −0.033 | 12994 | 13 |
| Vegetation cover (DEA) | E-AREA | 0.114 | 12994 | 13 |
| Convertibility | E-UNIT | 0.197 | 18412 | 13 |
| Convertibility | E-AREA | 0.127 | 18412 | 13 |
| Protection | E-UNIT | 0.076 | 20481 | 13 |
| Protection | E-AREA | 0.063 | 20481 | 13 |
| NVIS, partial (land-system, convertibility) | E-UNIT | 0.013 | 17187 | 13 |

**Table S6. Results under the originally pre-specified inference (KNN effective sample size).**

| Surrogate | Estimand | ρ [95% CI] | I² (%) | k |
|---|---|---|---|---|
| Land-system rarity | E-UNIT | 0.106 [0.057, 0.155] | 38 | 4 |
| Land-system rarity | E-AREA | 0.301 [0.264, 0.336] | 19 | 4 |
| Vegetation-type rarity (NVIS) | E-UNIT | 0.262 [0.179, 0.342] | 78 | 4 |
| Vegetation-type rarity (NVIS) | E-AREA | 0.287 [−0.424, 0.779] | 100 | 4 |
| Vegetation cover (DEA) | E-UNIT | 0.085 [−0.104, 0.269] | 96 | 4 |
| Vegetation cover (DEA) | E-AREA | −0.034 [−0.062, −0.006] | 0 | 4 |
| Convertibility | E-UNIT | 0.079 [−0.167, 0.315] | 97 | 3 |
| Convertibility | E-AREA | −0.025 [−0.173, 0.124] | 90 | 3 |
| Protection | E-UNIT | −0.019 [−0.049, 0.012] | 0 | 2 |
| Protection | E-AREA | −0.418 [−0.698, −0.027] | 99 | 2 |

Pre-specified method (P3.PR2.2), replaced by the spatial block bootstrap after it was found to under-represent long-range dependence (Section 2.5).

**Table S7. Area-weighted ρ before and after removing the largest 5% of polygons.**

| Area | Surrogate | All polygons | Largest 5% removed |
|---|---|---|---|
| Roper | Land-system rarity | 0.276 | 0.154 |
| Roper | Vegetation-type rarity (NVIS) | −0.157 | 0.122 |
| Roper | Vegetation cover (DEA) | −0.044 | 0.099 |
| Roper | Convertibility | 0.075 | −0.082 |
| Roper | Protection | −0.228 | 0.016 |
| Larrimah | Land-system rarity | 0.516 | 0.097 |
| Larrimah | Vegetation-type rarity (NVIS) | −0.362 | 0.326 |
| Larrimah | Vegetation cover (DEA) | 0.216 | 0.786 |
| Larrimah | Convertibility | −0.263 | 0.457 |
| Wadeye | Land-system rarity | 0.408 | 0.325 |
| Wadeye | Vegetation-type rarity (NVIS) | 0.612 | 0.658 |
| Wadeye | Vegetation cover (DEA) | −0.079 | −0.022 |
| Gunn Point | Land-system rarity | 0.308 | 0.163 |
| Gunn Point | Vegetation-type rarity (NVIS) | 0.737 | 0.215 |
| Gunn Point | Vegetation cover (DEA) | −0.028 | 0.032 |
| Gunn Point | Convertibility | −0.085 | 0.171 |
| Gunn Point | Protection | −0.577 | 0.043 |
| Deep Well | Land-system rarity | −0.004 | n.e. |
| Deep Well | Vegetation-type rarity (NVIS) | 0.026 | n.e. |
| Deep Well | Vegetation cover (DEA) | −0.422 | n.e. |

Pre-specified leverage check (P3.PR2.5), applied to every surrogate. P3 weighting (unweighted ranks).

**Table S8. Per-polygon ρ as polygons below a minimum area are removed.**

| Area | Surrogate | all | ≥ 0.01 ha | ≥ 0.1 ha | ≥ 0.5 ha | ≥ 1 ha | ≥ 5 ha |
|---|---|---|---|---|---|---|---|
| Deep Well | Vegetation cover (DEA) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Deep Well | Land-system rarity | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Deep Well | Vegetation-type rarity (NVIS) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Gunn Point | Vegetation cover (DEA) | −0.057 | −0.058 | 0.012 | 0.035 | 0.037 | 0.076 |
| Gunn Point | Convertibility | 0.196 | 0.195 | 0.210 | 0.161 | 0.130 | 0.148 |
| Gunn Point | Protection | −0.020 | −0.022 | 0.011 | 0.050 | 0.063 | 0.042 |
| Gunn Point | Land-system rarity | 0.141 | 0.119 | 0.186 | 0.258 | 0.286 | 0.355 |
| Gunn Point | Vegetation-type rarity (NVIS) | 0.217 | 0.240 | 0.181 | 0.182 | 0.204 | 0.209 |
| Larrimah | Vegetation cover (DEA) | 0.125 | 0.125 | 0.125 | 0.125 | 0.125 | 0.136 |
| Larrimah | Convertibility | 0.179 | 0.179 | 0.179 | 0.179 | 0.179 | 0.195 |
| Larrimah | Land-system rarity | −0.032 | −0.032 | −0.032 | −0.032 | −0.032 | 0.000 |
| Larrimah | Vegetation-type rarity (NVIS) | 0.064 | 0.064 | 0.064 | 0.064 | 0.064 | 0.069 |
| Roper | Vegetation cover (DEA) | 0.197 | 0.197 | 0.204 | 0.214 | 0.234 | 0.211 |
| Roper | Convertibility | −0.079 | −0.082 | −0.082 | −0.061 | −0.051 | −0.049 |
| Roper | Protection | −0.016 | −0.019 | −0.017 | −0.013 | −0.014 | −0.025 |
| Roper | Land-system rarity | 0.081 | 0.086 | 0.096 | 0.092 | 0.096 | 0.101 |
| Roper | Vegetation-type rarity (NVIS) | 0.218 | 0.216 | 0.223 | 0.234 | 0.226 | 0.207 |
| Wadeye | Vegetation cover (DEA) | 0.105 | 0.105 | 0.110 | 0.113 | 0.075 | 0.093 |
| Wadeye | Land-system rarity | 0.022 | 0.020 | 0.024 | 0.116 | 0.203 | 0.385 |
| Wadeye | Vegetation-type rarity (NVIS) | 0.512 | 0.512 | 0.512 | 0.517 | 0.569 | 0.661 |
| Greater Weddell | Vegetation cover (DEA) | −0.033 | −0.033 | −0.034 | 0.009 | 0.024 | 0.023 |
| Greater Weddell | Convertibility | 0.197 | 0.213 | 0.252 | 0.265 | 0.267 | 0.158 |
| Greater Weddell | Protection | 0.076 | 0.083 | 0.023 | 0.025 | 0.029 | 0.064 |
| Greater Weddell | Land-system rarity | −0.096 | −0.118 | −0.130 | −0.059 | −0.032 | −0.064 |
| Greater Weddell | Vegetation-type rarity (NVIS) | 0.233 | 0.276 | 0.409 | 0.385 | 0.382 | 0.393 |

**Appendix S1. Surrogate construction.** Convertibility scores by Australian Land Use and Management
primary class: conservation and natural environments 0.1; production from relatively natural
environments 1.0; dryland agriculture and plantations 0.4; irrigated agriculture 0.2; intensive uses
0.0; water missing. NVIS Major Vegetation Group codes treated as missing: 25 (cleared, non-native
vegetation, buildings), 27 (naturally bare), 28 (sea and estuaries) and 99 (unknown). Surrogate values
are rounded to four decimal places before analysis. Each surrogate is analysed on the polygons where
it is defined (pairwise deletion). Polygons coded 0 (not assessed) or 9 (water) are excluded.

**Appendix S2. Analysis plan and departures, with dates.** The research log records the co-primary
estimands (P3.PR1) and the confirmatory specification (P3.PR2) before the confirmatory runs. The
project was first committed to version control on 14 July 2026, with the log and the confirmatory
results in the same commit. Departures, all described in Section 2.8:

- July 2026, before the first commit: the spatial block bootstrap replaced the pre-specified
  nearest-neighbour effective sample size; the joint model and its cross-validation were added after
  the single-surrogate results.
- 3 October 2026 (pre-submission audit): rounding of overlay values to four decimal places; paired
  comparisons of the joint model and of the two rarity surrogates; Hartung–Knapp–Sidik–Jonkman
  intervals; area-weighted mid-ranks; the multiverse and mechanism analyses (exploratory).
- 4 October 2026 (final run): the Roper benchmark read from the published layer instead of an
  earlier intersection with the land-use map; BIORISK class definitions checked against each
  dataset (Appendix S3).

**Appendix S3. BIORISK class definitions by dataset,** from each dataset's attribute fields and
class-description tables (`data/meta/P4_DATA_CHECKS.md`). All five use codes 1–5 in the same order,
0 for not assessed and 9 for water.

| Class | Roper (2024) | Larrimah (2021) | Wadeye (2021) | Gunn Point (2020) | Deep Well (2021) |
|---|---|---|---|---|---|
| 1 | Nil: highly modified | Nil: highly modified* | Nil: highly modified* | Nil: highly modified | not present |
| 2 | not present | Low: no significant biodiversity value* | Low: no significant value | Low: no significant biodiversity value | Low: no significant biodiversity value |
| 3 | Mitigable: apply the mitigation hierarchy | Mitigable: apply land management strategies | Mitigable* | Uncertain: requires further biodiversity assessment | Mitigable: apply land management strategies |
| 4 | Moderate: sensitive or significant vegetation, including groundwater-dependent ecosystems, or species of conservation interest | Moderate: sensitive or significant vegetation, or species of conservation interest | Moderate: sensitive or significant vegetation, or species of conservation interest | Moderate: sensitive or significant vegetation types | Moderate: sensitive or significant vegetation, or species of conservation interest |
| 5 | High: significant vegetation community and/or threatened-species habitat | High* | High: significant vegetation community and/or threatened-species habitat | High: significant vegetation community in combination with threatened-species records | not present |

\* Defined in the dataset's class-description table but not present among its polygons.
