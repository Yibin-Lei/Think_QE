# Reproducing ThinkQE's main results (Tables 3 and 4) on Snellius

All commands run from the repo root (`~/Think_QE_IR2`), with `snellius/` inside it.

## One-time setup (login node)
    bash snellius/00_setup_env.sh            # env for R1-14B, OpenThinker2, Phi-4-reasoning
    bash snellius/00_setup_env.sh qwen3      # env for Qwen3-8B/14B (only needed for step 4)
    tmux                                     # so downloads survive disconnects
    bash snellius/01_download.sh             # BRIGHT data, MS MARCO index, 1.5B + 14B models
    sbatch snellius/02_index_bright.job      # BRIGHT Lucene indexes (CPU, ~minutes)

## Batched generation (TA-approved)
    git apply snellius/batching.patch       # once; adds --batch_generation and --seed (default path unchanged)
    BATCH=true bash snellius/submit_runs.sh <model> all        # SEED=1, 2, ... for repeat runs

## Runs
1. Smoke test (~1 job):   `bash snellius/submit_runs.sh deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B dl19`
2. Main model (9 jobs):   `bash snellius/submit_runs.sh deepseek-ai/DeepSeek-R1-Distill-Qwen-14B all`
3. Check:                 `python snellius/collect_results.py`
4. Other models (download first with `bash snellius/01_download.sh <model>`), then
   `bash snellius/submit_runs.sh <model> all` for each of:
   Qwen/Qwen3-8B, Qwen/Qwen3-14B, open-thoughts/OpenThinker2-7B, microsoft/Phi-4-reasoning

Monitor: `squeue -u $USER`; logs are `thinkqe_tqe_<dataset>_<model>_<jobid>.out` in the repo root.
Outputs: `/scratch-shared/$USER/thinkqe/outputs/<dataset>_<model>/` (cleaned after ~14 days unused; copy what you keep).

Expect small differences from the paper: generation samples at temperature 0.7 with no fixed seed.
