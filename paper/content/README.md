# Central paper content (Paper E)
Single source of truth for the text; journal versions only change the wrapper (as in Papers C and D).
- Files: meta, abstract, highlights, intro, related, methods, results, discussion, conclusions, availability, ai_use.
- Figure: `../figures/fig1_forest.pdf` from `experiments/e06_figures` run `e06_fig_20261110_04`.
- References: `../refs.bib`, rebuilt by `../build_refs.py` from `../dois.txt` and `../bib_raw/` (DOI content negotiation); pure ASCII.
- Numbers trace to `../../FINDINGS.md`. No first person (single author).
- Build: `journals/joi/main.tex` (Elsevier elsarticle): `tectonic -X compile main.tex`.
