# Project E literature (E1 gate, 2026-11-09)

## v0.8 wording check (2026-11-26)
Petersen et al. (2025), DOI 10.1016/j.joi.2024.101605: the author-hosted published manuscript's abstract
says disruptiveness incrementally increased in 2005-2015; the Introduction describes the net temporal/team-size
effects as "at the level of noise." Related work now reports a small increase with that qualification.
Full text checked at https://re.public.polimi.it/retrieve/dba99d17-aef1-47a8-93b3-261741391541/informetrics_2025.pdf .

Every DOI below resolved through Crossref or DataCite in run `experiments/e01_lit/runs/e01_doi_20261109_01` (title, venue, year, first author recorded in `dois.json`), except the two marked *search*, found by Crossref bibliographic query in the same run (`queries.json`). "Read": **full**, **abstract**, **inventory** (as described in Wu et al. 2026's Table 1, read verbatim via HTML on 2026-11-09), or **title**. Nothing below *full/abstract* may be cited for a specific finding before it is read.

## The debate (core)
| Reference | DOI | Read | Point |
|---|---|---|---|
| Funk & Owen-Smith (2017), Management Science | 10.1287/mnsc.2015.2366 | title | CD index definition |
| Wu, Wang & Evans (2019), Nature | 10.1038/s41586-019-0941-9 | title | Large teams develop, small teams disrupt |
| Park, Leahey & Funk (2023), Nature | 10.1038/s41586-022-05543-x | inventory | Papers and patents becoming less disruptive; PubMed used as robustness data |
| Holst et al. (2024), arXiv | 10.48550/arXiv.2402.14583 | search summary | Zero-reference records (CD5 = 1) drive the decline |
| Holst et al. (2026), Nature 656 (Matters Arising) | 10.1038/s41586-026-10787-y | title (paywalled) | "Dataset artefacts can **partially** drive the measured decline" |
| Park, Leahey & Funk (2026), Nature 656 (Reply) | 10.1038/s41586-026-10788-x | title (paywalled) | Reply to Holst et al. |
| Park, Leahey & Funk (2025), arXiv | 10.48550/arXiv.2503.00184 | inventory | Decline survives critics' own data/metric/model |
| Petersen, Arroyave & Pammolli (2024), QSS | 10.1162/qss_a_00333 | inventory | Citation inflation biases CD |
| Petersen et al. (2025), J Informetrics | 10.1016/j.joi.2024.101605 | inventory | Re-analysis: trend at noise level after controls |
| Wu, Wu, Park, Leahey & Funk (2026), arXiv | 10.48550/arXiv.2602.05140 | **full (Table 1 + §1–5)** | Inventory of 105 studies; 96 report decline |
| Leibel & Bornmann (2023), Scientometrics | 10.1007/s11192-023-04873-5 (*search*) | title | Review: data-induced biases of the index |
| Lin, Li & Wu (2025), arXiv / QSS | 10.48550/arXiv.2504.04677 | search summary | D-index = displacement of most-cited reference; 49M OpenAlex articles |
| Deng et al. (2025), Nat Comput Sci | 10.1038/s43588-025-00808-7 | inventory | Persistent disruption |
| Sixt & Pasin (2024), QSS | 10.1162/qss_a_00328 | inventory | CD at scale on Dimensions |
| Chen et al. (2025), arXiv | 10.48550/arXiv.2504.07828 | title | Thresholds for using the index **in research evaluation** |

## Biomedicine / PubMed (covered)
| Reference | DOI | Read | Point |
|---|---|---|---|
| Sheng et al. (2023), Scientometrics | 10.1007/s11192-023-04751-0 | inventory | PubMed biomedicine 2001–2010, decline |
| Bentley et al. (2023), Adv Complex Syst | 10.1142/s0219525923500066 | inventory | PubMed life sciences; mixed (growth since 2000) |
| Wang (2024), SSRN | 10.2139/ssrn.4923505 | inventory | PubMed 1950–2021, 8.7M, decline |
| Copara et al. (2024), arXiv | 10.48550/arXiv.2406.18792 | inventory | Decline "holds statistically across all top-level MeSH categories" |
| Surgical/clinical subfield studies (radiology, plastic, craniofacial, pediatric, colorectal surgery, breast cancer, pharmacy, fetal surgery) | listed in Wu et al. 2026 Table 1 (#7–10, #19, #20, #81, #103) | inventory | One subfield each |

## Open data / data quality (covered)
| Reference | DOI | Read | Point |
|---|---|---|---|
| Jiang & Liu (2024), J Inf Sci | 10.1177/01655515241263545 | title | CD from OpenCitations COCI |
| Jiang et al. (2025), J Scholarly Publishing | 10.3138/jsp-2023-0056 | inventory | OpenCitations; Asian journals |
| *Do OpenCitations and Dimensions serve as an alternative to WoS for calculating disruption indexes?* (2025), J Informetrics | 10.1016/j.joi.2025.101685 (*search*) | search summary | Missing citations in OpenCitations shift DI vs WoS |
| Spinellis (2023), PLOS ONE | 10.1371/journal.pone.0294946 | inventory | Crossref-based open reproducible CD trends |
| Yu, Rahwan & Jia (2025), arXiv | 10.48550/arXiv.2504.09589 | inventory | Robustness to citation inflation and zero-reference works |

## Integrity link (the gap)
| Reference | DOI | Read | Point |
|---|---|---|---|
| You et al. (2022), J Informetrics | 10.1016/j.joi.2022.101294 | inventory | **Closest:** "questionable publications were less disruptive" (Scopus, predatory venues) |
| Project D lit (`../../D_retraction_contamination/lit/LIT.md`) | — | — | Retraction citation-network work; none uses the disruption index |

## Gate result (2026-11-09)
- **Covered:** (1) the decline in biomedicine, including a breakdown over all top-level MeSH categories (Copara et al. 2024) and many single-subfield studies; (2) disruption on open data, including OpenCitations vs WoS (J Informetrics 2025); (3) the zero-reference artefact debate, now in Nature (Holst et al. 2026 + Reply 2026).
- **Not found** (searches 2026-11-09; the 105-study inventory mentions no retractions or paper mills): any study of the disruption index for **retracted or paper-mill papers**. Closest is You et al. 2022 (predatory venues, Scopus).
- **Consequence:** the original E framing (open-data biomedical replication with MeSH/NIH splits) is **not novel enough**. Proposed lead: the integrity link (see `../TODO.md`, decision E-R1).

## Gap statement (draft)
The disruption index is now widely used, and has been proposed for research evaluation with thresholds, but no study has asked how it scores papers later retracted for misconduct or produced by paper mills. If fraudulent papers score as disruptive, the index rewards the behaviour that integrity screening tries to catch. Using a prospective design on the open biomedical citation graph, E measures the disruption of retracted and paper-mill papers against matched controls from the same journal and year, by retraction reason, and tests how many would pass proposed evaluation thresholds.

## Still to read in full before writing
Holst et al. 2026 and Park et al. 2026 (Nature; paywalled: user PDF needed), J Informetrics 2025 (10.1016/j.joi.2025.101685), You et al. 2022, Chen et al. 2025, Leibel & Bornmann 2023, Funk & Owen-Smith 2017 (definition).

## Update 2026-11-23 (claim check; `CLAIM_CHECK_20261123.md`, spot-checked against primary texts)
- **Gap statement corrected.** Copara et al. (arXiv 2406.18792, **v5 read in full**) compute a disruption measure for
  **MeSH concepts** and find that concepts annotating retracted papers differ from others in 7 of 8 years (2014–2021).
  This is concept-level and retrospective; no paper-level comparison of retracted papers with matched controls, scored
  before retraction, was found. The paper now cites Copara et al. as the second integrity link next to You et al. 2022.
- **Wording corrections applied in v0.2:** zero-reference papers have CD = 1 when cited (undefined otherwise); Chen et
  al. 2025 recommend minimum reference/citation counts and windows (not a "highly disruptive" cut-off); Wu et al. 2026
  inventory = 105 empirical studies bearing on whether innovation is becoming less disruptive; Park et al. 2023 decline
  "over the decades studied" (patent series does not start in 1945); Bentley et al. 2023 dropped (PubMed claim not
  verifiable); Xu et al. 2025 supports "source choice affects scores", not "coverage varies by publisher and year";
  Lin et al. now cited in its published QSS 2026 version; Cabanac 2024 cited for detecting citations to retracted work.
- **Window convention verified:** cdindex (`src/cdindex.c`, commit 4eece64) counts citing works with
  `timestamp > focal` and `<= focal + delta` (same-year citers excluded with year timestamps = window t+1…t+5);
  Funk & Owen-Smith 2017 (author-hosted full text): "forward citations made during the first five years after the
  focal patent's issue"; Park et al. preprint v5: "five years after the year of each paper's publication".
- **Top 5% = "highly disruptive":** Wu, Wang & Evans 2019 (arXiv v2, full text): "72% more likely to be highly
  disruptive (top 5% disruption)".

| New reference (all DOIs resolved 2026-11-23) | DOI | Read | Used for |
|---|---|---|---|
| Wu & Yan (2019), arXiv | 10.48550/arXiv.1905.03461 | abstract | DI_nok = (SC − DC)/(SC + DC) proposed |
| Bornmann, Devarakonda, Tekles & Chacko (2020), QSS | 10.1162/qss_a_00068 | via claim check (author manuscript) | DI_1^nok notation |
| Lin, Li & Wu (2026), QSS | 10.1162/QSS.a.409 | arXiv v1 full | displacement interpretation (published version) |
| Schuirmann (1987), J Pharmacokinet Biopharm | 10.1007/BF01068419 | abstract | TOST |
| Lakens (2017), SPPS | 10.1177/1948550617697177 | PMC full (claim check) | equivalence tests, margins |
| Jiang et al. (2015), AAPS J | 10.1208/s12248-015-9753-5 | PMC full (claim check) | 0.80–1.25 ratio convention |
| Hsiao & Schneider (2021), QSS | 10.1162/qss_a_00155 | PMC full (claim check) | notices among citing contexts (612 excluded) |
| Xu et al. (2025), Scientific Data (CrossDI) | 10.1038/s41597-025-06232-w | full (claim check) | OpenCitations lowest coverage of three sources |
| Azoulay, Furman, Krieger & Murray (2015), REStat | 10.1162/REST_a_00469 | NBER w18499 full | retracted papers lose 69% of citations vs controls |
