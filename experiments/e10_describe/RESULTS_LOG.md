# E10 descriptive (POSTHOC.md P10): lab notebook

## e10_nk_20261123_01 (VM, 0.4 s; on `e02_pop_20261110_01` / `e03_cd5_20261110_01`, frozen hash verified)
- All 86,904 papers with a defined CD5: n_k quantiles (5, 25, 50, 75, 95%) 106, 930, **2,862**, 7,703, 32,701; citing
  papers n_i + n_j 1, 5, **12**, 25, 74; share n_k / (n_i + n_j + n_k) 0.948, 0.988, **0.996**, 0.999, 1.000.
  n_k is ≥ 90% of the denominator for 97.9% of papers and ≥ 99% for 71.3%.
- By group (median n_k / citing papers / share): retracted primary 4,481 / 19 / 0.995; retracted inside the window
  3,264 / 8 / 0.997; controls 3,158 / 13 / 0.996; reference sample 1,997 / 10 / 0.995.
- Reading: CD5 ≈ (n_i − n_j) / n_k for almost all papers, so differences among the citing papers move CD5 by
  thousandths at most.
