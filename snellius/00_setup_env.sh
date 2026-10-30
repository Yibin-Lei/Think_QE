#!/bin/bash
# Run on a Snellius login node, from inside the repo:
#   bash snellius/00_setup_env.sh          -> env "thinkqe_310"   (R1-14B, OpenThinker2, Phi-4-reasoning)
#   bash snellius/00_setup_env.sh qwen3    -> env "thinkqe_qwen3" (Qwen3-8B / Qwen3-14B need newer vLLM)
set -eo pipefail   # no -u: conda activate uses unset variables

if [ "${1:-}" = "qwen3" ]; then ENV=thinkqe_qwen3; REQ=snellius/requirements_qwen3.txt
else ENV=thinkqe_310; REQ=snellius/requirements_snellius.txt; fi

module purge
module load 2023
module load Anaconda3/2023.07-2
source "$(conda info --base)/etc/profile.d/conda.sh"

conda create -y -n $ENV python=3.10
conda activate $ENV
conda install -y -c conda-forge openjdk=11
pip install -r $REQ
python -m spacy download en_core_web_sm

# Point pyjnius at the env's Java on every activation (location differs per openjdk build)
mkdir -p "$CONDA_PREFIX/etc/conda/activate.d"
cat > "$CONDA_PREFIX/etc/conda/activate.d/java.sh" <<'EOS'
export JVM_PATH="$(find "$CONDA_PREFIX" -name libjvm.so | head -1)"
export JAVA_HOME="$(dirname "$(dirname "$(dirname "$JVM_PATH")")")"
EOS
conda deactivate && conda activate $ENV

python -c "from pyserini.search.lucene import LuceneSearcher; print('pyserini OK')"
python -c "import vllm, torch; print('vllm', vllm.__version__, 'torch', torch.__version__)"
pip cache purge || true
echo "Environment $ENV ready."
