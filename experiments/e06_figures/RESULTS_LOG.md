# E06 figures: lab notebook
- e06_fig_20261110_01: superseded (log-axis minor labels overlapped; legend clipped).
- e06_fig_20261110_02: superseded (panel-1 title lacked the ×10⁻³ scale).
- e06_fig_20261110_03: a rerun that failed to change the title (string mismatch); deleted before use, never cited.
- **e06_fig_20261110_04**: the paper figure (`paper/figures/fig1_forest.pdf`). Palette #2a78d6 / #eb6834, checked with the dataviz validator (light mode: all checks pass); window also encoded by marker shape.
- e06_fig_20261123_01: superseded (positive-control row label clipped at the left edge; Fig. 2 axis label reworded).
- **e06_fig_20261123_02** (laptop, Matplotlib 3.10.8, script `e06_figs_v2.py`): the v0.2 figures. `fig1_forest.pdf`
  (CD5/CD3 by reason class, DI_nok panel from e08 P5, review positive control from e08 P4) and `fig2_event.pdf`
  (balanced event time from e09). Rebuilt from the run records in a scratch folder: all four files byte-identical.
# 2026-11-26 submission-readiness revision
- Planned run `e06_fig_20261126_01`: same E4/E8/E9 input records and plotted values as `e06_fig_20261123_02`;
  embed TrueType fonts (PDF font type 42) so the existing en dashes in year ranges survive PDF text extraction.
  Figure 2 continues to plot separate defined-score means, not the mean of paired differences; the manuscript and
  caption now state the distinction and the different populations explicitly. No statistical estimate is changed.
- Completed in 1.7 seconds with Matplotlib 3.10.8; both PDF year ranges extract as en dashes. The new run's figures,
  configuration, stdout and checksums are preserved; earlier figure runs are unchanged.

# v0.5 paired annual figure (2026-11-26)
- `e06_fig_20261126_02` first plotted P12 paired points and 95% bootstrap intervals; its axis label was clipped
  and the citation legend overlapped a curve. `e06_fig_20261126_03` moved the legend and split the label, but needed
  a wider left margin. Both runs and their checksums are retained.
- **e06_fig_20261126_04** is current: P12 input `e12_diag_20261126_01/paired_event.csv`, whose points/counts first
  reproduce P9. Figure 1 is byte-identical to `e06_fig_20261126_01`. Figure 2 plots the paired annual gap with CIs,
  rather than different-subset marginal means; its citation panel is unchanged.
- PNG inspected and every rendered PDF word verified inside the page bounds. A first canvas check included an
  off-axis, undisplayed Matplotlib tick; the rendered-PDF check avoids that false positive.
