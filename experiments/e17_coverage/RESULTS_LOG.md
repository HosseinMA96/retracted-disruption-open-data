# P17 lab notebook

- 2026-11-27 UTC, before execution: P17 plan published as `4169ea7cbd6a600f420c6871c566bdaa37b5b214`
  (anonymous commit page and raw POSTHOC.md bytes verified). Four synthetic tests pass locally with DuckDB 1.5.6:
  restricted counts match brute force and the frozen `cd_lib` counter on three random graphs; whole-journal
  Mantel--Haenszel resampling keeps strata together; generic matched means use retracted-count weights.
  A throwaway end-to-end smoke run on a synthetic project tree exercised every replay guard and output.
  No real data were read before the VM run.
- `e17_coverage_20261127_01` (VM, started 23:03:03 UTC by the VM clock): 2:53.84 wall time, peak RSS
  3,324,496 KB, exit 0. Tests passed on the VM; frozen and graph hashes matched P15; independent counts reproduced
  frozen n_i/n_j for all 56,734 papers (1,390,863 citing events; 1,228,713 distinct citers); P15 unfiltered DI_nok
  and E4 mean gap/odds ratios replayed exactly. Fetch checksums verified; VM deallocated immediately.
- Results: citers of retracted papers have slightly more graph references (average share below 10: 2.3% vs
  2.9%; below 25: 11.7% vs 14.3%; mean log gap +0.048, 0.023-0.069). Restricted DI_nok gaps: 0.069
  (0.037-0.097) at >=10 and 0.071 (0.036-0.102) at >=25. Restricted positive-score ORs: 1.25 and 1.29.
  Journal-resampled primary intervals: positive OR 1.06-1.40, mean gap -0.00070 to 0.00112, top-5% 0.78-1.23,
  top-1% 0.35-1.12. By the pre-stated rule, the coverage-restricted contrast persists. No rule was changed.
