# E11 controls (POSTHOC.md P11, descriptive): lab notebook

## e11_controls_20261126_01 (VM, 4.4 s; `vm/run_posthoc4.sh 20261126 01`, log `vm/logs/run_posthoc4_20261126_01.log`)
- Why: the v0.2 text paired the 4,587 primary-set papers with all 52,147 controls, which were drawn for all 10,450
  retracted papers, and quoted control shares (18.7%, 4.05%, 0.73%) taken over all scored controls (found in the
  2026-11-26 readiness check). Plan P11 written first (POSTHOC.md SHA-256 `a87b287f…`, recorded in run.json).
- Before the run: `test_e11.py` passed on the laptop (throwaway venv, pandas 3.1.1) and on the VM (step `test_e11` of the
  same pipeline): synthetic populations through the real `e04_eval.py`; every count and share equal to a plain-loop
  computation; two runs byte-identical; the script stops when an e04 estimate, an e04 threshold, an e02 count or the
  frozen-score hash is altered (7 mutations).
- Inputs: CD5 `e02_pop_20261110_01` / `e03_cd5_20261110_01` / `e04_eval_20261110_01`; CD3 `e02_pop_cd3_20261110_01` /
  `e03_cd5_cd3_20261110_01` / `e04_eval_cd3_20261110_01`. Frozen hashes verified; every e04 value used was reproduced
  exactly (counts, strata, matched control mean, Mantel–Haenszel odds ratios and counts for > 0 / top 5% / top 1%, yearly
  thresholds, v1 control shares), as were e02's counts of strata and controls.
- **CD5.** Population: 10,450 retracted papers in 5,458 strata; 52,147 controls (52,122 scored). Primary set: 4,587
  papers (all scored) in 2,240 strata; 2,239 strata used (4,586 papers); the other one has no control.
  **Controls in the used strata: 31,674, of which 31,662 scored**; the other 3,219 strata (papers retracted inside the
  window only) hold 20,473 (20,460 scored). The v1 Mantel–Haenszel `control_n` (52,122) is the count of all scored
  controls; strata without a primary-set paper add nothing to the odds ratios.
- Undefined CD5: 46 papers (86,950 scored papers, 87,088 label rows): 25 controls (12 in the used strata), 2 papers
  retracted inside the window, 19 reference-sample papers; every one has n_i + n_j + n_k = 0 in the window.
- Shares, CD5 (retracted primary set, v1 Wilson | **controls weighted by the scored primary-set papers per stratum,
  95% bootstrap over strata** | controls pooled, used strata | controls pooled, other strata | v1: all scored controls):
  - score > 0: 20.1% (924/4,587) | **17.3% (16.0–18.6)** | 18.1% | 19.7% | 18.7%
  - top 5%: 3.1% (2.6–3.6; 142) | **3.1% (2.8–3.5)** | 3.3% | 5.2% | 4.05%
  - top 1%: 0.37% (0.23–0.59; 17) | **0.54% (0.43–0.66)** | 0.56% | 0.99% | 0.73%
  Over the 4,586 papers in the used strata the retracted shares are 20.1% (923), 3.1% (142), 0.37% (17).
- **CD3.** Population: 13,661 retracted papers in 6,565 strata; 68,190 controls (68,146 scored). Primary set: 7,350
  (7,349 scored) in 3,310 strata; 3,308 used (7,348 papers). **Controls in the used strata: 48,069, of which 48,044
  scored**; other 3,257 strata: 20,121 (20,102 scored). Undefined CD3: 79 papers (44 controls, 1 primary, 2 secondary,
  32 reference sample), all with a zero denominator.
  - score > 0: 22.3% (1,642/7,349) | 18.4% (17.4–19.6); top 5%: 3.8% (277) | 3.4% (3.1–3.8); top 1%: 0.50% (37) |
    0.56% (0.46–0.66).
- Reading: the v0.2 shares mixed in the controls of strata that hold only papers retracted inside their window, where
  scores above the thresholds are more frequent (CD5 top 5%: 5.2%). Like for like, retracted papers and their controls
  reach the top 5% equally often (3.1% and 3.1%), as the odds ratio of 0.99 says. No estimate of v1 or P3–P10 changes.
