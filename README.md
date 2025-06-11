# ThinkQE: Query Expansion via an Evolving Thinking Process

This is the code implementation for the paper "ThinkQE: Query Expansion via an Evolving Thinking Process".

## Python environment

```bash
bash create_env.sh
```

## Data preparation
For TREC DL 2019 and 2020, we directly use the prebuilt indexes and queries from Pyserini.

For BRIGHT, the scripts to prepare the data are in the Readme of the `bright` folder.


## Running scripts
### Default Hyperparameters
```bash
NUM_INTERACTION=3
KEEP_PASSAGE_NUM=5
GEN_NUM=2
USE_PASSAGE_FILTER=true
ACCUMULATE=true
```
### TREC DL 2019

```bash
python3 thinkqe.py \
    --expansion_method thinkqe \
    --threads 16 --batch-size 128 --index msmarco-v1-passage \
    --topics dl19-passage --answer_key contents \
    --bm25 --disable_bm25_param --max_demo_len 128 \
    --trec_python_path <path_to_trec_python> \
    --generation_model <path_to_generation_model> \
    --keep_passage_num ${KEEP_PASSAGE_NUM} \
    --gen_num ${GEN_NUM} \
    --use_passage_filter ${USE_PASSAGE_FILTER} \
    --output_dir <path_to_output_dir> \
    --overwrite_output_dir \
    --temperature 0.7 \
    --write_top_passages \
    --accumulate ${ACCUMULATE}
```

### TREC DL 2020

```bash
python3 thinkqe.py \
    --expansion_method thinkqe \
    --threads 16 --batch-size 128 --index msmarco-v1-passage \
    --topics dl20 --qrels dl20-passage --answer_key contents \
    --bm25 --disable_bm25_param --max_demo_len 128 \
    --trec_python_path <path_to_trec_python> \
    --generation_model <path_to_generation_model> \
    --keep_passage_num ${KEEP_PASSAGE_NUM} \
    --gen_num ${GEN_NUM} \
    --use_passage_filter ${USE_PASSAGE_FILTER} \
    --output_dir <path_to_output_dir> \
    --overwrite_output_dir \
    --temperature 0.7 \
    --write_top_passages \
    --accumulate ${ACCUMULATE}
```

### BRIGHT

```bash
DATASET="biology"
# can also be "earth_science" "economics" "psychology" "robotics" "stackoverflow" "sustainable_living"
python3 thinkqe.py \
    --expansion_method thinkqe \
    --threads 16 --batch-size 128 --index ./bright/data/pyserini_indexes/${DATASET} \
    --topics ./bright/data/pyserini_queries/${DATASET}.tsv --answer_key contents \
    --qrels ./bright/data/pyserini_qrels/${DATASET}.tsv \
    --bm25 --disable_bm25_param --max_demo_len 512 \
    --trec_python_path <path_to_trec_python> \
    --generation_model <path_to_generation_model> \
    --keep_passage_num ${KEEP_PASSAGE_NUM} \
    --gen_num ${GEN_NUM} \
    --use_passage_filter ${USE_PASSAGE_FILTER} \
    --output_dir <path_to_output_dir> \
    --overwrite_output_dir \
    --temperature 0.7 \
    --write_top_passages \
    --accumulate ${ACCUMULATE}
```

