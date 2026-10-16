"""Optional OCR cross-check agent: drops VLM lines that have no support in an independent OCR pass."""
import re

_reader = None


def _fuzzy(a, b):
    try:
        from rapidfuzz import fuzz
        return fuzz.partial_ratio(a, b)
    except ImportError:
        import difflib
        if not a or not b:
            return 0
        m = difflib.SequenceMatcher(None, a, b).find_longest_match(0, len(a), 0, len(b))
        return 100 * m.size / len(a)


def _alnum(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def ocr_blob(image_path):
    global _reader
    import easyocr
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=True, verbose=False)
    return _alnum(" ".join(_reader.readtext(image_path, detail=0, paragraph=False)))


def filter_by_ocr(lines, image_path, threshold, blob_fn=ocr_blob):
    try:
        blob = blob_fn(image_path)
    except Exception as e:  # OCR missing/failing must never break the pipeline
        print(f"[verify] OCR unavailable ({e}); skipping")
        return lines
    kept = []
    for l in lines:
        t = _alnum(l["text"])
        if len(t) < 3 or _fuzzy(t, blob) >= threshold:  # punctuation-only / tiny lines can't be verified
            kept.append(l)
    return kept
