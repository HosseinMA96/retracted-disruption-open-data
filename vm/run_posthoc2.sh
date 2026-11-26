#!/usr/bin/env bash
# Run ON THE VM: nohup bash ~/e/vm/run_posthoc2.sh YYYYMMDD NN > /dev/null 2>&1 &
# POSTHOC.md round 2 (P3-P8): unit test of yearly_lib (vs brute force and vs cd_lib), E7 label-free yearly counts
# (checked against both frozen E3 runs, then frozen), E8 evaluation (replays E4 exactly first). Each step is a new run.
# Deallocates the VM at the end, success or failure (AUTO_DEALLOCATE=1 by default).
set -uo pipefail
DATE="${1:?usage: run_posthoc2.sh YYYYMMDD NN}"; NN="${2:?usage: run_posthoc2.sh YYYYMMDD NN}"
E=~/e; PY=${E_PY:-~/mamba/envs/d/bin/python}; LOG=$E/vm/run_posthoc2_${DATE}_$NN.log
export E_DATA=$E/data/work; mkdir -p "$E_DATA/tmp"
E2_5=e02_pop_20261110_01; E3_5=e03_cd5_20261110_01; E4_5=e04_eval_20261110_01
E2_3=e02_pop_cd3_20261110_01; E3_3=e03_cd5_cd3_20261110_01; E4_3=e04_eval_cd3_20261110_01
E7=e07_yearly_${DATE}_$NN; E8=e08_posthoc2_${DATE}_$NN
finish() {
  echo "$(date -u +%FT%TZ) run_posthoc2 exit code $1" | tee -a "$LOG"; df -h ~ | tail -1 | tee -a "$LOG"; free -g | head -2 | tee -a "$LOG"
  if [ "${AUTO_DEALLOCATE:-1}" = "1" ]; then bash "$E/vm/self_deallocate.sh"; fi
  exit "$1"
}
step() {  # step NAME DIR CMD... ; stdout.log is copied into the run folder (when it exists) and its checksums refreshed
  local name=$1 dir=$2; shift 2
  echo "$(date -u +%FT%TZ) START $name" | tee -a "$LOG"
  ( cd "$E/experiments/$dir" && /usr/bin/time -v "$PY" "$@" ) > "$E_DATA/tmp/$name.log" 2>&1; local rc=$?
  cat "$E_DATA/tmp/$name.log" >> "$LOG"
  if [ -d "$E/experiments/$dir/runs/$name" ]; then cp "$E_DATA/tmp/$name.log" "$E/experiments/$dir/runs/$name/stdout.log"
    (cd "$E/experiments/$dir/runs/$name" && sha256sum $(ls | grep -v SHA256SUMS) > SHA256SUMS); fi
  echo "$(date -u +%FT%TZ) END $name rc=$rc" | tee -a "$LOG"; return $rc
}
{ echo "$(date -u +%FT%TZ) run_posthoc2 $DATE $NN on $(hostname); python $($PY --version 2>&1)"
  sha256sum $E/SPEC.md $E/POSTHOC.md $E/experiments/*/*.py; } >> "$LOG" 2>&1
step test_yearly e07_yearly test_yearly.py || finish 10
step "$E7" e07_yearly e07_yearly.py "$E7" "$E2_3,$E2_5" "$E3_3,$E3_5" || finish 20
step "$E8" e08_posthoc2 e08_eval.py "$E8" "$E2_5" "$E3_5" "$E4_5" "$E2_3" "$E3_3" "$E4_3" "$E7" || finish 30
echo "$(date -u +%FT%TZ) all done. On the laptop: vm/vmctl.sh fetch $E7 ; vm/vmctl.sh fetch $E8" | tee -a "$LOG"
finish 0
