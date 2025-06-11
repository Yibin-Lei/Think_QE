# Original source: https://github.com/ielab/llm-rankers/tree/main/Rank-R1/bright
#
# This script indexes corpora using Pyserini for BRIGHT datasets
#


for dataset in biology earth_science economics psychology robotics stackoverflow sustainable_living pony leetcode aops theoremqa_theorems theoremqa_questions
do
python -m pyserini.index.lucene \
  --collection JsonCollection \
  --input data/pyserini_corpus/$dataset \
  --index data/pyserini_indexes/$dataset \
  --generator DefaultLuceneDocumentGenerator \
  --storePositions --storeDocvectors --storeRaw \
  --threads 12
done