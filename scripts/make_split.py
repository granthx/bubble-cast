import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

"""Sequence-level train/val split of the 80 dev sequences (pages of one sequence stay together)."""
import argparse
import json

from mangaspeak.data import load_labels, make_split

ap = argparse.ArgumentParser()
ap.add_argument("--labels", default="dataset/development/labels.jsonl")
ap.add_argument("--val-frac", type=float, default=0.2)
ap.add_argument("--seed", type=int, default=13)
ap.add_argument("--out", default="splits.json")
a = ap.parse_args()

split = make_split(list(load_labels(a.labels)), a.val_frac, a.seed)
json.dump(split, open(a.out, "w"), indent=2)
print({k: len(v) for k, v in split.items()}, "->", a.out)
