import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

"""Run the LangGraph pipeline and write a submission-format JSONL.

Dev subset : --ids-from splits.json --split val   (write to val_predictions.jsonl, then evaluate.py)
Test       : --ids-from dataset/sample_submission.jsonl
"""
import argparse
import json
import os
import time

from mangaspeak.config import load_config
from mangaspeak.data import load_json, load_jsonl, load_sequences, write_jsonl
from mangaspeak.graph import build_graph, run_sequence
from mangaspeak.vlm import build_vlm

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="dataset")
ap.add_argument("--ids-from", required=True, help="sample_submission.jsonl | labels.jsonl | splits.json")
ap.add_argument("--split", default="val", help="key inside splits.json")
ap.add_argument("--out", default="predictions.jsonl")
ap.add_argument("--config", default="configs/default.yaml")
ap.add_argument("--adapter", default=None, help="LoRA adapter dir (overrides config)")
ap.add_argument("--set", nargs="*", default=[], help="config overrides e.g. pipeline.reconcile=true")
a = ap.parse_args()

cfg = load_config(a.config, a.set + ([f"model.adapter={a.adapter}"] if a.adapter else []))

if a.ids_from.endswith(".jsonl"):
    ids = [r["sequence_id"] for r in load_jsonl(a.ids_from)]
else:
    ids = load_json(a.ids_from)[a.split]

seqs = load_sequences(a.dataset)
done = {}
if os.path.exists(a.out):  # resume
    done = {r["sequence_id"]: r for r in load_jsonl(a.out)}

vlm = build_vlm(cfg)
app = build_graph(vlm, cfg)
rows = []
for n, sid in enumerate(ids, 1):
    if sid in done:
        rows.append(done[sid])
        continue
    t0 = time.time()
    try:
        res, log = run_sequence(app, sid, seqs[sid])
    except Exception as e:  # never lose the whole run to one bad sequence
        print(f"[{sid}] FAILED: {e}")
        res, log = {"sequence_id": sid, "pages": [[] for _ in seqs[sid]]}, [str(e)]
    rows.append(res)
    write_jsonl(a.out, rows)  # checkpoint every sequence
    print(f"[{n}/{len(ids)}] {sid} {time.time() - t0:.0f}s lines={[len(p) for p in res['pages']]} {log if log else ''}")

write_jsonl(a.out, rows)
print("wrote", a.out)
