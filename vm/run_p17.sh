#!/usr/bin/env bash
set -euo pipefail
RUN="${1:?usage: run_p17.sh RUN_ID PLAN_COMMIT}"
PLAN="${2:?public pre-run plan commit is required}"
E="$HOME/e"; PY="${E_PY:-$HOME/mamba/envs/d/bin/python}"
export E_DATA="$E/data/work" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
DIR="$E/experiments/e17_coverage"; LOG="$E_DATA/tmp/$RUN.log"
mkdir -p "$E_DATA/tmp"
test ! -e "$DIR/runs/$RUN"
cd "$DIR"
"$PY" test_coverage.py > "$LOG" 2>&1
set +e
/usr/bin/time -v "$PY" e17_coverage.py "$RUN" "$PLAN" >> "$LOG" 2>&1
RC=$?
set -e
if [ -d "$DIR/runs/$RUN" ]; then
  cp "$LOG" "$DIR/runs/$RUN/stdout.log"
  (cd "$DIR/runs/$RUN" && sha256sum ./*.json stdout.log > SHA256SUMS)
fi
cat "$LOG"
exit "$RC"
