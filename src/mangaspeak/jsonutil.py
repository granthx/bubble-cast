import json
import re


def extract_json(text):
    """Pull the first JSON object out of model output (handles ``` fences, chatter, trailing commas)."""
    if not text:
        return None
    text = re.sub(r"```(?:json)?", "", text)
    start = text.find("{")
    if start < 0:
        return None
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return _loads(text[start:i + 1])
    # truncated output: try to close it
    return _loads(text[start:] + '"}]}')


def _loads(s):
    for cand in (s, re.sub(r",\s*([}\]])", r"\1", s)):
        try:
            return json.loads(cand)
        except Exception:
            continue
    return None
