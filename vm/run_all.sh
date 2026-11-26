#!/usr/bin/env bash
# Run ON THE VM:  nohup bash ~/e/vm/run_all.sh YYYYMMDD [NN] > /dev/null 2>&1 &
# Unit test -> E2 populations -> E3 frozen CD5 scores -> E4 evaluation, each as a new run (never overwrites).
# Each step's stdout goes to its run folder (stdout.log) and to ~/e/vm/run_all_<DATE>.log.
# The VM deallocates itself at the end, success or failure (AUTO_DEALLOCATE=1 by default).
set -uo pipefail
DATE="${1:?usage: run_all.sh YYYYMMDD [NN]}"; NN="${2:-01}"
E=~/e; PY=${E_PY:-~/mamba/envs/d/bin/python}; LOG=$E/vm/run_all_${DATE}_$NN.log
export E_DATA=$E/data/work; mkdir -p "$E_DATA/tmp"
E2=e02_pop_${DATE}_$NN; E3=e03_cd5_${DATE}_$NN; E4=e04_eval_${DATE}_$NN
finish() {
  echo "$(date -u +%FT%TZ) run_all exit code $1" | tee -a "$LOG"; df -h ~ | tail -1 | tee -a "$LOG"; free -g | head -2 | tee -a "$LOG"
  if [ "${AUTO_DEALLOCATE:-1}" = "1" ]; then bash "$E/vm/self_deallocate.sh"; fi
  exit "$1"
}
step() {  # step NAME DIR CMD... ; stdout.log is copied into the run folder when the run folder exists
  local name=$1 dir=$2; shift 2
  echo "$(date -u +%FT%TZ) START $name" | tee -a "$LOG"
  ( cd "$E/experiments/$dir" && /usr/bin/time -v "$PY" "$@" ) > "$E_DATA/tmp/$name.log" 2>&1; local rc=$?
  cat "$E_DATA/tmp/$name.log" >> "$LOG"
  [ -d "$E/experiments/$dir/runs/$name" ] && cp "$E_DATA/tmp/$name.log" "$E/experiments/$dir/runs/$name/stdout.log"
  echo "$(date -u +%FT%TZ) END $name rc=$rc" | tee -a "$LOG"
  return $rc
}
{
  echo "$(date -u +%FT%TZ) run_all $DATE on $(hostname); python $($PY --version 2>&1); git-less code copy in $E"
  sha256sum $E/SPEC.md $E/experiments/*/*.py | tee -a "$LOG"
} >> "$LOG" 2>&1
step test_cd e03_cd5 test_cd.py || finish 10
step "$E2" e02_population e02_population.py "$E2" || finish 20
step "$E3" e03_cd5 e03_cd5.py "$E3" "$E2" 16 || finish 30
step "$E4" e04_eval e04_eval.py "$E4" "$E2" "$E3" || finish 40
# stdout.log was added after run.finish(): refresh the checksum list of each run folder
for d in $E/experiments/*/runs/*_${DATE}_$NN; do (cd "$d" && sha256sum $(ls | grep -v SHA256SUMS) > SHA256SUMS); done
echo "$(date -u +%FT%TZ) all done. On the laptop: vm/vmctl.sh fetch $E2 ; fetch $E3 ; fetch $E4" | tee -a "$LOG"
finish 0
