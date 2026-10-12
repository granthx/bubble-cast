"""Offline smoke test with a fake VLM (no GPU, no model download). Run: python tests/test_offline.py"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from PIL import Image

from mangaspeak.clean import apply_merge, clean_lines
from mangaspeak.config import load_config
from mangaspeak.data import load_sequences, make_split
from mangaspeak.graph import build_graph, run_sequence
from mangaspeak.jsonutil import extract_json


class FakeVLM:
    def __init__(self):
        self.calls = 0

    def generate(self, messages, max_new_tokens=0, temperature=0.0):
        self.calls += 1
        text = json.dumps(messages)
        if "continuity checker" in text:
            return '```json\n{"merge":{"char3":"char1"}}\n```'
        if "page 1 of 3" in text.lower():
            return '{"lines":[{"speaker":"char1","text":"Where are\\nyou going?"},{"speaker":"SFX","text":"BOOM"},{"speaker":"char2","text":"Home."}]}'
        if "page 2 of 3" in text.lower():
            return 'Sure! {"lines":[{"speaker":"char3","text":"Wait for me!"},{"speaker":"narrator","text":"42"},]}'
        return "garbage"  # page 3: unparsable -> must degrade to empty page


def main():
    assert extract_json('x ```json {"a":[1,2,]} ```') == {"a": [1, 2]}
    assert clean_lines([{"speaker": "Narrator", "text": "Hi  there"}]) == [{"speaker": "NARRATION", "text": "Hi there"}]
    assert apply_merge([[{"speaker": "char1", "text": "a"}], [{"speaker": "char3", "text": "b"}]],
                       {"char3": "char1", "char1": "char3"})[1][0]["speaker"] in ("char1", "char3")
    sp = make_split([f"s{i}" for i in range(80)])
    assert len(sp["train"]) + len(sp["val"]) == 80 and not set(sp["train"]) & set(sp["val"])

    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        for i in range(3):
            Image.new("RGB", (64, 96), "white").save(d / f"p{i}.png")
        json.dump([{"sequence_id": "seq_x", "pages": [f"p{i}.png" for i in range(3)]}], open(d / "sequences.json", "w"))
        seqs = load_sequences(d)
        cfg = load_config(None, ["pipeline.reconcile=true"])
        app = build_graph(FakeVLM(), cfg)
        res, log = run_sequence(app, "seq_x", seqs["seq_x"])
        print(json.dumps(res, indent=1), log)
        p = res["pages"]
        assert p[0] == [{"speaker": "char1", "text": "Where are you going?"}, {"speaker": "char2", "text": "Home."}]
        assert p[1] == [{"speaker": "char1", "text": "Wait for me!"}]  # char3 merged into char1; '42' dropped
        assert p[2] == []
    print("ALL OK")


if __name__ == "__main__":
    main()
