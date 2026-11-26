# Project E experiments: index and where every record lives

| Folder | Step | Runs cited in the paper | Notebook |
|---|---|---|---|
| `e01_lit/` | Literature gate: DOI verification | `e01_doi_20261109_01` | `RESULTS_LOG.md` |
| `e02_population/` | Retracted papers, journal × year controls, reference sample (no scores); CD3 population (post hoc P2) | `e02_pop_20261110_01`, `e02_pop_cd3_20261110_01` | `RESULTS_LOG.md` |
| `e03_cd5/` | CD library, unit test against brute force, **frozen** label-free scores | `e03_cd5_20261110_01`, `e03_cd5_cd3_20261110_01` | `RESULTS_LOG.md` |
| `e04_eval/` | Pre-specified evaluation (SPEC.md §6); checks the frozen hash, then joins labels | `e04_eval_20261110_01`, `e04_eval_cd3_20261110_01` | `RESULTS_LOG.md` |
| `e05_posthoc/` | **Post hoc** P1: reference and citation counts | `e05_refs_20261110_01` | `RESULTS_LOG.md` |
| `e07_yearly/` | **Post hoc** P6/P8 input: label-free yearly citing counts (+ notice records), checked against the frozen counts, **frozen** | `e07_yearly_20261123_02` | `RESULTS_LOG.md` |
| `e08_posthoc2/` | **Post hoc** P3–P8: equivalence, reviews, DI_nok, before/after, sign shift, notices (replays E4 exactly first) | `e08_posthoc2_20261123_02` | `RESULTS_LOG.md` |
| `e09_pretrend/` | **Post hoc** P9: placebo notice and balanced event time | `e09_pretrend_20261123_01` | `RESULTS_LOG.md` |
| `e10_describe/` | **Post hoc** P10: size of n_k (descriptive) | `e10_nk_20261123_01` | `RESULTS_LOG.md` |
| `e11_controls/` | **Post hoc** P11: controls behind the primary comparisons (counts, matched shares; descriptive; replays E4 first) | `e11_controls_20261126_01` | `RESULTS_LOG.md` |
| `e12_diagnostics/` | **Post hoc** P12: paired annual confidence intervals and matched mean-log count differences; reproduces P9/P11/P1 | `e12_diag_20261126_01` | `RESULTS_LOG.md` |
| `e06_figures/` | Paper figures from run records (laptop) | `e06_fig_20261126_04` (current; paired annual gaps and intervals); earlier marginal figure: `e06_fig_20261126_01` | `RESULTS_LOG.md` |

Runs not cited carry a `SUPERSEDED.txt` with the reason: `e07_yearly_20261123_01`, `e08_posthoc2_20261123_01`
(notice rule by type name; see POSTHOC.md P8 amendment), `e06_fig_20261110_01`, `_02`, `e06_fig_20261123_01` (layout).

| Record | Where |
|---|---|
| Pre-specified design | `../SPEC.md` (v1; its SHA-256 is in every run.json) |
| Pre-specification commit/date and hash provenance | `spec_provenance.json` (private Git history, not a registry timestamp) |
| Post hoc plans (written before each run) | `../POSTHOC.md` (its SHA-256 is in every post hoc run.json) |
| Claim → number → run | `../FINDINGS.md` |
| Lab notebook | `<exp>/RESULTS_LOG.md` |
| Per-run config, script hash, counts | `<exp>/runs/<run_id>/run.json` |
| Per-run checksums | `<exp>/runs/<run_id>/SHA256SUMS` |
| Run stdout | `<exp>/runs/<run_id>/stdout.log` |
| Main exploratory questions / diagnostic appendix | `../paper/content/results.tex`, `../paper/content/appendix.tex` |
| P12 paired points, counts and confidence intervals | `e12_diagnostics/runs/e12_diag_20261126_01/paired_event.csv` |
| Large intermediates (labels, frozen scores, yearly counts) | VM disk `~/e/data/work/` only (per-paper tables are never released) |
| VM billing events | `../vm/sessions.log` |
