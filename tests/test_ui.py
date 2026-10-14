"""Unit and regression tests for the Manga Speaker UI data layer and components."""
import json
from pathlib import Path
import pytest


def test_test_predictions_exist_and_valid():
    p = Path("test_predictions_7b.jsonl")
    assert p.exists(), "test_predictions_7b.jsonl must exist"
    
    rows = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
                
    assert len(rows) == 15, f"Expected 15 test sequences, got {len(rows)}"
    for r in rows:
        assert "sequence_id" in r
        assert "pages" in r
        assert len(r["pages"]) == 3, f"Sequence {r['sequence_id']} must have 3 pages"
        for p_idx, page in enumerate(r["pages"]):
            assert isinstance(page, list)
            for item in page:
                assert "speaker" in item, f"Missing speaker in {r['sequence_id']} p{p_idx+1}"
                assert "text" in item, f"Missing text in {r['sequence_id']} p{p_idx+1}"
                assert len(item["text"].strip()) > 0, "Text must not be empty"


def test_development_labels_exist_and_valid():
    p = Path("dataset/development/labels.jsonl")
    assert p.exists(), "dataset/development/labels.jsonl must exist"
    
    rows = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
                
    assert len(rows) == 80, f"Expected 80 dev sequences, got {len(rows)}"


def test_sequences_metadata_exist():
    p = Path("dataset/sequences.json")
    assert p.exists(), "dataset/sequences.json must exist"
    with open(p, "r", encoding="utf-8") as f:
        seqs = json.load(f)
    assert len(seqs) == 95, f"Expected 95 total sequences (80 dev + 15 test), got {len(seqs)}"


if __name__ == "__main__":
    test_test_predictions_exist_and_valid()
    test_development_labels_exist_and_valid()
    test_sequences_metadata_exist()
    print("ALL UI DATA TESTS PASSED!")
