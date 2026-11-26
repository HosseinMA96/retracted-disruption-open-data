# E05 post hoc (POSTHOC.md): lab notebook

## e05_refs_20261110_01 (P1, VM, 16 s; on e02_pop_20261110_01 / e03_cd5_20261110_01)
- Reference count, median [IQR]: retracted (primary) 40 [29, 53]; retracted inside window 33 [22, 47]; controls 35 [22, 51]; context 30 [16, 46].
- Citations in window [t, t+5], median [IQR]: retracted primary 19 [9, 36]; inside window 8 [3, 20]; controls 13 [5, 26]; context 10 [4, 22].
- Within journal × year (weighted by retracted papers): log1p reference count −0.017 (same length); log1p window citations +0.099 (≈10% more cited).
- Context sample Spearman: CD5 vs reference count −0.192; CD5 vs window citations −0.433.
- Reading: the raw reference-length gap comes from journals (retracted papers sit in journals with longer lists); inside strata lengths match. Robustness (c) splits strata further by pooled deciles and changes which strata contribute (2,315 vs 2,239).

## P2: CD3, papers 2000–2019 (VM; run_posthoc.sh 20261110 01)
- e02_pop_cd3_20261110_01 (152 s): eligible 14,354,335; retracted all 13,661, primary (after pub_year + 3) 7,350; by class (all/primary): honest error 1,990/615, misconduct 6,508/4,172, other 3,926/1,855, **paper mill 1,237/708**; strata 6,565 (5 without controls); controls 68,190; context 28,784; focal 110,462.
- e03_cd5_cd3_20261110_01 (158 s): window [t, t+3] (columns keep the names cd_w0 / cd_w1). Frozen hash in its run.json.
- e04_eval_cd3_20261110_01 (25 s): numbers in `../../FINDINGS.md` (post hoc section).
