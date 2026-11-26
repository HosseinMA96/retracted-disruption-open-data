#!/usr/bin/env bash
# Build the Journal of Informetrics upload packages from ../../content (never edits the sources):
#   submission/       identified manuscript: flat main.tex (content inlined, LaTeX comments removed), refs.bib, main.bbl,
#                     figures, elsarticle.cls + elsarticle-harv.bst (LPPL, unchanged), main.pdf
#   submission_anon/  the same with \anontrue (no author block, footnote, CRediT or repository link) for
#                     double-anonymized review; title_page.tex/pdf provide the separate author information
#   joi_latex_source.zip, joi_latex_source_anon.zip, highlights.txt (plain text, one bullet per line)
# Elsevier compiles with pdflatex + bibtex, so main.tex must be pure ASCII and must not need fontspec.
# Re-run after any change to ../../content, ../../refs.bib or ../../figures.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; P="$(cd "$HERE/../.." && pwd)"
TECTONIC="${TECTONIC:-$HOME/miniforge3/envs/tectonic-env/bin/tectonic}"
DOCX_PYTHON="${DOCX_PYTHON:-python3}"
CLS_DIR="${CLS_DIR:-$(dirname "$(find "$HOME/.cache/tectonic" -name elsarticle.cls | head -1)")}"
FIGS="fig1_forest fig2_event"

flatten () {  # flatten SRC DST ANON(0/1)
  python3 - "$1" "$2" "$3" <<'PY'
import re, sys, pathlib
src, dst, anon = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3] == "1"
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
if anon:
    assert t.count("\\newif\\ifanon\\anonfalse") == 1
    t = t.replace("\\newif\\ifanon\\anonfalse", "\\newif\\ifanon\\anontrue")
assert "\\input{" not in t, "unresolved \\input"
assert "\\todo{" not in t and "TODO" not in t, "TODO left in the text"
bad = sorted({c for c in t if ord(c) > 127}); assert not bad, f"non-ASCII in main.tex: {bad}"
pathlib.Path(dst).write_text(t)
PY
}

build () {  # build OUTDIR ANON ZIPNAME
  local out="$HERE/$1"; rm -rf "$out"; mkdir -p "$out"
  flatten "$HERE/main.tex" "$out/main.tex" "$2"
  cp "$P/refs.bib" "$CLS_DIR/elsarticle.cls" "$CLS_DIR/elsarticle-harv.bst" "$out/"
  for f in $FIGS; do cp "$P/figures/$f.pdf" "$out/"; done
  ( cd "$out" && "$TECTONIC" -X compile --keep-intermediates main.tex >/dev/null 2>"$out/.build.err" ) || { cat "$out/.build.err"; exit 1; }
  if grep -q -E "panicked|Undefined|undefined" "$out/.build.err"; then cat "$out/.build.err"; exit 1; fi
  rm -f "$out/.build.err" "$out/main.aux" "$out/main.blg" "$out/main.log" "$out/main.out" "$out/main.spl"
  test -s "$out/main.bbl" || { echo "main.bbl missing"; exit 1; }
  ( cd "$out" && rm -f "../$3" && zip -q -X "../$3" main.tex main.bbl refs.bib elsarticle.cls elsarticle-harv.bst $(for f in $FIGS; do echo "$f.pdf"; done) )
  echo "$1: $(pdfinfo "$out/main.pdf" | awk '/^Pages/{print $2}') pages; $3: $(unzip -l "$HERE/$3" | tail -1 | awk '{print $2" files, "$1" bytes"}')"
}

build submission 0 joi_latex_source.zip
build submission_anon 1 joi_latex_source_anon.zip
( cd "$HERE" && "$TECTONIC" -X compile title_page.tex )
# Individual editable sources and figures are in submission/ or submission_anon/; ZIPs are also supplied.
"$DOCX_PYTHON" "$HERE/build_declaration.py"
test -s "$HERE/competing_interests.docx"
# the anonymized PDF must not name the author anywhere (text or metadata)
anon_txt=$(pdftotext "$HERE/submission_anon/main.pdf" -)      # no pipe into grep -q: with pipefail, SIGPIPE hides matches
if grep -q -i -E "Microsoft|hosseinm|HosseinMA96|retracted-disruption" <<< "$anon_txt"; then
  grep -n -i -E "Microsoft|hosseinm|HosseinMA96|retracted-disruption" <<< "$anon_txt"; echo "ABORT: author or repository identity in the anonymized PDF"; exit 1
fi
echo "anonymized PDF: third-person citations of the author's datasets (allowed): $(grep -c -i "Mohasel Arjomandi" <<< "$anon_txt") lines"
pdfinfo "$HERE/submission_anon/main.pdf" | grep -i -E "^(Author|Creator|Producer|Title):" || true
# plain-text highlights (one per line), from the LaTeX items
python3 - "$P/content/highlights.tex" "$HERE/highlights.txt" <<'PY'
import sys, re
items = [l[5:].strip().replace("\\%", "%") for l in open(sys.argv[1]) if l.startswith("\\item")]
assert 3 <= len(items) <= 5 and all(len(i) <= 85 for i in items), [len(i) for i in items]
open(sys.argv[2], "w").write("\n".join(items) + "\n")
print("highlights.txt:", len(items), "bullets, max", max(map(len, items)), "characters")
PY
