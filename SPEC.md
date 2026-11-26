# Project E specification (pre-specified design, v1, 2026-11-09)

Written **before any disruption score is computed**. Its SHA-256 is stored in the `run.json` of every score and
evaluation run. Any later change gets a new version (v2, ...) with a dated reason, and runs say which version they used.
Analyses not listed here are reported as **post hoc**. This is a pre-specified design in a private repository, not a
public pre-registration; never call it "pre-registered".

## 1. Question
Do papers that were later retracted, in particular for paper mills and misconduct, score as **disruptive** on the
CD index, compared with papers from the same journal and year? And how many would pass the "highly disruptive"
thresholds used in evaluation? Gap: `lit/LIT.md` (no prior study; closest You et al. 2022, predatory venues).

- **RQ1 (primary):** CD5 of retracted vs matched control papers.
- **RQ2:** the same by retraction-reason class (paper mill, misconduct, honest error, other).
- **RQ3:** share of retracted vs control papers above the top-5% and top-1% CD5 thresholds of their publication year.
- **Context (not a contribution):** the yearly mean CD5 of a random biomedical sample, with and without CD5 = 1 papers
  (the Holst et al. zero-reference debate), so readers can place the groups.

## 2. Data (all on the VM; no new downloads)
- Citation graph: OpenCitations January 2024 (`edges.parquet`, `pubs_slim.parquet`, `pubs_j.parquet` from C run
  `c6_full_20261031_02`). Effectively complete to about Sept 2023 (D run `d00_cutoff_20261101_01`).
- Retraction labels: Retraction Watch commit `a98cc7e` (D run `d02_rw_20261101_01`), matched to graph nodes by D run
  `d05_match_20261101_02` (`rw2_*`, `rw_iid_*`). Reasons from `rw_papers_d02_rw_20261101_01.parquet`.
- PubMed 2026 baseline parse (D run `d04_pubmed_20261101_01`): biomedical flag, publication types, retraction flag.
- Disk: VM restored from `snap-project-d-osdisk-20261109` (D's archive; never modified).

## 3. Populations
- **Biomedical node:** as in D (PMID in Meta, or DOI in the PubMed baseline).
- **Eligible focal paper:** biomedical; `pub_year` 2000–2017 (so the 5-year window ends by 2022, inside the graph);
  has a `journal_id`; at least one reference in the graph (CD5 is undefined without references; the share of
  zero-reference papers in each group is reported separately); not a DOI duplicate (D's `dup` rule).
- **Retracted (exposed):** eligible and matched to a Retraction Watch paper with nature "Retraction". Reinstated papers
  are excluded.
  - **Primary set: retracted after the window:** first notice date later than 31 Dec of `pub_year + 5`, so the
    CD5 window ends before the retraction and the retraction cannot affect the score.
  - **Secondary set:** all retracted eligible papers.
- **Controls:** eligible papers from the same `journal_id × pub_year` that are not matched to any Retraction Watch retraction (D's paper table holds
  retractions only) and not flagged retracted in PubMed (publication type D016441). **K = 5** per retracted paper, the 5 with the lowest
  `hash(iid, 20261109)` in the stratum; without replacement within a stratum. Strata with no control are dropped and
  counted.
- **Context sample:** eligible papers with `hash(iid, 20261109) % 1000 < 2` (≈ 0.2%), any retraction status.

## 4. Reason classes (RQ2)
From the Retraction Watch reason list of each paper (exact strings, `reason_counts.csv` in D run `d02_rw_20261101_01`),
assigned in this order (first match wins):
1. **paper mill:** `Paper Mill`.
2. **misconduct:** any of `Falsification/Fabrication of Data`, `Falsification/Fabrication of Image`,
   `Falsification/Fabrication of Results`, `Manipulation of Images`, `Manipulation of Results`, `Manipulation of Data`,
   `Misconduct by Author`, `Misconduct - Official Investigation(s) and/or Finding(s)`, `Euphemisms for Misconduct`,
   `Plagiarism of/in Article`, `Plagiarism of Text`, `Plagiarism of Image`, `Plagiarism of Data`,
   `Euphemisms for Plagiarism`, `Duplication of/in Image`, `Compromised Peer Review`, `Rogue Editor`,
   `False/Forged Authorship`, `False/Forged Affiliation`, `Computer-Aided Content or Computer-Generated Content`,
   `Hoax Paper`, `Sabotage of Materials/Methods`.
3. **honest error:** any reason starting with `Error in` or `Error by`, or `Results Not Reproducible`,
   `Contamination of Cell Lines/Tissues`, `Contamination of Materials`, `Doing the Right Thing`.
4. **other:** everything else (including `Notice - Limited or No Information`).

## 5. Score
For focal paper *f* published in year *t*, with reference set R(f) in the graph, and window W = years [t, t+5]:
- A = papers published in W that cite f; B = papers published in W, other than f, that cite at least one paper in R(f).
- n_i = |A \ B|, n_j = |A ∩ B|, n_k = |B \ A|.
- **CD5 = (n_i − n_j) / (n_i + n_j + n_k)**; undefined (NULL) if the denominator is 0.
- TODO(verify): formula and window against the full texts of Funk & Owen-Smith 2017 and Park et al. 2023 (Methods
  state "five years after the year of each paper's publication"; the exact year bounds are not stated in the arXiv
  text). Sensitivity: W = [t+1, t+5].
- Also stored per paper: n_i, n_j, n_k, reference count, CD5 = 1 flag (n_j = n_k = 0), citations in W.
- Scores are computed **from the list of focal iids only** (no labels are read by the score script). They are frozen
  (SHA-256 in `run.json`) before the evaluation script joins labels.

## 6. Analyses
- **RQ1 (primary):** mean CD5 difference (retracted − controls) within strata, averaged over retracted papers;
  95% CI by bootstrap over strata (2,000 draws, `SeedSequence(20261109)`, rows sorted by iid). Papers with undefined
  CD5 (no citing papers in W) are excluded and counted per group.
  - Also: Mantel–Haenszel odds ratio for CD5 > 0 ("disruptive" sign), strata = journal × year.
- **RQ2:** RQ1 per reason class.
- **RQ3:** thresholds = 95th and 99th percentiles of CD5 per `pub_year` in the context sample. MH odds ratio for
  CD5 ≥ threshold, retracted vs controls; share above each threshold with Wilson intervals.
- **Pre-specified robustness:** (a) excluding CD5 = 1 papers (Holst et al.); (b) excluding reviews (PubMed types
  D016454, D000078182, D017418); (c) reference-count deciles inside strata (D15 lesson); (d) window [t+1, t+5];
  (e) the secondary set (all retracted); (f) papers with at least 5 citations in W.
- **Context:** mean CD5 per year 2000–2017 in the context sample, all papers and without CD5 = 1.

## 7. Reporting rules
- Group-level results only. Never list or release per-paper scores for papers that are not retracted.
- Report counts at every filter step (eligible, matched, dropped strata, undefined CD5).
- Every number in the paper traces to a run in `experiments/*/runs/` (`FINDINGS.md`).
