"""Dataset helpers. sequences.json layout is auto-detected (see MANGA_TASK_GUIDE.md, 'Assumptions')."""
import json
import random
from pathlib import Path

PATH_KEYS = ("pages", "images", "page_paths", "image_paths", "files")
FILE_KEYS = ("path", "file", "image", "filename", "image_path")


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def write_jsonl(p, rows):
    with open(p, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _find_sequences_file(root):
    root = Path(root)
    for c in (root / "sequences.json", root / "dataset" / "sequences.json"):
        if c.exists():
            return c
    hits = list(root.rglob("sequences.json"))
    if not hits:
        raise FileNotFoundError(f"sequences.json not found under {root}")
    return hits[0]


def _entry_pages(e):
    if isinstance(e, list):
        raw = e
    else:
        raw = next((e[k] for k in PATH_KEYS if k in e), None)
    if raw is None:
        raise ValueError(f"Cannot find page list in entry: {str(e)[:200]}")
    out = []
    for item in raw:
        if isinstance(item, dict):
            item = next(item[k] for k in FILE_KEYS if k in item)
        out.append(str(item))
    return out


def _resolve(root, seq_file, rel):
    root = Path(root)
    for base in (seq_file.parent, root, root / "development", root / "test", root / "dataset"):
        p = base / rel
        if p.exists():
            return str(p)
    name = Path(rel).name
    hits = list(root.rglob(name))
    if hits:
        return str(hits[0])
    raise FileNotFoundError(f"Image not found: {rel}")


def load_sequences(dataset_dir):
    """-> {sequence_id: [img1, img2, img3]} with resolved paths."""
    seq_file = _find_sequences_file(dataset_dir)
    obj = load_json(seq_file)
    if isinstance(obj, dict) and "sequences" in obj:
        obj = obj["sequences"]
    if isinstance(obj, dict):
        entries = list(obj.items())
    else:
        entries = [(e.get("sequence_id") or e.get("id"), e) for e in obj]
    return {sid: [_resolve(dataset_dir, seq_file, r) for r in _entry_pages(e)] for sid, e in entries}


def load_labels(path):
    return {r["sequence_id"]: r["pages"] for r in load_jsonl(path)}


def make_split(seq_ids, val_frac=0.2, seed=13):
    """Sequence-level split: the three pages of a sequence never get separated."""
    ids = sorted(seq_ids)
    random.Random(seed).shuffle(ids)
    n_val = max(1, round(len(ids) * val_frac))
    return {"train": sorted(ids[n_val:]), "val": sorted(ids[:n_val])}
