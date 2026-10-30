#!/bin/bash
# Run on a login node inside tmux (needs internet). Downloads data + the given models
# so GPU jobs can run offline. Safe to rerun: finished downloads are skipped.
#   bash snellius/01_download.sh                                   # data + smoke-test 1.5B + R1-14B
#   bash snellius/01_download.sh Qwen/Qwen3-8B Qwen/Qwen3-14B      # later: more models
set -euo pipefail
source "$(dirname "$0")/common.sh"

MODELS=("$@")
[ ${#MODELS[@]} -eq 0 ] && MODELS=(deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B deepseek-ai/DeepSeek-R1-Distill-Qwen-14B)
for m in "${MODELS[@]}"; do echo ">> $m"; python -c "import sys; from huggingface_hub import snapshot_download; snapshot_download(sys.argv[1])" "$m"; done

# DL19/DL20 queries + qrels: pyserini 0.22.1 downloads them from an Anserini URL that no
# longer exists, but it checks this cache folder first.
TQ=~/.cache/anserini/topics-and-qrels; mkdir -p $TQ
BASE=https://raw.githubusercontent.com/castorini/anserini-tools/master
for f in topics/topics.dl19-passage.txt topics/topics.dl20.txt qrels/qrels.dl19-passage.txt qrels/qrels.dl20-passage.txt; do
  [ -s $TQ/$(basename $f) ] || curl -fsSL -o $TQ/$(basename $f) $BASE/$f
done

python -c "from pyserini.search.lucene import LuceneSearcher; LuceneSearcher.from_prebuilt_index('msmarco-v1-passage'); print('MS MARCO index OK')"

# BRIGHT scripts write to a relative data/ folder, so they must run from bright/
if [ ! -f bright/data/pyserini_corpus/biology/biology.jsonl ]; then
  (cd bright && python write_pyserini_qrels.py && python write_pyserini_queries.py && python write_pyserini_corpus.py)
fi
echo "Downloads done."
