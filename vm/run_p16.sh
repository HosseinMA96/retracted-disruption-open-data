#!/usr/bin/env bash
set -euo pipefail
RUN="${1:?usage: run_p16.sh RUN_ID PLAN_COMMIT}"
PLAN="${2:?public pre-run plan commit is required}"
E="$HOME/e"; PY="${E_PY:-$HOME/mamba/envs/d/bin/python}"
export E_DATA="$E/data/work" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
DIR="$E/experiments/e16_topic"; LOG="$E_DATA/tmp/$RUN.log"
mkdir -p "$E_DATA/tmp"
test ! -e "$DIR/runs/$RUN"
cd "$DIR"
"$PY" test_topic.py > "$LOG" 2>&1
set +e
/usr/bin/time -v "$PY" e16_topic.py "$RUN" "$PLAN" >> "$LOG" 2>&1
RC=$?
set -e
if [ -d "$DIR/runs/$RUN" ]; then
  cp "$LOG" "$DIR/runs/$RUN/stdout.log"
  (cd "$DIR/runs/$RUN" && sha256sum ./*.json stdout.log > SHA256SUMS)
fi
cat "$LOG"
exit "$RC"
