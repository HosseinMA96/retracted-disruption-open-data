# Post hoc analyses (added 2026-11-10, after seeing e04_eval_20261110_01)

Not in `SPEC.md` v1 (whose SHA-256 is recorded in the v1 runs and is left unchanged). Everything here is reported as **post hoc**.

1. **P1 reference length.** Robustness (c) (reference-count deciles inside strata) moved the estimates (top-5% OR 0.99 → 1.47). P1 describes reference counts and window citations by group and class (median, IQR, within-stratum mean difference in log reference count), and the Spearman correlation of CD5 with reference count in the context sample. Script `e05_posthoc/e05_refs.py`.
2. **P2 three-year window (CD3), papers 2000–2019.** Most paper-mill papers were published after 2017, so the 5-year window leaves only 276 in the primary set. P2 reruns E2–E4 unchanged except last publication year 2019 and window 3 years (primary set: first notice after 31 Dec of pub_year + 3). Runs `e02_pop_cd3_*`, `e03_cd5_cd3_*` (scores named cd_w0 but the window is [t, t+3]), `e04_eval_cd3_*`.

# Post hoc round 2 (written 2026-11-23, BEFORE any of the runs below; after seeing all v1, P1 and P2 results)

Motivation: reviewer risks recorded in `TODO.md` on 2026-11-10 (null result without an equivalence test or a positive
control; scores bunched near zero because n_k dominates; robustness (c) unexplained; why scores shift when retractions
fall inside the window). The user approved the strengthening plan on 2026-11-23 ("drive them to completion").
Everything below is **post hoc** and is reported as such. SPEC.md v1 is not changed. Margins, windows, populations and
expected directions are fixed here, before the numbers exist. Seeds: `SeedSequence(20261109)`, 2,000 bootstrap draws
over journal × year strata, as in SPEC §6.

3. **P3 equivalence (two one-sided tests).** For the primary set (CD5) and the P2 primary set (CD3), overall and by
   reason class:
   - mean difference (retracted − controls): equivalence margin ±0.1 × SD of the score in the reference (context)
     sample of the same population (a standardized difference of 0.1, half of Cohen's "small"); equivalence at
     α = 0.05 if the 90% bootstrap interval (5th–95th percentiles of the same 2,000 draws that give the 95% interval)
     lies inside the margin;
   - Mantel–Haenszel odds ratios (score > 0, top 5%, top 1%): margin 0.80–1.25 (the conventional ratio equivalence
     range); equivalence if the 90% interval (log scale, Robins–Breslow–Greenland SE) lies inside; TOST p-value =
     larger of the two one-sided p-values;
   - also reported: the smallest symmetric margin that the data would support (max |90% bound| for the difference;
     max(upper, 1/lower) of the 90% interval for odds ratios), so readers can apply their own margin.
   The script first reproduces the v1 primary estimates (difference, 95% interval, odds ratios) exactly and stops if
   they differ.
4. **P4 positive control: reviews.** Among the never-retracted controls of the CD5 population, reviews (PubMed types
   Review, Systematic Review, Meta-Analysis; the SPEC robustness (b) flag) are compared with non-review controls of the
   same journal × year, with the RQ1/RQ3 estimators (stratified mean difference, MH odds ratios for score > 0 and top
   5%). **Expected before running:** reviews are more consolidating (negative difference, odds ratios below 1), because
   papers that cite a review often also cite the work it reviews (large n_j). Purpose: show that the design and sample
   sizes detect a contrast expected from the construction of the index; its size is compared with the P3 margin.
   Also computed with DI_nok (P5).
5. **P5 DI_nok.** DI_nok = (n_i − n_j)/(n_i + n_j), the variant without n_k, from the frozen counts (CD5 window
   [t, t+5]; CD3 window [t, t+3]); defined for papers with at least one citing paper in the window. RQ1–RQ3 for the
   primary sets (CD5 and CD3), overall and by class, with thresholds = 95th/99th percentiles of DI_nok per publication
   year in the reference sample. Ties at ±1 mean that shares above a threshold can exceed the nominal 5%/1%.
6. **P6 before and after the retraction (difference in differences).** New label-free count run **e07**: for every
   focal paper of `e02_pop_cd3_20261110_01` (2000–2019; contains the CD5 population) and every citing year
   y = t … 2023, the numbers of citing papers that do not / do also cite at least one reference of the focal paper
   (n_i^y, n_j^y), and the same counts for citing records that are editorial notices (P8). Same rules as `cd_lib`
   (no self-loops, citing paper must have a year). e07 checks that its yearly counts summed over [t, t+3], [t+1, t+3]
   and (papers ≤ 2017) [t, t+5] equal the frozen counts of `e03_cd5_cd3_20261110_01` and `e03_cd5_20261110_01`
   exactly, and its output is hashed before e08 joins labels.
   - Population: all non-reinstated retracted papers of the CD3 population with retraction year R (year of the first
     notice) satisfying t + 1 ≤ R ≤ 2021; controls = the controls of the same journal × year stratum, evaluated at
     the same R.
   - Windows: before = citing years max(t, R−3) … R−1; after = R+1 … min(R+3, 2022). Year R itself is excluded.
     Main analysis excludes notice citations; sensitivity includes them.
   - Per paper: DI_nok on each window (needs ≥ 1 citing paper in the window); Δ = DI_nok(after) − DI_nok(before).
     Estimate = mean over retracted papers of [Δ_r − mean Δ of their stratum's controls at R_r]; retracted papers
     without a control with defined Δ are dropped and counted; 95% interval by bootstrap over strata. Also by reason
     class.
   - Descriptive: citing papers per window (before/after) by group (sanity check: retracted papers are expected to
     lose citations after the notice relative to controls); event-time means of yearly DI_nok for τ = y − R from −5
     to +5 (papers with ≥ 1 citing paper that year), retracted vs their stratum controls, for a figure.
   - **Expected before running:** DI_nok rises after the retraction relative to controls (citers cite the paper
     without its references), in line with robustness (e).
7. **P7 the sign shift and robustness (c).** On the CD5 primary set:
   (a) share of papers with no citing paper in the window (score exactly 0 by construction when n_k > 0), MH odds
   ratio retracted vs controls; (b) MH odds ratio for CD5 > 0 among papers with ≥ 1 citing paper in the window;
   (c) conditional logistic regression with strata = journal × year (all primary-set papers in strata with controls)
   for CD5 > 0 and for the top 5%, covariate log(1 + reference count); a second model adds log(1 + citing papers in
   the window). These are compared with SPEC robustness (c), which kept only the 3,664 of 4,587 retracted papers that
   had a control in the same reference-count decile.
8. **P8 editorial-notice citations.** A citing record is an editorial notice if its PubMed record has publication type
   "Retraction of Publication", "Published Erratum" or "Expression of Concern", or a comments/corrections link
   RetractionOf, ErratumFor or ExpressionOfConcernFor (attributes of the citing record only; computed in e07 for all
   focal papers alike). Reported: (a) share of papers with ≥ 1 notice citation in the CD5 window, for retracted papers
   retracted inside vs after the window and for controls; (b) robustness (e) (all retracted) and the primary analysis
   recomputed with notice citations removed from n_i, n_j and n_k; (c) P6 with and without notice citations.
   - **Amendment (2026-11-23, after run `e07_yearly_20261123_01`, before any P8 result was read):** in the PubMed 2026
     baseline, publication type D016440 is named "Retraction Notice" (the name "Retraction of Publication" used above
     no longer occurs), so the name-based rule caught retraction notices only through their RetractionOf links. The
     rule is now applied to publication-type identifiers: D016440 (Retraction Notice), D016425 (Published Erratum),
     D000075742 (Expression of Concern), plus the same three links. Same intent, same three notice types. Reruns:
     `e07_yearly_20261123_02`, `e08_posthoc2_20261123_02`; the `_01` runs are kept for the record and not used.

# Post hoc round 3 (written 2026-11-23, after reading `e08_posthoc2_20261123_02`, before running anything below)

9. **P9 pre-trend check of P6.** The P6 event-time table shows that the DI_nok gap between retracted papers and their
   controls already widens before the notice (paired difference 0.06 at τ = −5, 0.12 at τ = −1). Two checks, same
   population, data (`e07_yearly_20261123_02`, notices excluded), estimator and bootstrap as P6:
   (a) **placebo event** at F = R − 3: before = citing years max(t, F−3) … F−1, after = F+1 … R−1 (two years, all
   before the notice); papers with R ≥ t + 4. The real P6 difference in differences is recomputed on the same papers
   for comparison. If the real change around the notice is a continuation of the earlier trend, the placebo estimate
   will be of similar size;
   (b) **balanced event time:** the P6 event-time means restricted to retracted papers whose years τ = −3 … +3 are all
   inside [t, 2022] (R ≥ t + 3 and R ≤ 2019), so that the set of papers that can contribute does not change with τ.
10. **P10 size of n_k (descriptive, 2026-11-23, before running).** Quantiles of n_k, of n_i + n_j and of the share
    n_k / (n_i + n_j + n_k) in the CD5 window, for all scored papers and by group (retracted primary set, controls,
    reference sample), from the frozen scores of `e03_cd5_20261110_01`. Purpose: to state how much n_k dilutes the
    index, instead of asserting it.

# Post hoc round 4 (written 2026-11-26, before running anything below; after reading all results above)

11. **P11 the controls behind the primary comparisons (descriptive).** Controls were drawn for every retracted paper of
    a population, primary and secondary sets together (SPEC: five per retracted paper within journal × year), and each
    comparison uses the controls of the strata that contain papers of the compared set (e04 `compare()`: inner join of
    strata for the mean difference; strata without a compared paper add nothing to a Mantel–Haenszel odds ratio). The
    v0.2 text paired the primary set with the whole control pool (52,147 controls; CD3: 68,190), and the control shares
    it quoted next to the stratified odds ratios (positive score 18.7%, top 5% 4.05%, top 1% 0.73%; e04 `mh_*`
    `control_n` and `share_top_*_controls`) were taken over all scored controls, including strata without a primary-set
    paper. For the primary set of each window (CD5: `e02_pop_20261110_01`, `e03_cd5_20261110_01`,
    `e04_eval_20261110_01`; CD3: `e02_pop_cd3_20261110_01`, `e03_cd5_cd3_20261110_01`, `e04_eval_cd3_20261110_01`),
    from the frozen scores:
    (a) strata that contain a primary-set paper; strata used by the primary comparison (≥ 1 scored primary-set paper and
        ≥ 1 scored control); controls, and controls with a defined score, in the used strata and in the other strata;
    (b) papers without a defined score, by group, with a check that each has n_i + n_j + n_k = 0 in the window;
    (c) shares with score > 0, ≥ the yearly top-5% threshold and ≥ the top-1% threshold, for the retracted papers in the
        used strata and for their controls: pooled (Wilson 95% interval) and weighted by the number of scored
        primary-set papers per stratum, the weighting of the SPEC mean difference (95% interval from 2,000 bootstrap
        draws over the sorted used strata; generators: the first two children of `SeedSequence(20261109)`, CD5 then
        CD3); for the record, the pooled shares of the controls in the other strata.
    Nothing is tested and no earlier estimate changes. The script first reproduces from the frozen inputs every e04
    value it relies on (counts, strata, matched control mean, Mantel–Haenszel odds ratios and counts, yearly thresholds,
    the v0.2 control shares) and the e02 counts of strata and controls, and stops if any differs. Purpose: to state the
    comparison group correctly in the paper and to put like-for-like control shares next to the retracted shares.
    Script `e11_controls/e11_controls.py`, test `e11_controls/test_e11.py` (synthetic data), pipeline
    `vm/run_posthoc4.sh`.
