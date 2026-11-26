# Project E findings (claim → number → run)

All from `e04_eval_20261110_01` (scores `e03_cd5_20261110_01`, populations `e02_pop_20261110_01`, SPEC v1) unless stated. Mean differences are retracted − matched controls within journal × year, weighted by retracted papers, 95% bootstrap CI over strata. ORs are Mantel–Haenszel within journal × year.

## RQ1 (4,587 scored primary papers; 4,586 compared in 2,239 strata)
- Mean CD5: retracted −0.00217, controls −0.00236; **difference 0.00020 [−0.00061, 0.00109]**; a small estimated gap.
- CD5 > 0: 924/4,587 retracted vs 9,755/52,122 controls; **OR 1.23 [1.13, 1.34]**. (The control count and share here,
  and in the two RQ3 lines below, are over all scored controls of the population, including strata without a
  primary-set paper; the paper uses the like-for-like shares of P11 since v0.3.)
- RQ3, top 5% of the year (context-sample threshold): 3.1% [2.6, 3.6] vs 4.05% [3.9, 4.2] (all controls; P11: 3.1%
  [2.8, 3.5]); **OR 0.99 [0.83, 1.20]**.
- RQ3, top 1%: 17/4,587 = 0.37% [0.23, 0.59] vs 0.73% [0.66, 0.80] (all controls; P11: 0.54% [0.43, 0.66]); **OR 0.67
  [0.40, 1.12]**.

## RQ2 (primary set by reason class)
| Class | n | Diff [CI] | OR CD5>0 [CI] | OR top 5% [CI] | Top 1% (retracted) |
|---|---|---|---|---|---|
| Misconduct | 2,742 compared | 0.00032 [−0.00021, 0.00082] | 1.29 [1.15, 1.44] | 0.93 [0.71, 1.22] | 5 (0.18%) |
| Paper mill | 276 | 0.00058 [−0.00014, 0.00123] | 1.20 [0.93, 1.57] | 1.10 [0.53, 2.29] | 0 |
| Honest error | 294 | −0.00408 [−0.00768, −0.00073] | 1.15 [0.82, 1.60] | 1.02 [0.55, 1.88] | 2 |
| Other | 1,274 | 0.00084 [−0.00172, 0.00397] | 1.18 [1.02, 1.36] | 1.06 [0.79, 1.41] | 10 |

## Pre-specified robustness (primary set unless noted)
| Check | Diff [CI] | OR CD5>0 | OR top 5% |
|---|---|---|---|
| (a) without CD5 = 1 | 0.00005 [−0.00050, 0.00059] | 1.23 [1.13, 1.33] | 0.99 [0.82, 1.19] |
| (b) without reviews | 0.00014 [−0.00074, 0.00118] | 1.23 [1.12, 1.34] | 0.98 [0.81, 1.19] |
| (c) + reference-count deciles in strata | 0.00123 [0.00039, 0.00223] | 1.38 [1.24, 1.53] | 1.47 [1.15, 1.88] |
| (d) window [t+1, t+5] | 0.00031 [−0.00063, 0.00135] | 1.24 [1.14, 1.35] | 1.01 [0.84, 1.21] |
| (e) all retracted (10,448) | 0.00144 [0.00078, 0.00221] | 1.50 [1.42, 1.58] | 1.00 [0.90, 1.12] |
| (f) ≥ 5 citations in window | 0.00062 [0.00007, 0.00115] | 1.28 [1.17, 1.41] | 1.09 [0.88, 1.35] |

## Context (random 0.2% biomedical sample, 2000–2017; not a contribution)
- Mean CD5 per year stays between −0.0049 and 0.0009 (`context_by_year.csv`); CD5 = 1 share ≤ 0.3% in every year, because zero-reference records are excluded.

## Reading (draft; to be checked in self-review)
- In the pre-specified five-year comparison, retracted papers have a small mean gap and **no unadjusted top-tier excess**; they are slightly more often on the positive side of zero (OR ≈ 1.2–1.3), a small shift around a score that is near zero for almost all papers.
- When reference length is held fixed (c), retracted papers look somewhat more disruptive (top-5% OR 1.47): they tend to have reference lists that differ in length from their controls. To examine (post hoc: reference counts by group).
- Including papers retracted inside the window (e) raises OR(CD5>0) to 1.50, consistent with retraction itself changing later citations (the reason for the primary-set rule).
- Paper-mill papers are few in this window (276); the paper-mill question mostly needs post-2017 papers, which lack a full 5-year window in the Jan 2024 graph.

# Post hoc (POSTHOC.md; not in SPEC v1)

## P1 reference length (`e05_refs_20261110_01`)
- Median references: retracted (primary) 40, full control pool 35, context 30; within journal × year the difference in
  log(1 + group arithmetic mean) is −0.017. This is not evidence of balance in mean paper-level log references (P12).
- Median window citations: retracted (primary) 19, full control pool 13; within strata +0.099 in log(1 + group mean).
- CD5 correlates negatively with reference count (Spearman −0.19) and with window citations (−0.43) in the context sample.

## P2 three-year window, papers 2000–2019 (`e04_eval_cd3_20261110_01`)
There are 7,349 scored primary papers and 7,348 compared papers. The table's n is the compared count.
These post hoc top-tier estimates lean toward a modest excess; they do not all match the five-year result.
| Set | n | Diff [CI] | OR CD3>0 | OR top 5% | OR top 1% |
|---|---|---|---|---|---|
| Primary (retracted after pub_year + 3) | 7,348 | 0.00039 [−0.00027, 0.00114] | 1.30 [1.22, 1.39] | 1.12 [0.98, 1.28] | 0.89 [0.63, 1.28] |
| Misconduct | 4,171 | 0.00045 [−0.00019, 0.00119] | 1.42 [1.31, 1.55] | 1.17 [0.97, 1.41] | 1.00 [0.62, 1.63] |
| Paper mill | 708 | 0.00039 [−0.00009, 0.00082] | 1.12 [0.95, 1.32] | 1.23 [0.83, 1.81] | 0 of 708 |
| Honest error | 615 | −0.00267 [−0.00429, −0.00117] | 1.22 [0.97, 1.54] | 0.88 [0.55, 1.41] | 2 of 615 |
| Other | 1,854 | 0.00128 [−0.00074, 0.00355] | 1.22 [1.08, 1.38] | 1.10 [0.87, 1.40] | 1.06 [0.60, 1.87] |
| (c) + reference deciles | 5,941 | 0.00126 [0.00052, 0.00202] | 1.33 [1.23, 1.44] | 1.46 [1.23, 1.73] | 1.45 [0.92, 2.28] |
| (e) all retracted | 13,653 | 0.00127 [0.00067, 0.00190] | 1.54 [1.47, 1.61] | 1.16 [1.06, 1.26] | 0.88 [0.70, 1.11] |
| (f) ≥ 5 citations | 5,863 | 0.00078 [0.00023, 0.00136] | 1.39 [1.29, 1.49] | 1.32 [1.12, 1.56] | 1.13 [0.68, 1.89] |

## P13 article-type sensitivity (`e13_articles_20261126_01`)

Planned in POSTHOC.md before the run. Original CD5/CD3 primary estimates and all six P7 models reproduced, with
frozen score/label hashes and original review flags checked. Both groups require Journal Article, with any linked
review/editorial/notice type excluded; Retracted Publication is retained. Thresholds/control draw stay fixed.

| Window | Eligible / scored / compared retracted | Compared controls / strata | Mean CD gap [95% CI] | Positive OR [95% CI] | Top-5% OR [95% CI] |
|---|---|---|---|---|---|
| CD5 | 3,528 / 3,528 / 3,521 | 23,839 / 1,841 | 0.000761013 [-0.000218134, 0.001886385] | 1.244691 [1.131045, 1.369756] | 1.072056 [0.861843, 1.333544] |
| CD3 | 5,600 / 5,599 / 5,592 | 37,334 / 2,735 | 0.000871718 [0.000183705, 0.001694908] | 1.322477 [1.229414, 1.422585] | 1.213136 [1.035646, 1.421045] |

- CD5 matched mean log reference gap +0.064059 [0.045366, 0.083135], with means 3.626294 and 3.562235;
  log-of-stratum-mean reference gap +0.005866. Mean log citation gap +0.265192 [0.233241, 0.299106].
- CD5 top-5% conditional logit: unadjusted 1.073582 [0.862298, 1.336636], reference-adjusted
  1.639967 [1.279035, 2.102752], both covariates 1.394909 [1.078519, 1.804114].
  Each uses 1,524 retracted papers in 383 outcome-varying strata.
- DI_nok gaps: CD5 +0.073527 [0.048851, 0.097828], 3,471 compared; CD3 +0.082218 [0.062421, 0.102031],
  5,413 compared. All reason-class estimates are in windows.*.by_class and Appendix Table A.1.
- Publication-type restriction retains the imbalance and adjusted excess; it changes both groups and does not
  isolate a causal mechanism. The broad Journal Article category is not guaranteed to mean original research.

# Inherited from Project D (cited as data-preparation facts)
- Retraction Watch → graph: 52,254 of 62,735 retracted papers matched (83.3%) by DOI or PMID (`d05_match_20261101_02`, D repository `retracted-neighbours-open-data`); 53,170 matched graph nodes (also `e02_pop_20261110_01`: rw_matched_iids 53,170).
- The January 2024 graph is effectively complete to about September 2023 (`d00_cutoff_20261101_01`).
- Retraction Watch snapshot: commit a98cc7e (30 Oct 2026), 62,735 retracted papers (`d02_rw_20261101_01`).
- Paper-mill retractions in the snapshot: 11,716 papers; by notice year 2016–2019: 2, 3, 4, 4; 2020: 246; 2021: 815; 2022: 934; 2023: 6,782; 2024: 1,805; 2025: 1,115 (`d02_rw_20261101_01`).

# Post hoc round 2 (POSTHOC.md P3–P8; run `e08_posthoc2_20261123_02` on `e07_yearly_20261123_02`; the replay of v1 is exact)

## P3 historical margins and interval bounds (margins fixed in POSTHOC.md before the run)
- Margin for mean differences: ±0.1 SD of the score in the reference sample: CD5 ±0.00442 (SD 0.0442); CD3 ±0.00442.
- CD5 primary: difference 0.00020, **90% interval −0.00051 to 0.00093**; absolute-difference bound 0.00093.
- CD5 primary, top 5%: OR 0.99, **90% 0.85–1.16**. Top 1%: 0.67, 90% 0.44–1.03.
  CD5 > 0: 1.23, 90% 1.15–1.32.
- CD3 primary: difference 90% −0.00017 to 0.00101; top 5% 1.12, 90% 1.00–1.25.
- By class (CD5), mean-difference 90% intervals: misconduct −0.00010 to 0.00074, paper mill 0.00001 to 0.00111,
  other −0.00127 to 0.00343, honest error −0.00699 to −0.00123.
- v0.5 drops equivalence conclusions: the conventional mean margin exceeds the review effect, and the paper-mill
  90% interval lies entirely above zero. Original TOST outputs remain unchanged in the archived JSON.

## P4 positive control: reviews vs other never-retracted papers (same journal × year; CD5 controls)
- 6,032 reviews (4,832 in 2,083 usable strata) vs 46,090: CD5 difference **−0.00329 (−0.0066 to −0.0011)**
  (−0.074 SD); top 5% OR **0.58 (0.47–0.72)**; top 1% 0.39 (0.21–0.73); CD5 > 0 0.95 (0.86–1.04).
- The retracted papers' 90% interval excludes mean differences above 0.00093, about 28% of the review gap.
- Reviews versus other controls: positive-CD5 OR **0.947024745 (0.860810156–1.041874171)**, 4,832 compared reviews;
  mean DI_nok difference **−0.076072618 (−0.194619308–0.033042631)**, 4,736 compared reviews. Both intervals
  include the null. These are Figure 1's review sign and DI_nok panels, now also reported in text and Table 3.

## P5 DI_nok = (n_i − n_j)/(n_i + n_j)
- CD5 window, primary (4,518 defined, **4,517 compared**): retracted −0.309, controls −0.376,
  **difference +0.067 (0.046–0.087)**. Share of citing papers that also cite a reference:
  (1 − DI_nok)/2 ≈ 0.655 vs 0.688.
- By class: misconduct +0.083 (0.058–0.109); other +0.049 (0.019–0.078); paper mill +0.054 (−0.003 to 0.120);
  honest error +0.004 (−0.056 to 0.060). CD3 window, primary (7,125 defined, **7,122 compared**):
  +0.075 (0.056–0.093); paper mill +0.056
  (−0.008 to 0.122).
- Top-tier thresholds of DI_nok are degenerate (95th and 99th percentiles = 1.0 in every year); papers at DI_nok = 1:
  retracted 2.5% vs controls 4.9% (OR 0.59, 0.48–0.72) — not interpreted as a top-tier result.
- Note: sign(CD) = sign(DI_nok) for cited papers, so OR(CD5 > 0) is the DI_nok shift seen through the sign.

## P7 the sign shift and robustness (c) (CD5 primary)
- No citing paper in the window: 1.5% of retracted vs 4.0% of controls (MH OR 0.43, 0.33–0.56).
- Cited papers only: OR(CD5 > 0) **1.20 (1.11–1.31)**.
- Conditional logit, strata journal × year: CD5 > 0: 1.23 (1.14–1.34) unadjusted; **1.32 (1.21–1.44)** + log(1 +
  references); 1.32 (1.21–1.43) + log(1 + window citations). Top 5%: 0.99 (0.83–1.20) unadjusted; **1.42 (1.16–1.75)**
  + log(1 + references); 1.19 (0.96–1.47) + log(1 + window citations). Reference coefficient −1.64 (top 5%).
- Reading: the adjusted top-tier comparison is sensitive to reference length. P12's matched mean-log imbalance
  supports the direction of the shift; P1's pooled lower quartiles (29 vs 22) are not matched evidence.

## P8 editorial-notice citations (retraction notices, errata, expressions of concern; PubMed types/links)
- ≥ 1 notice citation in the CD5 window: retracted after the window 18.4% (844/4,587); retracted inside the window 36.7%
  (2,151/5,863); controls 4.7% (2,456/52,147); reference sample 3.0%.
- Without notice citations: primary unchanged (difference 0.00029; CD5 > 0 1.24; top 5% 1.02); all retracted
  (robustness e) CD5 > 0 **1.50 → 1.35 (1.28–1.42)**; retracted inside the window only **1.71 → 1.44 (1.34–1.54)**.

## P6 before and after the retraction (CD3 population 2000–2019; notices excluded)
- 7,899 retracted papers with t+1 ≤ R ≤ 2021; 5,100 with a defined change and controls (2,842 strata).
- DI_nok change after vs before (R−3…R−1 vs R+1…R+3): retracted +0.174, controls +0.100; **DiD +0.074 (0.050–0.097)**;
  with notices +0.074. By class: honest error +0.124 (0.075–0.173); misconduct +0.090 (0.061–0.121); other +0.020
  (−0.028 to 0.067); paper mill +0.039 (−0.052 to 0.132).
- Citing papers per year, before → after: retracted 3.94 → 2.61; controls 3.10 → 4.69.

# Post hoc round 3 (POSTHOC.md P9; run `e09_pretrend_20261123_01`)
- Papers with R ≥ t + 4: real DiD **+0.064 (0.037–0.093)** (2,763); **placebo at R − 3: +0.036 (0.012–0.060)** (2,565).
  Honest error: real +0.079 (0.012–0.149), placebo +0.005 (−0.065 to 0.077). Misconduct: real +0.078 (0.041–0.115),
  placebo +0.042 (0.010–0.074).
- Balanced event time (3,083 papers): paired gap in DI_nok 0.053 (τ = −3), 0.072, 0.089, 0.092 (τ = 0), 0.123, 0.201,
  0.151 (τ = +3). Citing papers per year, retracted vs controls: 5.4 vs 4.0 (τ = −3), 6.3 vs 4.8 (τ = −2), 3.6 vs 4.8
  (τ = +1), 2.3 vs 4.5 (τ = +3).
- Reading: the divergence starts before the notice and steepens after it; part of the post-notice change continues an
  earlier trend (strongest for misconduct, absent for honest error).

## P10 size of n_k (`e10_nk_20261123_01`, descriptive)
- Median paper (CD5 window): n_k 2,862, citing papers 12; n_k is 99.6% of the denominator (median); ≥ 90% for 97.9% of
  papers, ≥ 99% for 71.3%. Controls: median n_k 3,158, citing 13; retracted primary: 4,481, 19.

## Counts used in the paper's text and tables (from the run records)
- RQ1: 4,586 of the 4,587 primary-set papers are in the 2,239 strata with scored controls (`e04_eval_20261110_01`, `retracted_in_used_strata`).
- RQ1 positive scores in those comparison strata: 923/4,586 (20.1%), versus 924/4,587 over all primary-set papers
  (`e11_controls_20261126_01`, `controls.json`, `cd5.shares.pos.retracted_used_strata` and
  `retracted_all_primary_v1`). The unmatched paper does not contribute to the within-stratum estimates.
- P7: the conditional logit for CD5 > 0 uses 3,766 retracted papers (strata with outcome variation); for the top 5%, 2,168 (`e08_posthoc2_20261123_02`).
- P7: CD5 > 0 with both log references and log window citations: OR 1.31637, 95% CI 1.20953–1.43266, reported as
  **1.32 (1.21–1.43)** (`e08_posthoc2_20261123_02`, `P7_sign_shift.clogit.pos_refs_cites`).
- P8: papers retracted inside the window: 5,861 scored / **5,858 compared** with notice records,
  5,860 scored / **5,857 compared** without (`e08_posthoc2_20261123_02`, `P8_notices.inside_window_only_*`).

# Post hoc round 4 (POSTHOC.md P11, descriptive; run `e11_controls_20261126_01`; every e04 value used reproduced exactly)
- Controls were drawn for all retracted papers of a population; a comparison uses the controls in the strata of the
  compared papers. CD5: 52,147 controls (52,122 scored) for 10,450 retracted papers in 5,458 strata; the primary set's
  2,239 used strata hold **31,674 controls, 31,662 scored** (the comparison group of RQ1–RQ3); the other 3,219 strata
  hold 20,473. CD3 (P2): 68,190 controls for 13,661 retracted papers; the 3,308 used strata hold **48,069, 48,044 scored**.
- Undefined scores have n_i + n_j + n_k = 0 (checked for every paper). CD5: 46 papers = 25 controls (12 in the used
  strata) + 2 retracted inside the window + 19 reference sample. CD3: 79 papers = 44 controls + 1 primary + 2 secondary +
  32 reference sample.
- Like-for-like shares (controls weighted by the scored primary-set papers per stratum, as the SPEC mean difference;
  95% bootstrap over strata), retracted vs controls. CD5: score > 0 20.1% vs **17.3% (16.0–18.6)**; top 5% 3.1% vs
  **3.1% (2.8–3.5)**; top 1% 0.37% vs **0.54% (0.43–0.66)**. CD3: > 0 22.3% vs 18.4% (17.4–19.6); top 5% 3.8% vs
  3.4% (3.1–3.8); top 1% 0.50% vs 0.56% (0.46–0.66).
- Pooled shares of the controls in strata without a primary-set paper (CD5): > 0 19.7%, top 5% 5.2%, top 1% 0.99%; this
  is the main reason why the all-controls shares of v1 (18.7%, 4.05%, 0.73%) differ from the like-for-like shares
  (the rest is the weighting: pooled shares in the used strata are 18.1%, 3.3%, 0.56%).

## Event-figure estimands clarified in v0.4 (same P9 run; no new estimates)
- v0.4 Figure 2 plotted `dinok_ret` and `dinok_ctl`, each a mean over its own defined annual scores. At tau = -3, 0, +2,
  their differences are 0.04809, 0.07358, 0.18485.
- The text's 0.05281, 0.09228, 0.20150 are `paired_diff`: means over pairs with both scores defined. These are not
  differences of separately averaged curves; the paired subsets contain 2,220, 2,440 and 1,982 papers, respectively.
- Both use the 3,083-paper event-time population. The 5,100-paper P6 window comparison and its 3.10 to 4.69 control
  citation change are separate; Figure 2's balanced controls instead have means from 4.04 to 4.93 per year.
- P1's -0.017 and 0.099 are differences of **log(1 + the within-stratum group mean)**, not means of paper-level
  log(1 + counts), as verified in `e05_refs.py`. v0.5 retains this in the appendix and adds P12's distinct statistic.

## P12 paired annual intervals and matched mean-log counts (`e12_diag_20261126_01`)
Frozen input hashes checked; all seven P9 paired points/counts, P11's 4,586 / 31,662 comparison population and both
P1 log-of-mean points reproduced before new calculations. Seed 20261109, 2,000 journal-year bootstrap resamples.
- Mean log(1 + references): retracted **3.641801947**, matched controls **3.557478452**;
  difference **+0.084323495 (0.058004811–0.109042910)**.
- Mean log(1 + window citing papers): **2.956958933** vs **2.646093595**;
  difference **+0.310865338 (0.279558768–0.341075849)**.
- Figure 2 now plots `paired_event.csv`: tau -3 **0.052810085 (0.020407792–0.082910556), n=2,220**;
  tau 0 **0.092282431 (0.059448072–0.124484299), n=2,440**;
  tau +2 **0.201497208 (0.161588681–0.241737852), n=1,982**.
- Label inputs contain no author-identifier columns; no author-cluster or largest-retractor check was performed.
  The limitation is stated, and the VM was deallocated immediately after the run and checksum-verified fetch.

## v0.6 accounting and scope clarification (no analysis rerun)
- Scored-paper count: 10,450 retracted + 52,147 controls + 24,491 reference-sample memberships = 87,088;
  E2's DISTINCT focal list has 86,950 papers, reconciling 138 overlaps with the reference sample.
  E2's disjoint retracted/control construction and group/focal counts support the reconciliation.
- CD3 mean differences are distinct before rounding: overall **0.000390019384**, paper mill **0.000393714743**;
  both correctly print as 0.00039. Their original confidence intervals are unchanged.
- E2 imposes no publication-type eligibility filter. Reviews are flagged, not excluded from the main controls;
  editorial, letter, comment and notice items can qualify. No research-article-only rerun is performed.
- Retraction Watch's raw CSV has an `Author` field (D2 run metadata); processed diagnostic labels omit it.
  A raw-name exclusion is possible but not performed. The author requested manuscript-only changes and no VM restart.

## P14 author-name exclusion (`e14_authors_20261126_01`; v0.8)

POSTHOC.md plan precedes execution; raw CSV/D2 hashes, D2 key/reinstatement counts and frozen score/label hashes
verified. D5 mapping hash recorded and unchanged during the join. Original CD primary points/intervals/positive
and top-5% odds ratios/retracted comparison counts and P5 DI_nok points/counts reproduced first.
Aggregate outputs only; no author-name strings, identifiers or paper-name associations released.

| Quantity | CD5 | CD3 |
|---|---|---|
| Primary papers removed (all have linked names) | 2,280 / 4,587 | 3,722 / 7,350 |
| Retained eligible / scored / compared | 2,307 / 2,307 / 2,306 | 3,628 / 3,627 / 3,626 |
| Compared controls / strata (CD) | 23,999 / 1,363 | 37,294 / 2,115 |
| Mean CD gap, 95% CI | 0.000270349 (-0.001132407, 0.001948257) | 0.000633389 (-0.000474505, 0.001839628) |
| Positive-score OR, 95% CI | 1.259203 (1.122322, 1.412778) | 1.320564 (1.207766, 1.443897) |
| Top-5% OR, 95% CI | 0.969281 (0.750257, 1.252244) | 1.032776 (0.850834, 1.253625) |
| DI_nok gap, 95% CI | 0.060765180 (0.037890014, 0.083505447) | 0.068509649 (0.048250237, 0.089267319) |
| DI_nok compared papers / controls / strata | 2,260 / 23,161 / 1,327 | 3,485 / 35,081 / 2,020 |

Source: `results.json.windows.cd5/cd3`; all reason-class CD/DI_nok points, intervals, ORs and counts are in
`by_class`, and Table A.2 uses those mean contrasts. `author_summary`: 62,734 non-reinstated paper keys,
62,621 with names, 174,990 normalized names, 1,649 names at >=10 keys, 22,028 excluded keys.
The DI_nok gap persists; the shorter-window top-tier excess weakens under this restriction.
Names are not disambiguated identities and the bootstrap remains journal-year.

v0.8 interpretation: P12/P13 overall mean-log reference differences establish direction, not the magnitude of the
adjusted OR changes or a causal explanation. The manuscript drops P1's log-of-stratum-mean quantities; original
run records and their distinct statistics remain intact here. Reported differences are computed before rounding.
Primary CD5 means are -0.002165233620 and -0.002363267049, yielding +0.000198033428.

## v0.9 wording, accounting and source clarification (no analysis rerun)

- A.3 uses P8 `retracted_in_used_strata`: **5,858 / 5,857 compared**, not the **5,861 / 5,860 scored**
  counts in `retracted_defined`. The all-retracted no-notices positive-score CI is
  **1.282206215528376–1.42493183279939**, printed **1.28–1.42**, from current run _02.
- Citing papers in A/B come from the whole OpenCitations edge table, joined to the full parsed publication table
  for known years; PubMed/journal rules apply only to focal eligibility. Evidence:
  `experiments/e03_cd5/e03_cd5.py` passes C's `edges.parquet` and `pubs_slim.parquet` to `cd_lib.build_inputs`;
  `cd_lib.py` joins citing IDs to publication years without biomedical or journal filtering.
  Thus the median n_k = 2,862 counts reference-only citing papers across the graph, not just biomedical citers.
- The composition wording now explicitly concerns whether a citing paper also cites references, not how often
  it cites the focal paper: **65.5% vs 68.8% for controls** (unchanged P5 results).
- Figure run `e06_fig_20261126_07` changes review-row spacing only; Figure 2 is byte-identical to _06.
  Identified-only JOI source and persistent upload instructions retain the author and GitHub link.
