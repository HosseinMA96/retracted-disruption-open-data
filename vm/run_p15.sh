#!/usr/bin/env bash
# Execute on the preserved VM; laptop fetches aggregate outputs and then deallocates.
set -euo pipefail
RUN="${1:?usage: run_p15.sh RUN_ID}"
E="$HOME/e"; PY="${E_PY:-$HOME/mamba/envs/d/bin/python}"
export E_DATA="$E/data/work" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p "$E_DATA/tmp"
DIR="$E/experiments/e15_citers"
LOG="$E_DATA/tmp/$RUN.log"
test ! -e "$DIR/runs/$RUN"
cd "$DIR"
"$PY" test_citers.py > "$LOG" 2>&1
set +e
/usr/bin/time -v "$PY" e15_citers.py "$RUN" >> "$LOG" 2>&1
RC=$?
set -e
if [ -d "$DIR/runs/$RUN" ]; then
  cp "$LOG" "$DIR/runs/$RUN/stdout.log"
  (cd "$DIR/runs/$RUN" && sha256sum ./*.json stdout.log > SHA256SUMS)
fi
cat "$LOG"
exit "$RC"
