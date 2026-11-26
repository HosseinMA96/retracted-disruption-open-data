# P12 diagnostic notebook

Planned before the first run in POSTHOC.md: reproduce P9 annual paired points and P11/P1 populations/statistics;
bootstrap annual paired gaps and matched means of log counts; inspect the available author-identifier columns.
No per-paper outputs are released and no original run is overwritten.

## e12_diag_20261126_01 (2026-11-26)
VM run: 2026-11-26T18:34:19Z, 0.9 s recorded analysis time (1.29 s wall time), peak RSS 512,404 KB.
Synthetic tests passed locally and on the VM. Frozen CD5/CD3 score and yearly-count hashes passed.
All seven P9 paired points/counts, P11's 4,586 retracted / 31,662 control population and both original P1
log-of-group-mean differences reproduced (absolute tolerance 1e-12).

Matched mean-of-log differences, 95% journal-year strata-bootstrap intervals (2,000 draws, seed 20261109):
- References: 3.641801947 retracted vs 3.557478452 weighted controls; difference +0.084323495
  (0.058004811, 0.109042910).
- Window citing papers: 2.956958933 vs 2.646093595; difference +0.310865338 (0.279558768, 0.341075849).
- Original P1 log-of-mean points remain -0.017011734 and +0.098965652; they are different statistics.

Annual paired points, pair counts and 95% intervals are in `paired_event.csv`. At tau -3, 0 and +2:
0.052810085 (0.020407792, 0.082910556), n=2,220;
0.092282431 (0.059448072, 0.124484299), n=2,440;
0.201497208 (0.161588681, 0.241737852), n=1,982.
The diagnostic label inputs contain no author-identifier columns; no author-cluster sensitivity was performed.
Aggregate records were fetched with verified SHA256SUMS and the VM was deallocated immediately afterward.
