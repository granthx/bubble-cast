"""
Export handlers for screenplay scripts, prediction JSONL, and sequence JSON.
"""
import json
from pathlib import Path
from typing import Any, Dict, List

from .data import CHARACTER_PROFILES, SERIES_TITLES, repo


def generate_screenplay_script(sequence_id: str, pages_dialogues: List[List[Dict[str, str]]]) -> str:
    series_title = SERIES_TITLES.get(sequence_id, "Manga Chapter")
    profiles = CHARACTER_PROFILES.get(sequence_id, {})

    lines = [
        f"TITLE: {series_title}",
        f"SEQUENCE ID: {sequence_id}",
        "=" * 60,
        "",
    ]

    for p_idx, page in enumerate(pages_dialogues):
        lines.append(f"--- PAGE {p_idx + 1} ---")
        if not page:
            lines.append("   [SILENT PAGE - NO SPOKEN DIALOGUE]")
        else:
            for b_idx, item in enumerate(page, 1):
                spk = item.get("speaker", "char1")
                profile = profiles.get(spk)
                spk_name = profile[0] if profile else spk.upper()
                txt = item.get("text", "")
                lines.append(f"{b_idx:02d}. {spk_name} ({spk}): \"{txt}\"")
        lines.append("")

    return "\n".join(lines)


def get_sequence_json_string(sequence_id: str, source: str = "test") -> str:
    data_source = repo.test_predictions if source == "test" else repo.dev_labels
    pages = data_source.get(sequence_id, [[], [], []])
    obj = {
        "sequence_id": sequence_id,
        "pages": pages,
    }
    return json.dumps(obj, indent=2, ensure_ascii=False)
