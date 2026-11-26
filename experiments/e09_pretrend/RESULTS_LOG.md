# E09 pre-trend checks of P6 (POSTHOC.md P9): lab notebook

## e09_pretrend_20261123_01 (VM, 9 s, `run_posthoc3.sh 20261123 01`, AUTO_DEALLOCATE=0; VM stopped by `vmctl.sh stop`)
- Frozen inputs verified; reproduces the P6 point estimate and n of `e08_posthoc2_20261123_02` exactly.
- (a) Papers with R ≥ t + 4 (3,471): **real DiD +0.064 (0.037–0.093)** (2,763 with controls); **placebo at R − 3
  +0.036 (0.012–0.060)** (2,565). By class, real vs placebo: honest error +0.079 (0.012–0.149) vs +0.005 (−0.065 to
  0.077); misconduct +0.078 (0.041–0.115) vs +0.042 (0.010–0.074); other +0.033 vs +0.016 (both include 0); paper mill
  +0.052 (148 papers; wide).
- (b) Balanced event time (3,083 papers, τ = −3 … +3 observable): paired gap 0.053, 0.072, 0.089, 0.092 (τ = 0), 0.123,
  0.201, 0.151; citing papers per year (retracted vs controls) 5.4/4.0, 6.3/4.8, 6.1/4.9, 5.3/4.9, 3.6/4.8, 2.8/4.7,
  2.3/4.5.
- Reading: the divergence starts before the notice and steepens after it; about half of the change around the notice is
  matched by the placebo. Retracted papers are cited more than controls in the years before the notice, then less.
