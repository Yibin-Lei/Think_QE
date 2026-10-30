"""Compare your ThinkQE runs with the paper (Tables 3 and 4). From the repo root:
    python snellius/collect_results.py            # all models
    python snellius/collect_results.py 14B        # only runs whose model name contains "14B"
Reads /scratch-shared/$USER/thinkqe/outputs/<dataset>_<model>[__<variant>]/.
Per run: final-round score vs the paper, plus generations without "</think>\\n" (what
extract_answer() splits on; in those the whole reasoning trace becomes the expansion).
Then, per model, mean ± std over all seeds of the batched runs."""
import json, os, glob, sys, statistics as st

OUT = f"/scratch-shared/{os.environ['USER']}/thinkqe/outputs"
FILTER = sys.argv[1] if len(sys.argv) > 1 else ""
BRIGHT = ["biology", "earth_science", "economics", "psychology", "robotics", "stackoverflow", "sustainable_living"]
ORDER = ["dl19", "dl20"] + BRIGHT
PAPER = {  # DL: (mAP, nDCG@10, R@1k); BRIGHT: nDCG@10 per domain
  "DeepSeek-R1-Distill-Qwen-14B": {"dl19": (45.9, 68.8, 89.3), "dl20": (43.9, 64.7, 87.8), "bright": [47.3, 52.5, 29.2, 40.0, 19.3, 28.0, 27.9]},
  "Qwen3-8B":                     {"dl19": (44.5, 65.0, 87.9), "dl20": (41.9, 62.8, 88.0), "bright": [49.8, 55.3, 27.6, 36.7, 19.9, 29.0, 28.3]},
  "Qwen3-14B":                    {"dl19": (45.2, 64.9, 88.4), "dl20": (42.4, 63.5, 88.4), "bright": [51.5, 53.2, 27.8, 37.2, 22.0, 16.1, 27.5]},
  "OpenThinker2-7B":              {"dl19": (44.8, 65.3, 87.3), "dl20": (43.2, 63.5, 87.9), "bright": [50.5, 54.1, 25.8, 36.7, 18.1, 28.2, 28.9]},
  "Phi-4-reasoning":              {"dl19": (44.0, 65.0, 87.1), "dl20": (43.0, 63.9, 87.2), "bright": [51.8, 53.5, 29.7, 38.5, 21.8, 29.3, 27.7]},
}
KEYS = ("map", "ndcg@10", "recall@1000")

def paper(model, ds):
    p = PAPER.get(model)
    if not p: return None
    return p[ds] if ds in ("dl19", "dl20") else p["bright"][BRIGHT.index(ds)]

def fmt(v): return "  -  " if v is None else f"{v:5.1f}"
def fmt3(t): return "/".join(fmt(x) for x in t) if t else "-"

runs = {}  # (model, variant) -> {ds: record}
for run in glob.glob(f"{OUT}/*"):
    name = os.path.basename(run)
    ds = next((d for d in ORDER if name.startswith(d + "_")), None)
    if ds is None: continue
    model, _, variant = name[len(ds) + 1:].partition("__")
    variant = variant or "unbatched_s0"
    if FILTER and FILTER not in model: continue
    files = sorted(glob.glob(f"{run}/bm25-aug*_result_retrieval.trec.metrics.json"),
                   key=lambda f: int(f.split("bm25-aug")[1].split("_")[0]))
    rec = {"round": None}
    if files:
        try:
            m = json.load(open(files[-1]))
        except (json.JSONDecodeError, OSError):   # file being written by a running job
            files = files[:-1]
            if not files:
                runs.setdefault((model, variant), {})[ds] = rec; continue
            m = json.load(open(files[-1]))
        rec["round"] = int(files[-1].split("bm25-aug")[1].split("_")[0])
        rec["vals"] = tuple(m.get(k) for k in KEYS) if ds in ("dl19", "dl20") else (m.get("ndcg@10"),)
        n = bad = 0
        for f in glob.glob(f"{run}/*.responses.json"):
            try: data = json.load(open(f))
            except (json.JSONDecodeError, OSError): continue   # being written
            for resps in data.values():
                for r in resps: n += 1; bad += "</think>\n" not in r
        rec["bad"], rec["n"] = bad, n
    runs.setdefault((model, variant), {})[ds] = rec

if not runs: print(f"No runs found in {OUT}"); sys.exit()
print("DL19/DL20: mAP/nDCG@10/R@1k.  BRIGHT: nDCG@10.  Only finished runs (round 3/3) are final.")
for (model, variant) in sorted(runs):
    print(f"\n== {model} [{variant}]")
    recs = runs[(model, variant)]
    for ds in ORDER:
        if ds not in recs: continue
        r = recs[ds]
        if r["round"] is None: print(f"  {ds:19s} no results yet"); continue
        p = paper(model, ds)
        ours = fmt3(r["vals"]) if ds in ("dl19", "dl20") else fmt(r["vals"][0])
        theirs = fmt3(p) if ds in ("dl19", "dl20") else fmt(p)
        note = f"round {r['round']}/3" + (f", {r['bad']}/{r['n']} unclosed </think>" if r["bad"] else "")
        print(f"  {ds:19s} ours {ours} | paper {theirs} | {note}")
    done = [recs[d]["vals"][0] for d in BRIGHT if d in recs and recs[d]["round"] == 3]
    if len(done) == 7:
        pb = PAPER.get(model, {}).get("bright")
        print(f"  {'BRIGHT average':19s} ours {fmt(st.mean(done))} | paper {fmt(st.mean(pb)) if pb else '-'}")

# Mean ± std over seeds (batched runs that finished all 3 rounds)
for model in sorted({m for m, _ in runs}):
    seeds = [v for (m, v) in runs if m == model and v.startswith("batched_s")]
    if len(seeds) < 2: continue
    print(f"\n== {model}: mean ± std over seeds ({', '.join(sorted(seeds))})")
    avgs = []
    for ds in ORDER:
        vals = [runs[(model, s)][ds]["vals"] for s in seeds
                if ds in runs[(model, s)] and runs[(model, s)][ds]["round"] == 3]
        if len(vals) < 2: continue
        cols = list(zip(*vals))
        ms = " / ".join(f"{st.mean(c):4.1f}±{st.stdev(c):3.1f}" for c in cols)
        p = paper(model, ds)
        print(f"  {ds:19s} n={len(vals)}  {ms} | paper {fmt3(p) if ds in ('dl19','dl20') else fmt(p)}")
    per_seed = []
    for s in seeds:
        v = [runs[(model, s)][d]["vals"][0] for d in BRIGHT if d in runs[(model, s)] and runs[(model, s)][d]["round"] == 3]
        if len(v) == 7: per_seed.append(st.mean(v))
    if len(per_seed) >= 2:
        pb = PAPER.get(model, {}).get("bright")
        print(f"  {'BRIGHT average':19s} n={len(per_seed)}  {st.mean(per_seed):4.1f}±{st.stdev(per_seed):3.1f} | paper {fmt(st.mean(pb)) if pb else '-'}")
