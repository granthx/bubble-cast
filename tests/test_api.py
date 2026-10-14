"""
Automated tests for Manga Speaker FastAPI backend.
Run: python tests/test_api.py
"""
import io
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "ok"
    assert data["test_sequences"] == 15
    assert data["dev_sequences"] == 80
    print("PASS: test_health")


def test_sources():
    resp = client.get("/api/sources")
    assert resp.status_code == 200, resp.text
    sources = resp.json()
    assert len(sources) == 2
    assert sources[0]["id"] == "test"
    assert sources[1]["id"] == "dev"
    print("PASS: test_sources")


def test_sequences():
    resp = client.get("/api/sequences?source=test")
    assert resp.status_code == 200, resp.text
    seqs = resp.json()
    assert len(seqs) == 15
    first = seqs[0]
    assert "sequence_id" in first
    assert "title" in first
    assert "total_lines" in first
    assert "speakers" in first

    resp_dev = client.get("/api/sequences?source=dev")
    assert resp_dev.status_code == 200
    assert len(resp_dev.json()) == 80
    print("PASS: test_sequences (test & dev)")


def test_sequence_detail():
    seq_id = "seq_81b1782990ab7950"
    resp = client.get(f"/api/sequences/{seq_id}?source=test")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["sequence_id"] == seq_id
    assert "Tokyo Ghoul:re" in data["title"]
    assert len(data["pages"]) == 3
    assert len(data["characters"]) > 0

    # Check dialogue structure
    p1 = data["pages"][0]
    assert "page_number" in p1
    assert "dialogues" in p1
    if p1["dialogues"]:
        d1 = p1["dialogues"][0]
        assert "order_index" in d1
        assert "speaker" in d1
        assert "text" in d1
        assert "color" in d1
    print("PASS: test_sequence_detail")


def test_multilingual():
    resp = client.get("/api/multilingual")
    assert resp.status_code == 200, resp.text
    traditions = resp.json()
    assert len(traditions) == 4
    ids = [t["id"] for t in traditions]
    assert "japanese_manga" in ids
    assert "korean_manhwa" in ids
    assert "chinese_manhua" in ids
    assert "english_comics" in ids
    print("PASS: test_multilingual")


def test_exports():
    # 1. Predictions
    r_pred = client.get("/api/exports/predictions")
    assert r_pred.status_code == 200
    assert "seq_" in r_pred.text

    # 2. README
    r_rm = client.get("/api/exports/readme")
    assert r_rm.status_code == 200
    assert len(r_rm.text) > 100

    # 3. Sequence JSON
    seq_id = "seq_81b1782990ab7950"
    r_json = client.get(f"/api/exports/sequence/{seq_id}/json?source=test")
    assert r_json.status_code == 200
    assert seq_id in r_json.json()["sequence_id"]

    # 4. Sequence Screenplay script
    r_script = client.get(f"/api/exports/sequence/{seq_id}/script?source=test")
    assert r_script.status_code == 200
    assert "TITLE:" in r_script.text
    assert "PAGE 1" in r_script.text
    print("PASS: test_exports")


def test_analyze_upload():
    # Create 2 small test image buffers
    buf1 = io.BytesIO()
    Image.new("RGB", (64, 64), color="white").save(buf1, format="PNG")
    buf1.seek(0)

    buf2 = io.BytesIO()
    Image.new("RGB", (64, 64), color="black").save(buf2, format="PNG")
    buf2.seek(0)

    files = [
        ("files", ("page1.png", buf1.getvalue(), "image/png")),
        ("files", ("page2.png", buf2.getvalue(), "image/png")),
    ]
    data = {
        "reading_flow": "Japanese Manga (Right-to-Left)",
        "language_mode": "Auto-Detect",
    }
    resp = client.post("/api/analyze", files=files, data=data)
    assert resp.status_code == 200, resp.text
    res_data = resp.json()
    assert res_data["sequence_id"] == "uploaded_seq"
    assert res_data["page_count"] == 2
    assert "pages" in res_data
    print("PASS: test_analyze_upload")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Manga Speaker API Tests...")
    print("=" * 60)
    test_health()
    test_sources()
    test_sequences()
    test_sequence_detail()
    test_multilingual()
    test_exports()
    test_analyze_upload()
    print("=" * 60)
    print("ALL BACKEND API TESTS PASSED!")
    print("=" * 60)
