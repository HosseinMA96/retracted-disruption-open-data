#!/usr/bin/env bash
# Run ON THE VM: nohup bash ~/e/vm/run_posthoc.sh YYYYMMDD NN E2_V1 E3_V1 > /dev/null 2>&1 &
# POSTHOC.md P1 (on the v1 runs) and P2 (CD3, papers 2000-2019). Deallocates the VM at the end.
set -uo pipefail
DATE=$1; NN=$2; E2V1=$3; E3V1=$4
E=~/e; PY=${E_PY:-~/mamba/envs/d/bin/python}; LOG=$E/vm/run_posthoc_${DATE}_$NN.log
export E_DATA=$E/data/work; mkdir -p "$E_DATA/tmp"
P1=e05_refs_${DATE}_$NN; E2=e02_pop_cd3_${DATE}_$NN; E3=e03_cd5_cd3_${DATE}_$NN; E4=e04_eval_cd3_${DATE}_$NN
finish() { echo "$(date -u +%FT%TZ) run_posthoc exit code $1" | tee -a "$LOG"; [ "${AUTO_DEALLOCATE:-1}" = "1" ] && bash "$E/vm/self_deallocate.sh"; exit "$1"; }
step() {
  local name=$1 dir=$2; shift 2
  echo "$(date -u +%FT%TZ) START $name" | tee -a "$LOG"
  ( cd "$E/experiments/$dir" && /usr/bin/time -v "$PY" "$@" ) > "$E_DATA/tmp/$name.log" 2>&1; local rc=$?
  cat "$E_DATA/tmp/$name.log" >> "$LOG"
  if [ -d "$E/experiments/$dir/runs/$name" ]; then cp "$E_DATA/tmp/$name.log" "$E/experiments/$dir/runs/$name/stdout.log"
    (cd "$E/experiments/$dir/runs/$name" && sha256sum $(ls | grep -v SHA256SUMS) > SHA256SUMS); fi
  echo "$(date -u +%FT%TZ) END $name rc=$rc" | tee -a "$LOG"; return $rc
}
sha256sum $E/SPEC.md $E/POSTHOC.md $E/experiments/*/*.py >> "$LOG"
step "$P1" e05_posthoc e05_refs.py "$P1" "$E2V1" "$E3V1" || finish 10
step "$E2" e02_population e02_population.py "$E2" 2019 3 || finish 20
step "$E3" e03_cd5 e03_cd5.py "$E3" "$E2" 16 3 || finish 30
step "$E4" e04_eval e04_eval.py "$E4" "$E2" "$E3" || finish 40
finish 0
