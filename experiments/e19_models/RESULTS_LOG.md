# P19 lab notebook

- 2026-11-27 UTC, before execution: P19 plan published as `d14be2e63862fd8a2c755b9ac2b2de3e9a59afb6`
  (anonymous commit page and raw POSTHOC.md bytes verified). Two synthetic tests pass locally with statsmodels 0.14.4
  in an isolated folder (the VM uses its pinned 0.15.0): union-link vs PMID-priority flag selection, and the P13
  conditional-logit wrapper on flagged primary papers and controls. A throwaway synthetic end-to-end run exercised
  every replay guard. No real data were read before the VM run.
- `e19_models_20261127_01` (VM, started 00:31:13 UTC on 28 November by the VM clock): 4:54.61 wall time, peak
  RSS 10,975,216 KB, exit 0. Tests passed on the VM (a sparse synthetic top-5% fit emits an overflow warning in its CI;
  the test does not use that interval). Hashes matched; eligibility counts, P13's six union-link models (1e-6) and
  P16's PMID-priority MH odds ratios reproduced. Fetch checksums verified; VM deallocated.
- PMID-priority models: positive 1.25 (1.14-1.38), 1.34 (1.21-1.47), 1.35 (1.22-1.49), 2,813 retracted in 1,199
  strata; top 5% 1.07 (0.86-1.33), 1.62 (1.27-2.08), 1.39 (1.07-1.79), 1,546 in 393 strata. With both covariates the
  top-5% excess persists in both article-only samples (union link 1.39, 1.08-1.80) but not in the full sample
  (1.19, 0.96-1.47). No other specification was tried.
