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
| `e13_article_types/` | **Post hoc** P13: article-type restriction of both groups; frozen-score and original-estimate replay | `e13_articles_20261126_01` | `RESULTS_LOG.md` |
| `e14_authors/` | **Post hoc** P14: exclude primary nodes linked to author names on at least ten retracted paper keys; baseline replay | `e14_authors_20261126_01` | `RESULTS_LOG.md` |
| `e15_citers/` | **Post hoc** P15: citing-record exclusions, adjusted DI_nok mean, whole-journal bootstrap and top-ten-journal exclusion | `e15_citers_20261127_02`; population flow `e15_flow_20261127_02` (current; _01 preserved) | `RESULTS_LOG.md` |
| `e16_topic/` | **Post hoc** P16: PMID-prioritized type audit, major-MeSH matching and fixed-window journal intervals | `e16_topic_20261127_03` (successful; _01/_02 preserved) | `RESULTS_LOG.md` |
| `e17_coverage/` | **Post hoc** P17: citer reference coverage, coverage-restricted DI_nok/sign and whole-journal primary intervals | `e17_coverage_20261127_01` | `RESULTS_LOG.md` |
| `e18_types/` | **Post hoc** P18: composition of PMID-prioritized article-type filter failures (descriptive) | `e18_types_20261127_01` | `RESULTS_LOG.md` |
| `e19_models/` | **Post hoc** P19: P13's conditional-logit models refitted on the PMID-priority article sample | `e19_models_20261127_01` | `RESULTS_LOG.md` |
| `e06_figures/` | Paper figures from run records (laptop) | `e06_fig_20261127_10` (current; whole-journal DI_nok intervals, original CD/event values, four null lines); paired annual intervals from P12 | `RESULTS_LOG.md` |

Runs not cited carry a `SUPERSEDED.txt` with the reason: `e07_yearly_20261123_01`, `e08_posthoc2_20261123_01`
(notice rule by type name; see POSTHOC.md P8 amendment), `e06_fig_20261110_01`, `_02`, `e06_fig_20261123_01` (layout).

| Record | Where |
|---|---|
| Pre-specified design | `../SPEC.md` (v1; its SHA-256 is in every run.json) |
| Pre-specification commit/date, hash and clock-source provenance | `spec_provenance.json` (private Git history; VM/laptop timestamps are not directly comparable) |
| Post hoc plans (written before each run) | `../POSTHOC.md` (its SHA-256 is in every post hoc run.json) |
| Claim → number → run | `../FINDINGS.md` |
| Lab notebook | `<exp>/RESULTS_LOG.md` |
| Per-run config, script hash, counts | `<exp>/runs/<run_id>/run.json` |
| Per-run checksums | `<exp>/runs/<run_id>/SHA256SUMS` |
| Run stdout | `<exp>/runs/<run_id>/stdout.log` |
| Main exploratory questions / diagnostic appendix / supplementary material | `../paper/content/results.tex`, `../paper/content/appendix.tex`, `../paper/content/supplement.tex` |
| P12 paired points, counts and confidence intervals | `e12_diagnostics/runs/e12_diag_20261126_01/paired_event.csv` |
| P13 type coverage, restricted counts, estimates and input hashes | `e13_article_types/runs/e13_articles_20261126_01/results.json` |
| P14 aggregate author coverage, exclusions and comparisons (no names or associations) | `e14_authors/runs/e14_authors_20261126_01/results.json` |
| P15 filters, matched/regression means, classes, journal ranks, coverage and hashes | `e15_citers/runs/e15_citers_20261127_02/results.json`, `manifest.json` |
| Population-flow inputs, counts and checksums | `e15_citers/runs/e15_flow_20261127_02/` (current) |
| Failed P15 join and exact source audit | `e15_citers/runs/e15_citers_20261127_01/`, `e15_citers/versions/e15_01_source.tgz` |
| P16 type-linkage audit, topic coverage/matched baselines and fixed-window journal intervals | `e16_topic/runs/e16_topic_20261127_03/results.json`, `run.json`, `manifest.json` |
| P17 citer coverage, restricted DI_nok/sign and journal-clustered primary intervals | `e17_coverage/runs/e17_coverage_20261127_01/results.json`, `run.json`, `manifest.json` |
| P18 publication types behind article-type filter failures (aggregate counts) | `e18_types/runs/e18_types_20261127_01/results.json`, `run.json`, `manifest.json` |
| P19 PMID-priority adjusted sign/top-tier models and replayed union-link models | `e19_models/runs/e19_models_20261127_01/results.json`, `run.json`, `manifest.json` |
| P16 failed attempts and exact source audits | `e16_topic/runs/e16_topic_20261127_01/`, `_02/`; `e16_topic/versions/e16_01_source.tgz`, `e16_02_source.tgz` |
| Large intermediates (labels, frozen scores, yearly counts) | VM disk `~/e/data/work/` only (per-paper tables are never released) |
| VM billing events | `../vm/sessions.log` |
