#!/bin/bash
# Submit one ThinkQE job per dataset for a model. From the repo root:
#   bash snellius/submit_runs.sh deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B dl19     # smoke test
#   bash snellius/submit_runs.sh deepseek-ai/DeepSeek-R1-Distill-Qwen-14B all       # all 9 datasets
#   bash snellius/submit_runs.sh <model> biology economics                          # pick datasets
# Options (environment variables):
#   BATCH=true   one vLLM call per round instead of per query (needs batching.patch applied)
#   SEED=1       vLLM seed (default 0)
#   e.g.  BATCH=true SEED=1 bash snellius/submit_runs.sh deepseek-ai/DeepSeek-R1-Distill-Qwen-14B all
# Slurm only bills time actually used, so the time limits below are generous on purpose.
set -euo pipefail
MODEL=${1:?usage: submit_runs.sh <hf_model_id> <all|dataset...>}; shift
BRIGHT=(biology earth_science economics psychology robotics stackoverflow sustainable_living)
if [ "${1:-all}" = "all" ]; then DATASETS=(dl19 dl20 "${BRIGHT[@]}"); else DATASETS=("$@"); fi

for d in "${DATASETS[@]}"; do
  case $d in dl19|dl20) T=04:00:00 ;; *) T=08:00:00 ;; esac
  if [ "${BATCH:-false}" = "true" ] && ! grep -q batch_generation thinkqe.py; then
    echo "BATCH=true but batching.patch is not applied (run: git apply snellius/batching.patch)"; exit 1; fi
  MODEL=$MODEL BATCH=${BATCH:-false} SEED=${SEED:-0} sbatch --export=ALL --time=$T \
      --job-name="tqe_${d}_$(basename "$MODEL")$([ "${BATCH:-false}" = true ] && echo _b)_s${SEED:-0}" \
      snellius/run_thinkqe.job "$d"
done
squeue -u "$USER"
