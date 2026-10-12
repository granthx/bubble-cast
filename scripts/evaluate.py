import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

"""Score predictions with the official scorer; optionally restrict references to the validation split."""
import argparse
import json
import subprocess
import tempfile

from mangaspeak.data import load_json, load_jsonl, write_jsonl

ap = argparse.ArgumentParser()
ap.add_argument("--predictions", required=True)
ap.add_argument("--references", default="dataset/development/labels.jsonl")
ap.add_argument("--scorer", default="dataset/score.py")
ap.add_argument("--ids-from", default=None, help="splits.json to restrict references")
ap.add_argument("--split", default="val")
ap.add_argument("--output", default="scores.json")
a = ap.parse_args()

refs = a.references
if a.ids_from:
    keep = set(load_json(a.ids_from)[a.split])
    tmp = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    tmp.close()
    write_jsonl(tmp.name, [r for r in load_jsonl(a.references) if r["sequence_id"] in keep])
    refs = tmp.name

subprocess.run(["python", a.scorer, "--references", refs, "--predictions", a.predictions,
                "--output", a.output], check=True)
s = json.load(open(a.output))
print(json.dumps(s, indent=2)[:2000])
