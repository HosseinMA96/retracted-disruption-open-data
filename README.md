<h1 align="center">Do retracted papers look disruptive?</h1>

<p align="center">
  <em>The CD index before retraction on the open biomedical citation graph</em>
</p>

<p align="center">
  <img alt="Pre-specified" src="https://img.shields.io/badge/design-pre--specified-2a78d6">
  <img alt="Open data only" src="https://img.shields.io/badge/data-open%20only-1baf7a">
  <img alt="Python 3.11" src="https://img.shields.io/badge/python-3.11-eda100">
  <img alt="Code: MIT" src="https://img.shields.io/badge/code-MIT-6250d6">
  <img alt="Records: CC BY 4.0" src="https://img.shields.io/badge/records-CC%20BY%204.0-eb6834">
</p>

Companion repository to the paper by **Hossein Mohasel Arjomandi** (manuscript prepared for submission). It holds
the code, the design specification and the post hoc plans with their hashes, every run record with checksums, a map
from each number in the paper to the run that produced it, and the LaTeX source.

## In one paragraph

The CD index of disruption is widely used, and its use in research evaluation is being discussed. This project asks how
it scores papers that are **later retracted**. Scores are computed on the **January 2024** OpenCitations graph (linked
to PubMed) for biomedical papers published 2000–2017 that were retracted only **after** their five-year scoring window
closed, and for never-retracted controls from the **same journal and year**. The design was specified before any score
was computed; the scores were **frozen with a hash** before retraction labels were joined. Analyses added later are
labelled post hoc, and each plan was written down before it was run.

## Results at a glance

| | |
|---|---|
| Retracted papers scored before their retraction | **4,587** |
| Primary comparison: retracted papers / scored controls / journal-year strata | **4,586** / **31,662** / **2,239** |
| Mean difference in CD5 (retracted − controls) | **0.0002** (95% CI −0.0006 to 0.0011) |
| Interpretable mean-difference bound (post hoc 90% interval) | Absolute differences above **0.00093** excluded, about 28% of the review effect |
| Odds ratio for a positive CD5 (pre-specified RQ1) | **1.23** (1.13–1.34); resampling whole journals 1.06–1.40 (P17) |
| Odds ratio for reaching the top 5% of the year | **0.99** (0.83–1.20) |
| Positive control: reviews vs other papers, top 5% | 0.58 (0.47–0.72): the design detects a real contrast |
| Unfiltered DI_nok (exploratory) | **+0.067** (95% whole-journal CI 0.034-0.095); reference-co-citation shares **65.5% vs 68.8%** |
| DI_nok after excluding notice, comment/letter and retracted citers (P15) | **+0.082** (95% journal CI 0.049–0.110); 4,504 compared retracted / 30,389 controls |
| Filtered DI_nok with reference and citation adjustment | **+0.097** (0.065–0.127) |
| Filtered DI_nok excluding ten highest-retraction journals | **+0.053** (0.033–0.074); with both covariates +0.070 (0.049–0.091) |
| Top 5%, reference-adjusted and then also citation-adjusted (post hoc) | 1.42 (1.16–1.75), then 1.19 (0.96–1.47): model-dependent |
| Matched difference in mean log(1 + references), P12 | **+0.084** (0.058–0.109), 4,586 retracted papers / 31,662 controls |
| PMID-prioritized article types (P16), CD5 top 5% | 1.07 (0.86-1.32), 3,619 compared retracted papers / 24,192 controls |
| Original union-link type filter (P13), reference-adjusted CD5 top 5% | 1.64 (1.28-2.10); matched mean-log reference gap +0.064 (0.045-0.083) |
| PMID-prioritized article types (P16), CD3 top 5% | 1.21 (1.04-1.42), 5,736 compared retracted papers / 37,776 controls |
| Author-name exclusion (P14), five-year DI_nok, whole-journal interval | +0.061 (0.033-0.089), 2,260 compared papers; 2,280 primary papers removed |
| Descriptor-major MeSH matching (P16), only 540 retained papers | +0.050 (-0.012 to 0.097); exact-retained-paper baseline +0.082 (-0.006 to 0.136): inconclusive |
| Descriptor-major MeSH matching with PMID-prioritized article types, 417 papers | +0.063 (-0.003 to 0.124); exact-retained baseline +0.086 (-0.005 to 0.148): inconclusive |
| Author-name exclusion (P14), three-year top 5% | 1.03 (0.85-1.25), 3,626 compared papers |
| Citer coverage (P17): average share of citers with < 10 references in the graph | 2.3% (retracted) vs 2.9% (controls): citers of retracted papers are slightly better covered |
| DI_nok counting only citers with ≥ 10 / ≥ 25 references in the graph (P17) | **+0.069** (0.037–0.097) / **+0.071** (0.036–0.102) |
| Median sizes over all 86,904 papers with a defined CD5 | 2,862 papers citing only the references vs 12 citing the paper (19 / 13 for late-retracted papers / controls) |
| Change in DI_nok after vs before the notice, minus controls (post hoc) | +0.074 (0.050–0.097); placebo 3 years earlier +0.036 |

**Take-away:** the pre-specified five-year analysis shows a small positive-score shift but no clear unadjusted top-tier
excess; the post hoc three-year window leans toward a modest excess, but this weakens under author-name exclusions.
The unfiltered citation-composition gap applies a known denominator problem to late-retracted papers.
As a robustness check, the contrast persists after removing notices, comments/letters and retracted citers,
adjusting reference and citation counts, and excluding the ten highest-retraction journals.
PMID priority corrects some DOI-only type propagation; 21.0% of primary papers and 17.2% of drawn controls
still fail the broad article filter. Topic matching has limited coverage and does not confirm the gap.
The frozen extract records descriptor-major tags, not qualifier-only major tags; this is not complete major-heading coverage.
Original union-link article models retain the reference imbalance; type flags do not guarantee original research.
The n_k term compresses the citation-composition gap, and scores including post-retraction years are shifted. Every
number above is traced in [`FINDINGS.md`](FINDINGS.md). Mean-log reference gaps describe the direction of imbalance,
not the magnitude of the adjusted odds-ratio shifts. P14 uses name strings, not disambiguated author identities.
The review positive control detects the mean and top-tier CD5 contrasts, but not a clear sign or DI_nok contrast.

The full pool of 52,147 controls was drawn for all 10,450 retracted papers, including those retracted inside their
window. Of these controls, 25 have an undefined CD5 because its denominator is zero, leaving 52,122 scored controls.
The primary comparison uses only the 31,662 scored controls in strata containing scored primary-set papers.

<p align="center">
  <img src="paper/figures/fig1_forest.png" alt="Retracted vs matched controls by reason, with the review positive control" width="90%">
</p>
<p align="center">
  <img src="paper/figures/fig2_event.png" alt="Citing papers around the retraction notice" width="80%">
</p>

## What is in here

```text
.
├── README.md            ← you are here
├── SPEC.md              pre-specified design (v1; its SHA-256 is in every run.json)
├── POSTHOC.md           post hoc plans P1–P17, each written before it was run
├── FINDINGS.md          every number in the paper → the run that produced it
├── REPRODUCE.md         inputs, environment, exact commands in order, determinism notes
├── CITATION.cff         how to cite this repository
├── experiments/
│   ├── README.md        index of steps and the runs cited in the paper
│   ├── e01 … e17/       one folder per step: script(s), lab notebook RESULTS_LOG.md, runs/<run_id>/
│   └── …/runs/<id>/     run.json (parameters, script hash, counts) · stdout.log · group-level outputs · SHA256SUMS
├── paper/               LaTeX source (content/, journals/joi/main.tex), figures, refs.bib + DOI checks
├── lit/                 literature gate, verified DOIs and the claim check
└── vm/                  scripts and environment for the large-machine steps
```

## Quick start

```bash
# 1. verify every run record against its checksums
ok=1; for d in experiments/*/runs/*/; do (cd "$d" && sha256sum -c --quiet SHA256SUMS) || ok=0; done; [ $ok = 1 ] && echo "all runs OK"

# 2. unit tests (need duckdb, pandas): CD counts and yearly counts against brute force
cd experiments/e03_cd5 && python test_cd.py && cd ../e07_yearly && python test_yearly.py && cd ../..
python experiments/e13_article_types/test_sensitivity.py
python experiments/e14_authors/test_authors.py
python experiments/e15_citers/test_citers.py
python experiments/e16_topic/test_topic.py
python experiments/e17_coverage/test_coverage.py

# 3. rebuild the figures from the run records (byte-identical to the committed ones with Matplotlib 3.10.8)
cd experiments/e06_figures && python e06_figs_v2.py my_rebuild e04_eval_20261110_01 e04_eval_cd3_20261110_01 \
   e08_posthoc2_20261123_02 e09_pretrend_20261123_01 e12_diag_20261126_01 e16_topic_20261127_03 && \
   cmp runs/my_rebuild/fig1_forest.pdf ../../paper/figures/fig1_forest.pdf && \
   cmp runs/my_rebuild/fig2_event.pdf ../../paper/figures/fig2_event.pdf && cd ../..
python experiments/e15_citers/flow_diagram.py my_flow e15_citers_20261127_02
cmp experiments/e15_citers/runs/my_flow/fig3_population_flow.pdf paper/figures/fig3_population_flow.pdf

# 4. build the paper (Tectonic or any LaTeX)
cd paper/journals/joi && tectonic -X compile main.tex
```

**Full pipeline:** graph steps used a 64 GB RAM machine; recorded step timings, including the failed P15 attempt,
are in [`REPRODUCE.md`](REPRODUCE.md).

**JOI upload:** use the identified `paper/journals/joi/joi_latex_source.zip`, not a manuscript PDF or the legacy
anonymized package. The official declarations tool must be completed; the required separate editable
highlights file contains five bullets, each at most 84 characters. The author confirmed the 200-word abstract
and mandatory-highlights requirements; direct access to the current publisher guide remains blocked.
See [`paper/journals/joi/UPLOAD.md`](paper/journals/joi/UPLOAD.md); nothing has been submitted.
The v0.17 revision leads with unfiltered DI_nok and credits earlier denominator work. It adds the P17 citer-coverage
check and journal-resampled primary intervals, frames the positive-score excess as citer composition (CD and DI_nok
share the sign of n_i − n_j), and moves P13/P16 detail unchanged into a two-page supplementary PDF.
It retains the original pre-specified CD results, adds the identifier-aware type audit and inconclusive topic check,
and standardizes fixed-window DI_nok intervals to whole journals.
The validated identified/flat/arXiv builds have 35 pages, a 197-word abstract and approximately 9,393 words
before References, excluding review-margin line numbers. Only the explanatory flow diagram's caption carries an
AI note; data plots are covered in Methods. Earlier statistical results and all figure PDFs are unchanged.
The version prepared for submission is tagged as release `v1.0.0`; Zenodo archiving has not been set up.
The MeSH parser audit is documented in the topic notebook; no broader extraction or empirical rerun was performed.
Local builds use Tectonic. Editorial Manager's pdfLaTeX PDF must still be reviewed,
and Elsevier's declarations tool must always be completed at upload.
The abstract defines late retraction and the five-year index, and explains the denominator mechanism.
The highlights recommend pre-notice windows with notice records removed, rather than headlining a
model-dependent reference-adjusted result. P15 increases, rather than removes, the DI_nok gap; incomplete
annotation and retrospective retraction flags remain limitations. No journal or arXiv submission has been made.
The separate [cover letter](paper/journals/joi/cover_letter.pdf) and its
[editable source](paper/journals/joi/cover_letter.tex) identify the companion preprint and shared linked dataset.
CD mean-gap intervals in the forest use journal-year resampling; fixed-window DI_nok means use whole-journal
resampling throughout. Event-time intervals retain journal-year resampling. All four forest panels mark the null.
Clock sources and cross-host timestamp discrepancies are
documented in `experiments/spec_provenance.json`; immutable dates are not adjusted.

## Data sources

| Source | Used for | Access | Terms |
|---|---|---|---|
| Parsed OpenCitations snapshot, Jan 2024 | citation graph | Illinois Data Bank, [doi:10.13012/B2IDB-5216575_V1](https://doi.org/10.13012/B2IDB-5216575_V1) | CC BY 4.0 |
| OpenCitations Meta | DOIs, PMIDs, journals, years | figshare, [doi:10.6084/m9.figshare.21747461.v7](https://doi.org/10.6084/m9.figshare.21747461.v7) | CC0 |
| Retraction Watch database | retraction labels, dates, reasons | [gitlab.com/crossref/retraction-watch-data](https://gitlab.com/crossref/retraction-watch-data), commit `a98cc7e`; linked table [doi:10.5281/zenodo.23874477](https://doi.org/10.5281/zenodo.23874477) | see the source; please cite it |
| PubMed 2026 baseline | biomedical flag, reviews, notice records, article-type sensitivity | [NLM baseline files](https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/) | courtesy of the U.S. National Library of Medicine |

## Rigour by design

- **Pre-specified.** [`SPEC.md`](SPEC.md) fixed populations, score, analyses and robustness checks before any score
  existed; its hash is recorded in every run. It was not deposited with a registry, so it is a pre-specification, not a
  formal pre-registration. The original repository and commit history remain private; the public release cannot
  resolve commit `293755b1`. [`experiments/spec_provenance.json`](experiments/spec_provenance.json) documents this.
- **Post hoc, but planned.** Each later analysis was written into [`POSTHOC.md`](POSTHOC.md) with its margins and
  expected directions before it was run; one rule was amended (and the affected runs redone) before its results were read.
- **Frozen scores.** Evaluation scripts check the hashes of the frozen score and count files before they read any label,
  and new evaluation scripts first reproduce the earlier estimates exactly.
- **Tested counting.** The disruption counts and the yearly counts are tested against brute-force counts on random graphs.
- **Nothing overwritten.** Every run gets its own folder; replaced runs keep a `SUPERSEDED.txt` explaining why.
- **Verified references.** References were checked through their DOI, publisher page or arXiv record
  ([`paper/bib_verification.tsv`](paper/bib_verification.tsv)).

## Responsible use

- No author names, and **no score, rank or list of non-retracted papers**; per-paper tables stay on the analysis machine.
- A retraction is a public editorial label; it does not by itself imply misconduct. All results are associations.

## Citation

Please cite the paper (details will be added on publication) and this repository; GitHub's *Cite this repository*
button uses [`CITATION.cff`](CITATION.cff).

## Licences

Code: [MIT](LICENSE). Run records, tables, figures and documentation: [CC BY 4.0](LICENSE-DATA). The input datasets
keep their own terms.

## Generative AI

Claude Opus 5.5 (Anthropic) was used as a coding and writing assistant under the author's direction;
GitHub Copilot CLI 1.0.116 (GitHub, powered by OpenAI's GPT-6.1 Sol) assisted added analysis/visualization code,
tests and manuscript edits. The author directed these revisions and confirmed checks of analysis,
numbers and sources. Final review of the new P16 findings and current text remains required before submission.
