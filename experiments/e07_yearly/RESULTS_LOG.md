# E07 yearly citation counts (post hoc P6/P8, POSTHOC.md round 2): lab notebook

Label-free: reads the focal lists (iid, pub_year), the graph tables and PubMed publication types / comments-corrections
links of *citing* records. Output `yearly.parquet` (VM only; per paper and citing year: n_i, n_j and the notice parts)
is checked against the frozen E3 counts and hashed before e08 joins labels.

Clock note: VM timestamps are NTP-synchronised UTC; the laptop's `vm/sessions.log` entries of 2026-11-24 are one hour
behind true UTC (laptop clock offset), consistently for start and stop.

## Unit test `test_yearly.py` (2026-11-23, laptop venv pinned to the VM versions, then VM)
- Random toy graphs (20 seeds, 1,200 focal papers) with duplicate edges, 60+ self-loops, mutual citations, citing nodes
  without a year and notice records: yearly counts equal a brute-force count, and their sums over [t, t+5] and
  [t+1, t+5] equal `e03_cd5/cd_lib.py` (the frozen-score code) exactly.
- Sensitivity of the test checked by five deliberate mutations of `yearly_lib.py` (self-loops kept in the also-cites
  join; self-citation kept in A; f itself kept as a notice citer; citers of f counted in the notice part of n_k; wrong
  nj_ntc filter): each one fails the test. A first version of the test missed the self-loop mutation (too few
  self-loops in the toy graphs); the graphs were enlarged before any VM run.
- VM run (2026-11-24 06:09Z, inside `run_posthoc2.sh 20261123 01`): OK, 8 s.

## e07_yearly_20261123_01 (VM, 170 s) — kept for the record, NOT USED (notice rule superseded)
- Focal 110,462 (union of `e02_pop_cd3_20261110_01` and `e02_pop_20261110_01`; the CD5 focal list is contained in it).
- **Checks: window sums equal the frozen counts exactly**: `e03_cd5_cd3_20261110_01` 110,462 papers, windows [0,3] and
  [1,3], 0 mismatches; `e03_cd5_20261110_01` 86,950 papers, windows [0,5] and [1,5], 0 mismatches.
- Rows: fr 4,409,105; a 4,603,700; ab 2,953,897; yearly rows 948,941.
- **Incident:** the PubMed 2026 baseline names D016440 "Retraction Notice" (29,990 records); the rule written in
  POSTHOC.md used the older name "Retraction of Publication", which does not occur. Retraction notices were therefore
  caught only through RetractionOf links (29,272 records flagged by link only). Rule changed to publication-type UIs
  (POSTHOC.md P8 amendment, written before any P8 result was read); rerun as `e07_yearly_20261123_02`.
- Types seen (UI, name, records): D000075742 Expression of Concern 3,248; D016425 Published Erratum 194,062;
  D016440 Retraction Notice 29,990; D016441 Retracted Publication 30,697 (the retracted articles themselves; not a
  notice type).

## e07_yearly_20261123_02 (VM, 177 s, `run_posthoc2.sh 20261123 02`) — the run used by e08/e09
- Notice rule by publication-type UI (D016440 Retraction Notice, D016425 Published Erratum, D000075742 Expression of
  Concern) or link (RetractionOf, ErratumFor, ExpressionOfConcernFor): 227,191 PubMed records (4,683 by type only,
  222,508 by type and link; none by link only); **106,386 notice nodes** in the graph (2,893 of them are focal papers).
- **Checks: window sums equal the frozen counts exactly**: `e03_cd5_cd3_20261110_01` (110,462 papers, windows [0,3],
  [1,3]) and `e03_cd5_20261110_01` (86,950 papers, windows [0,5], [1,5]): 0 mismatches each.
- Rows: fr 4,409,105; a 4,603,700; ab 2,953,897; notice edges 1,227,460; notice n_k pairs 3,270,437; yearly rows 949,578.
- Citing papers 2000–2023 (all focal papers): n_i 1,649,803, n_j 2,953,897; from notices: 6,697 (n_i), 7,447 (n_j);
  10,520 focal papers have at least one notice citation (label-free summary).
- **Frozen:** `yearly.parquet` sha256 `257bd0f858992d12dd05662b1af47947319c6ceca6bd0c400a60d1557f5e25cb` (949,578 rows), VM only.
