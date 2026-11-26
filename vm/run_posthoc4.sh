#!/usr/bin/env bash
# Run ON THE VM: nohup bash ~/e/vm/run_posthoc4.sh YYYYMMDD NN < /dev/null > /dev/null 2>&1 &
# POSTHOC.md round 4 (P11, descriptive: the controls behind the primary comparisons): test of e11 on synthetic data,
# then E11 on the frozen inputs of v1 (replays E4 first). Deallocates the VM at the end (AUTO_DEALLOCATE=1 by default).
set -uo pipefail
DATE="${1:?usage: run_posthoc4.sh YYYYMMDD NN}"; NN="${2:?usage: run_posthoc4.sh YYYYMMDD NN}"
E=~/e; PY=${E_PY:-~/mamba/envs/d/bin/python}; LOG=$E/vm/run_posthoc4_${DATE}_$NN.log
export E_DATA=$E/data/work; mkdir -p "$E_DATA/tmp"
E2_5=e02_pop_20261110_01; E3_5=e03_cd5_20261110_01; E4_5=e04_eval_20261110_01
E2_3=e02_pop_cd3_20261110_01; E3_3=e03_cd5_cd3_20261110_01; E4_3=e04_eval_cd3_20261110_01
E11=e11_controls_${DATE}_$NN
finish() { echo "$(date -u +%FT%TZ) run_posthoc4 exit code $1" | tee -a "$LOG"
  if [ "${AUTO_DEALLOCATE:-1}" = "1" ]; then bash "$E/vm/self_deallocate.sh"; fi; exit "$1"; }
step() {  # step NAME DIR CMD... ; stdout.log is copied into the run folder (when it exists) and its checksums refreshed
  local name=$1 dir=$2; shift 2
  echo "$(date -u +%FT%TZ) START $name" | tee -a "$LOG"
  ( cd "$E/experiments/$dir" && /usr/bin/time -v "$PY" "$@" ) > "$E_DATA/tmp/$name.log" 2>&1; local rc=$?
  cat "$E_DATA/tmp/$name.log" >> "$LOG"
  if [ -d "$E/experiments/$dir/runs/$name" ]; then cp "$E_DATA/tmp/$name.log" "$E/experiments/$dir/runs/$name/stdout.log"
    (cd "$E/experiments/$dir/runs/$name" && sha256sum $(ls | grep -v SHA256SUMS) > SHA256SUMS); fi
  echo "$(date -u +%FT%TZ) END $name rc=$rc" | tee -a "$LOG"; return $rc
}
{ echo "$(date -u +%FT%TZ) run_posthoc4 $DATE $NN on $(hostname); python $($PY --version 2>&1)"
  sha256sum $E/SPEC.md $E/POSTHOC.md $E/experiments/e11_controls/*.py; } >> "$LOG" 2>&1
step test_e11 e11_controls test_e11.py || finish 10
step "$E11" e11_controls e11_controls.py "$E11" "$E2_5" "$E3_5" "$E4_5" "$E2_3" "$E3_3" "$E4_3" || finish 20
echo "$(date -u +%FT%TZ) all done. On the laptop: vm/vmctl.sh fetch $E11" | tee -a "$LOG"
finish 0
