#!/usr/bin/env bash
# Build the identified Journal of Informetrics upload package (single-anonymized review):
#   submission/       identified manuscript: flat main.tex (content inlined, LaTeX comments removed), refs.bib, main.bbl,
#                     figures, elsarticle.cls + elsarticle-harv.bst (LPPL, unchanged), main.pdf
#   joi_latex_source.zip, highlights.txt and local competing_interests.docx
# Legacy submission_anon/ and joi_latex_source_anon.zip are not rebuilt and must not be uploaded to JOI.
# Elsevier compiles with pdflatex + bibtex, so main.tex must be pure ASCII and must not need fontspec.
# Re-run after any change to ../../content, ../../refs.bib or ../../figures.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; P="$(cd "$HERE/../.." && pwd)"
TECTONIC="${TECTONIC:-$HOME/miniforge3/envs/tectonic-env/bin/tectonic}"
DOCX_PYTHON="${DOCX_PYTHON:-python3}"
CLS_DIR="${CLS_DIR:-$(dirname "$(find "$HOME/.cache/tectonic" -name elsarticle.cls | head -1)")}"
FIGS="fig1_forest fig2_event fig3_population_flow"

flatten () {  # flatten SRC DST
  python3 - "$1" "$2" <<'PY'
import re, sys, pathlib
src, dst = pathlib.Path(sys.argv[1]), sys.argv[2]
def inline(text, cwd):
    def rep(m):
        f = cwd / m.group(1); f = f if f.suffix else f.with_suffix(".tex")
        return inline(f.read_text(), f.parent).rstrip("\n")
    return re.sub(r"\\input\{([^}]+)\}", rep, text)
t = inline(src.read_text(), src.parent)
out = []
for line in t.splitlines():
    if re.match(r"^\s*%", line):
        continue
    if line.startswith(r"\newcommand{\todo}"):
        continue
    s = re.sub(r"(?<!\\)%.*$", "", line)
    if s != line:
        s += "%"          # keep line joins such as "\resizebox{\linewidth}{!}{%"
    out.append(s)
t = "\n".join(out) + "\n"
t = t.replace("\\graphicspath{{../../figures/}}", "\\graphicspath{{./}}").replace("\\bibliography{../../refs}", "\\bibliography{refs}")
assert t.count("\\newif\\ifanon\\anonfalse") == 1, "JOI requires the identified manuscript"
assert "\\input{" not in t, "unresolved \\input"
assert "\\todo{" not in t and "TODO" not in t, "TODO left in the text"
bad = sorted({c for c in t if ord(c) > 127}); assert not bad, f"non-ASCII in main.tex: {bad}"
pathlib.Path(dst).write_text(t)
PY
}

build () {  # build OUTDIR ZIPNAME
  local out="$HERE/$1"; rm -rf "$out"; mkdir -p "$out"
  flatten "$HERE/main.tex" "$out/main.tex"
  cp "$P/refs.bib" "$CLS_DIR/elsarticle.cls" "$CLS_DIR/elsarticle-harv.bst" "$out/"
  for f in $FIGS; do cp "$P/figures/$f.pdf" "$out/"; done
  ( cd "$out" && "$TECTONIC" -X compile --keep-intermediates main.tex >/dev/null 2>"$out/.build.err" ) || { cat "$out/.build.err"; exit 1; }
  if grep -q -E "panicked|Undefined|undefined" "$out/.build.err"; then cat "$out/.build.err"; exit 1; fi
  rm -f "$out/.build.err" "$out/main.aux" "$out/main.blg" "$out/main.log" "$out/main.out" "$out/main.spl"
  test -s "$out/main.bbl" || { echo "main.bbl missing"; exit 1; }
  ( cd "$out" && rm -f "../$2" && zip -q -X "../$2" main.tex main.bbl refs.bib elsarticle.cls elsarticle-harv.bst $(for f in $FIGS; do echo "$f.pdf"; done) )
  echo "$1: $(pdfinfo "$out/main.pdf" | awk '/^Pages/{print $2}') pages; $2: $(unzip -l "$HERE/$2" | tail -1 | awk '{print $2" files, "$1" bytes"}')"
}

build submission joi_latex_source.zip
( cd "$HERE" && "$TECTONIC" -X compile title_page.tex )
( cd "$HERE" && "$TECTONIC" -X compile cover_letter.tex )
# Individual editable sources and figures are in submission/; see UPLOAD.md.
"$DOCX_PYTHON" "$HERE/build_declaration.py"
test -s "$HERE/competing_interests.docx"
# The identified PDF must retain authorship and the public code link.
identified_txt=$(pdftotext "$HERE/submission/main.pdf" -)
if ! grep -q "Hossein Mohasel Arjomandi" <<< "$identified_txt" || ! grep -q "HosseinMA96" <<< "$identified_txt"; then
  echo "ABORT: author or public repository link missing from the identified PDF"; exit 1
fi
echo "identified PDF: author and public repository link retained"
# plain-text highlights (one per line), from the LaTeX items
python3 - "$P/content/highlights.tex" "$HERE/highlights.txt" <<'PY'
import sys, re
items = [l[5:].strip().replace("\\%", "%") for l in open(sys.argv[1]) if l.startswith("\\item")]
assert 3 <= len(items) <= 5 and all(len(i) <= 85 for i in items), [len(i) for i in items]
open(sys.argv[2], "w").write("\n".join(items) + "\n")
print("highlights.txt:", len(items), "bullets, max", max(map(len, items)), "characters")
PY
