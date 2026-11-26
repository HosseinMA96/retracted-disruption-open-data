# E08 post hoc round 2 (POSTHOC.md P3–P8): lab notebook

Group-level outputs only (`results.json`, `event_time.csv`). The script verifies the frozen E3/E7 hashes, then replays
E4 in E4's order with E4's seeds and stops unless every v1 estimate is reproduced.

## Smoke test (2026-11-23, laptop venv pinned to the VM versions, synthetic data in /tmp, deleted)
- Synthetic populations, scores and yearly counts with a planted post-retraction effect: the replay of a real e04 run on
  the same synthetic data was reproduced exactly (11 comparisons per population); P6 recovered the planted effect;
  reruns byte-identical.

## e08_posthoc2_20261123_01 (VM, 211 s) — kept for the record, NOT USED
- Used the notice flags of `e07_yearly_20261123_01` (superseded). Its P6/P8 output was not read. P3–P5 and P7 do not use
  notice flags and are identical in run _02 (same seeds, same order).

## e08_posthoc2_20261123_02 (VM, 211 s, `run_posthoc2.sh 20261123 02`) — the run cited in the paper
- Frozen inputs verified; **replay reproduces `e04_eval_20261110_01` and `e04_eval_cd3_20261110_01` exactly** (11
  comparisons each).
- **P3 equivalence.** Margin for the mean difference = 0.1 × SD of CD5 in the reference sample = ±0.00442 (SD 0.0442).
  CD5 primary: 90% interval −0.00051 to 0.00093 → equivalent; smallest supported margin 0.00093. Top 5%: OR 0.99, 90%
  0.85–1.16 → equivalent within 0.80–1.25 (TOST p = 0.011). Top 1%: 0.67, 90% 0.44–1.03 → not shown. CD5 > 0: 1.23,
  90% 1.15–1.32 → not equivalent (a real shift, see P7). CD3 primary: difference equivalent (90% −0.00017 to 0.00101);
  top 5% 1.12, 90% 1.00–1.25 → narrowly not equivalent (p = 0.054). By class: mean differences equivalent for
  misconduct, paper mill and other (CD5 and CD3); honest error (CD5) not; class odds ratios too imprecise.
- **P4 reviews (positive control).** 6,032 reviews vs 46,090 other controls: CD5 difference −0.00329 (−0.0066 to
  −0.0011), i.e. −0.074 SD; top 5% OR 0.58 (0.47–0.72); top 1% 0.39 (0.21–0.73); CD5 > 0 0.95 (0.86–1.04). Expected
  direction. Note: the review gap in mean CD5 is smaller than the ±0.0044 margin; the retracted papers' interval rules out
  differences above 0.00093 (about a quarter of the review gap).
- **P5 DI_nok.** CD5 window: retracted −0.309 vs controls −0.376, **difference +0.067 (0.046 to 0.087)** (4,518
  defined; margin ±0.056 → not equivalent). By class: misconduct +0.083 (0.058–0.109), other +0.049 (0.019–0.078),
  paper mill +0.054 (−0.003 to 0.120), honest error +0.004 (−0.056 to 0.060). CD3 window: +0.075 (0.056–0.093).
  **Thresholds degenerate:** the 95th and 99th percentiles of DI_nok are 1.0 in every year (more than 5% of papers score
  exactly 1), so "top 5%" = DI_nok = 1; retracted 2.5% vs controls 4.9% (OR 0.59, 0.48–0.72) — extremes arise at low
  citation counts and retracted papers are cited more (P1, P7a). Not used as a top-tier result.
- **P7 sign shift.** Uncited in window: 1.5% vs 4.0% (OR 0.43, 0.33–0.56). Cited papers only: OR(CD5 > 0) 1.20
  (1.11–1.31). Conditional logit (strata journal × year): CD5 > 0 unadjusted 1.23 (1.14–1.34), + log refs 1.32
  (1.21–1.44), + log citations 1.32 (1.21–1.43); **top 5% unadjusted 0.99 (0.83–1.20), + log refs 1.42 (1.16–1.75)**,
  + log citations 1.19 (0.96–1.47) (2,168 retracted papers in 538 informative strata). Reference-count coefficient
  −1.64 (top 5%), −0.63 (CD5 > 0). Robustness (c) is therefore confounding by reference length (retracted papers less
  often have short lists; pooled lower quartile 29 vs 22 references, `e05_refs_20261110_01`), not only a change of strata.
- **P8 notice citations (CD5 window).** Share with ≥ 1 notice citation: retracted after the window 18.4% (844/4,587),
  retracted inside the window 36.7% (2,151/5,863), controls 4.7%, reference sample 3.0%. Without notices: primary
  unchanged (difference 0.00029, OR CD5 > 0 1.24, top 5% 1.02); all retracted (robustness e) OR(CD5 > 0) 1.50 → 1.35
  (1.28–1.43); retracted inside the window only 1.71 (1.60–1.82) → 1.44 (1.34–1.54).
- **P6 before/after (CD3 population).** 7,899 retracted papers with t+1 ≤ R ≤ 2021; 5,100 with a defined change and
  controls. **DiD in DI_nok +0.074 (0.050 to 0.097)** (retracted +0.174, controls +0.100); with notices +0.074. By class:
  honest error +0.124 (0.075–0.173), misconduct +0.090 (0.061–0.121), other +0.020 (−0.028 to 0.067), paper mill +0.039
  (−0.052 to 0.132). Citing papers per year, before → after: retracted 3.94 → 2.61, controls 3.10 → 4.69 (expected drop).
  Event-time table (`event_time.csv`): the paired gap already rises before the notice (0.06 at τ = −5, 0.12 at τ = −1)
  → pre-trend check P9 (POSTHOC round 3).
