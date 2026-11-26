#!/usr/bin/env bash
# Run ON THE VM: nohup bash ~/e/vm/run_posthoc3.sh YYYYMMDD NN < /dev/null > /dev/null 2>&1 &
# POSTHOC.md round 3 (P9 pre-trend checks of P6) on the frozen inputs of round 2. Deallocates the VM at the end.
set -uo pipefail
DATE="${1:?usage: run_posthoc3.sh YYYYMMDD NN}"; NN="${2:?usage: run_posthoc3.sh YYYYMMDD NN}"
E=~/e; PY=${E_PY:-~/mamba/envs/d/bin/python}; LOG=$E/vm/run_posthoc3_${DATE}_$NN.log
export E_DATA=$E/data/work; mkdir -p "$E_DATA/tmp"
E2_3=e02_pop_cd3_20261110_01; E3_3=e03_cd5_cd3_20261110_01; E7=e07_yearly_20261123_02; E8=e08_posthoc2_20261123_02
E9=e09_pretrend_${DATE}_$NN
finish() { echo "$(date -u +%FT%TZ) run_posthoc3 exit code $1" | tee -a "$LOG"
  if [ "${AUTO_DEALLOCATE:-1}" = "1" ]; then bash "$E/vm/self_deallocate.sh"; fi; exit "$1"; }
step() {
  local name=$1 dir=$2; shift 2
  echo "$(date -u +%FT%TZ) START $name" | tee -a "$LOG"
  ( cd "$E/experiments/$dir" && /usr/bin/time -v "$PY" "$@" ) > "$E_DATA/tmp/$name.log" 2>&1; local rc=$?
  cat "$E_DATA/tmp/$name.log" >> "$LOG"
  if [ -d "$E/experiments/$dir/runs/$name" ]; then cp "$E_DATA/tmp/$name.log" "$E/experiments/$dir/runs/$name/stdout.log"
    (cd "$E/experiments/$dir/runs/$name" && sha256sum $(ls | grep -v SHA256SUMS) > SHA256SUMS); fi
  echo "$(date -u +%FT%TZ) END $name rc=$rc" | tee -a "$LOG"; return $rc
}
{ echo "$(date -u +%FT%TZ) run_posthoc3 $DATE $NN on $(hostname)"; sha256sum $E/POSTHOC.md $E/experiments/e09_pretrend/*.py; } >> "$LOG" 2>&1
step "$E9" e09_pretrend e09_pretrend.py "$E9" "$E2_3" "$E3_3" "$E7" "$E8" || finish 10
echo "$(date -u +%FT%TZ) all done. On the laptop: vm/vmctl.sh fetch $E9" | tee -a "$LOG"
finish 0
