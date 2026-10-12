"""Deterministic post-processing 'harness' rules (tune these on the dev split)."""
import re

NARRATION = "NARRATION"
SFX_SPEAKERS = {"sfx", "sound", "soundeffect", "sound_effect", "ignore", "none", "null", "watermark", "credit"}
JUNK_TEXT = re.compile(
    r"(https?://|www\.|\\.com\\b|\\.net\\b|scanlat|translated by|translation:|typeset|cleaned by|"
    r"redraw|raw by|join our|discord|read (more )?at|chapter\\s*\\d+\\s*$)", re.I)


CJK_SFX = {
    # Japanese common manga sound effects
    "ドッ", "バァン", "ゴゴゴ", "ドン", "ザー", "キャー", "ハァ", "フッ", "クッ", "ドキドキ", "シーン",
    # Korean common webtoon sound effects
    "콰쾅", "쿠구구", "퍽", "쿵", "헉", "앗", "하아", "쳇", "두근두근", "쿵쾅",
    # Chinese common manhua sound effects
    "轰", "啪", "呼", "咚", "哈", "啊", "哼", "嘭", "咔嚓"
}


def norm_speaker(s):
    s = str(s or "").strip()
    if s.lower() in ("narration", "narrator", "narration box", "caption"):
        return NARRATION
    cleaned = re.sub(r"[^a-z0-9_]+", "", s.lower().replace(" ", "_"))
    m = re.fullmatch(r"(?:char|character)_?(\d+)", cleaned)
    if m:
        return f"char{m.group(1)}"
    return cleaned or "char0"


def norm_text(t):
    t = str(t or "").replace("\u2019", "'").replace("\u2018", "'")
    t = re.sub(r"-\s*\n\s*", "-", t)           # hyphenated print wrap
    t = re.sub(r"\s+", " ", t).strip()
    return t


def clean_lines(lines):
    out = []
    for l in lines:
        if not isinstance(l, dict):
            continue
        spk, txt = norm_speaker(l.get("speaker")), norm_text(l.get("text"))
        if not txt or spk in SFX_SPEAKERS or txt in CJK_SFX:
            continue
        if re.fullmatch(r"[-–—\s]*\d{1,4}[-–—\s]*", txt):  # bare page number
            continue
        if JUNK_TEXT.search(txt):
            continue
        if out and out[-1] == {"speaker": spk, "text": txt} and len(txt) > 3:  # model stutter loop
            continue
        out.append({"speaker": spk, "text": txt})
    return out


def parse_lines(obj):
    """Accepts {"lines":[...]} or a bare list. Returns list or None if unusable."""
    if isinstance(obj, dict):
        obj = obj.get("lines", obj.get("pages"))
    if not isinstance(obj, list):
        return None
    return [l for l in obj if isinstance(l, dict) and "text" in l]


def apply_merge(pages, merge):
    """Validate + apply {later_label: earlier_label}; ignores unknown labels, NARRATION and cycles."""
    labels = {l["speaker"] for p in pages for l in p}
    mapping = {}
    for src, dst in (merge or {}).items():
        src, dst = norm_speaker(src), norm_speaker(dst)
        if src in labels and dst in labels and src != dst and NARRATION not in (src, dst):
            mapping[src] = dst

    def root(x, seen=()):
        return x if x not in mapping or x in seen else root(mapping[x], seen + (x,))

    return [[{"speaker": root(l["speaker"]), "text": l["text"]} for l in p] for p in pages]


NARRATION_CUES = re.compile(
    r'\b(her mother|his mother|their mother|at that time|meanwhile|in the end|it was|she had|he had|they were|'
    r'joined the|among the|was enacted|or so i hear|with the support|it seems that|years ago|later that|the following|'
    r'suddenly|at the same time|at this moment|as expected|once upon a time|days later|hours later|the next day|'
    r'that night|the following day|at this point|some time later|moments later|flashback)\b',
    re.IGNORECASE
)

# Patterns that strongly indicate a speaker change (question asked → answer follows)
QA_ENDINGS = re.compile(r"[?？]\s*$")
INTERJECTIONS = {"hm?", "huh?", "what?", "yeah.", "no.", "right?", "really?", "wait.", "stop.",
                 "what!?", "yeah!", "eh?", "oh?", "oh!", "ah.", "ah!", "yes.", "no!", "huh!"}


def _text_key(txt: str) -> str:
    """Normalise text for dedup comparison (supports English, Japanese, Chinese, Korean)."""
    return re.sub(r"[^\w\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]+", "", txt.lower()).strip()



def remove_context_leak(current_lines, prev_pages):
    """
    Drop any line in current_lines whose normalised text already appeared in ANY
    previous page. This is a full set-diff (not just prefix) so re-ordered leaks
    are also caught.
    """
    if not prev_pages or not current_lines:
        return current_lines

    prev_keys = {_text_key(l["text"]) for pg in prev_pages for l in pg if l["text"]}
    out = []
    for line in current_lines:
        key = _text_key(line["text"])
        # Allow short lines (≤4 words) through — they could be new exclamations
        if key and len(key.split()) > 4 and key in prev_keys:
            continue
        out.append(line)
    return out


def refine_sequence(pages):
    """
    Post-processing pass applied after all 3 pages are collected:
    1. Strip lines repeated from earlier pages (full set-diff dedup).
    2. Fix speaker labels: NARRATION detection, and char1/char2 alternation
       based on Q→A patterns and positional heuristics.
    """
    # ── Step 1: dedup across pages ──────────────────────────────────────────
    cleaned_pages = []
    for page in pages:
        deduped = remove_context_leak(page, cleaned_pages)
        cleaned_pages.append(deduped)

    # ── Step 2: speaker refinement ───────────────────────────────────────────
    out_pages = []
    # Track which char labels have been seen so we can toggle meaningfully
    cur_speaker = "char1"
    alt_speaker = "char2"

    for page in cleaned_pages:
        new_page = []
        for idx, line in enumerate(page):
            spk = line.get("speaker", "char1")
            txt = line.get("text", "")

            # --- NARRATION detection ---
            if NARRATION_CUES.search(txt) and len(txt) > 20:
                spk = NARRATION

            # --- Speaker normalisation ---
            elif spk in ("char0", "UNKNOWN", "unknown"):
                spk = cur_speaker

            elif spk == "char1":
                # If previous non-NARRATION line ended with a question and this
                # looks like a short reply → toggle to alternate speaker
                if idx > 0:
                    prev = new_page[-1]
                    if (prev["speaker"] not in (NARRATION,)
                            and (QA_ENDINGS.search(prev["text"])
                                 or prev["text"].strip().lower() in INTERJECTIONS)
                            and len(txt.split()) <= 12):
                        spk = alt_speaker
                        cur_speaker = alt_speaker
                        alt_speaker = "char1" if alt_speaker == "char2" else "char2"
                    else:
                        cur_speaker = "char1"

            # Track the running speaker for unlabelled lines
            if spk not in (NARRATION, "char0", "UNKNOWN"):
                cur_speaker = spk

            new_page.append({"speaker": spk, "text": txt})
        out_pages.append(new_page)

    return out_pages
