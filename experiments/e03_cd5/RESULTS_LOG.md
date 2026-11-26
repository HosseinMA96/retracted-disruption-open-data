# E03 CD5 scores: lab notebook

## Unit test `test_cd.py` (2026-11-10, VM vm-project-e)
- First run FAILED (seed 1, focal 37: n_k 32 vs brute force 31). Cause: `inc` kept self-loop edges, so a reference that cites itself counted as a citer of that reference. Fix: `e.citing_iid <> e.cited_iid` in `cd_lib.build_inputs`. Logged here; no run folder (test only).
- Second run: 1,200 focal papers over 20 random graphs equal brute force for both windows → OK.

## e03_cd5_20261110_01 (VM, 146 s, 16 batches)
- Focal 86,950 (from e02_pop_20261110_01; reads iids and years only). Focal–reference pairs 3,407,153; target nodes 2,417,970; incoming citations kept 331,830,072.
- CD5 defined (window [t, t+5]): 86,904; ([t+1, t+5]): 86,885. CD5 = 1 share of defined: 0.00038 (zero-reference papers were excluded by design).
- CD5 quantiles (1, 5, 25, 50, 75, 95, 99%): −0.0578, −0.0218, −0.0044, −0.0010, 0.0, 0.0059, 0.0556.
- **Frozen:** scores.parquet sha256 `fa9fdb9ad3105c06d3bc490c0ddd518f927e5466e85445f09163aa566459c015` (86,950 rows), VM only.
