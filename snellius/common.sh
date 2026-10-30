# Sourced by the other scripts.
# Big files go to scratch-shared (home is 200 GB). Scratch is cleaned after
# ~14 days without access: copy results you want to keep.
export WORK=/scratch-shared/$USER/thinkqe
export HF_HOME=$WORK/hf_cache
export PYSERINI_CACHE=$WORK/pyserini_cache
export MODEL=${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}   # model used in the paper
mkdir -p "$WORK" "$HF_HOME" "$PYSERINI_CACHE"

# Qwen3 models need the newer environment
case "$MODEL" in *Qwen3*) CONDA_ENV=thinkqe_qwen3 ;; *) CONDA_ENV=thinkqe_310 ;; esac

set +u  # module/conda scripts use unset variables
module purge
module load 2023
module load Anaconda3/2023.07-2
source "$(conda info --base)/etc/profile.d/conda.sh"
# fully deactivate whatever was active in the calling shell, then activate cleanly
while [ "${CONDA_SHLVL:-0}" -gt 0 ]; do conda deactivate; done
conda activate $CONDA_ENV
set -u
case "$(which python)" in
  *"/envs/$CONDA_ENV/"*) echo "Using $(which python)" ;;
  *) echo "ERROR: env $CONDA_ENV not active (python is $(which python))"; exit 1 ;;
esac
