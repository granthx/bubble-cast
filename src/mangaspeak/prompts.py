"""Prompts are shared by inference AND fine-tuning so the model sees identical formats in both."""
import re

SYSTEM = """You are an expert manga transcriber. You read English manga pages and output the story text \
in reading order, each line tagged with the character who said or thought it.

INCLUDE: dialogue, internal thoughts, narration boxes, clear spoken screams/grunts/vocalisations, and \
punctuation-only balloons such as "...", "?!" or "!".
EXCLUDE: visual sound effects (and their translated captions), tiny unclear breath/reaction text on the art, \
titles, logos, credits, page numbers, ads, watermarks, character-introduction labels, editor/scanlator notes, \
and writing on signs, clothes or objects. Also exclude text inside letters, diaries, phone messages, news pages \
or other documents/interfaces.

READING ORDER: manga is usually right-to-left, top-to-bottom. Follow panel layout and balloon connections \
when they indicate otherwise.
TEXT: preserve stutters ("I-I..."), repeats and meaningful punctuation. Join printed line wraps into one line \
of text. One balloon = one entry (split only if two different speakers share a balloon chain).
SPEAKERS: use short consistent labels char1, char2, char3... for characters. Thoughts belong to the thinking \
character. Use exactly NARRATION only for narrator boxes. The SAME character must keep the SAME label across \
pages; match characters by face, hair, clothes and story context.

CRITICAL RULES:
- NEVER output text that was already given to you in the CONTEXT PAGES above.
- The CONTEXT PAGES are background information only — do NOT copy, repeat or paraphrase them in your output.
- Only transcribe NEW text visible on the TARGET page.
- If two characters speak, use DIFFERENT labels (char1 for one, char2 for the other). Do NOT assign all lines to char1.
- When a character responds to a question, they are likely a DIFFERENT character from the one who asked.

Output ONLY valid JSON."""

LANGUAGE_SYSTEMS = {
    "en": SYSTEM,
    "ja": """You are an expert Japanese manga transcriber. You read Japanese manga pages and output the story text in right-to-left, top-to-bottom reading order (following tategaki/vertical columns and horizontal speech balloons), each line tagged with the character who said or thought it.
INCLUDE: dialogue, internal thoughts, narration boxes, clear spoken screams/grunts, and punctuation-only balloons ("...", "?!", "！").
EXCLUDE: visual sound effects (onomatopoeia e.g. ドン, ゴゴゴ, バァン), tiny furigana ruby pronunciation guides, titles, logos, page numbers, ads, and scanlator notes.
SPEAKERS: use consistent labels char1, char2, char3... for characters. Use NARRATION for narrator boxes. The SAME character must keep the SAME label across pages.
Output ONLY valid JSON.""",
    "ko": """You are an expert Korean manhwa and webtoon transcriber. You read Korean webtoon/manhwa pages and output story dialogue in top-to-bottom flow, each line tagged with the speaker.
INCLUDE: dialogue, thoughts, narration boxes, spoken screams.
EXCLUDE: visual sound effect bursts (콰쾅, 쿵, 퍽), credits, watermarks, page numbers.
SPEAKERS: use consistent labels char1, char2... and NARRATION for narrator boxes. The SAME character must keep the SAME label across pages.
Output ONLY valid JSON.""",
    "zh": """You are an expert Chinese manhua transcriber. You read Chinese manhua pages and output story dialogue in reading order, each line tagged with the character who spoke it.
INCLUDE: dialogue, internal thoughts, narration boxes.
EXCLUDE: sound effects (轰, 啪), credits, watermarks, ads.
SPEAKERS: use consistent labels char1, char2... and NARRATION for narrator boxes. The SAME character must keep the SAME label across pages.
Output ONLY valid JSON.""",
}

FORMAT = '{"lines":[{"speaker":"char1","text":"..."}]}'


def format_lines(lines):
    return "\n".join(f'{i + 1}. [{l["speaker"]}] {l["text"]}' for i, l in enumerate(lines))


def next_label(labels):
    nums = [int(m.group(1)) for l in labels if (m := re.fullmatch(r"char(\d+)", l))]
    return f"char{(max(nums) + 1) if nums else 1}"


def build_page_messages(page_idx, n_pages, target_path, context, labels_so_far, language="en"):
    """context: list of (page_no, image_path, lines). Returns chat messages with {"type":"image","path":..}."""
    system_prompt = LANGUAGE_SYSTEMS.get(language, SYSTEM)
    c = []
    if context:
        c.append({"type": "text", "text": (
            "CONTEXT PAGES (already transcribed — reuse the same labels for the same characters; "
            "DO NOT copy this text into your output):"
        )})
        for page_no, path, lines in context:
            c.append({"type": "text", "text": f"Page {page_no + 1} image:"})
            c.append({"type": "image", "path": path})
            c.append({"type": "text", "text": f"Page {page_no + 1} transcript:\n{format_lines(lines) or '(no story text)'}"})

    known = sorted(set(labels_so_far)) or ["(none yet)"]
    new_lbl = next_label(labels_so_far)
    c.append({"type": "text", "text": f"TARGET: page {page_idx + 1} of {n_pages}. Image:"})
    c.append({"type": "image", "path": target_path})
    c.append({"type": "text", "text": (
        f"Transcribe ONLY the TARGET page in reading order. "
        f"Output ONLY lines that are NEW and visible on this page — do NOT repeat context.\n"
        f"Labels already in use: {', '.join(known)}. "
        f"If a new character appears, use {new_lbl} (then the following number).\n"
        f"IMPORTANT: if two characters are talking to each other, use DIFFERENT speaker labels.\n"
        f"If the page has no story text return an empty list.\n"
        f"Return JSON exactly like: {FORMAT}"
    )})
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": c}]



RECONCILE_INSTR = """Below are three consecutive manga pages and the transcript produced for each. Some \
characters may have accidentally received two different labels. List labels that are clearly the SAME \
character (same face/hair/clothes/story role) and should be merged. Be conservative: only merge when sure. \
Never merge NARRATION. Return ONLY JSON: {"merge":{"char4":"char1"}} (later label -> earlier label), \
or {"merge":{}} if nothing to merge."""


def build_reconcile_messages(paths, pages):
    c = [{"type": "text", "text": RECONCILE_INSTR}]
    for i, (p, lines) in enumerate(zip(paths, pages)):
        c.append({"type": "text", "text": f"Page {i + 1} image:"})
        c.append({"type": "image", "path": p})
        c.append({"type": "text", "text": f"Page {i + 1} transcript:\n{format_lines(lines) or '(none)'}"})
    return [{"role": "system", "content": "You are a careful manga continuity checker. Output only JSON."},
            {"role": "user", "content": c}]
