# Implementation Plan: Multilingual Manga Reader & Speaker ID (EN / JA / ZH / KO)

## 1. Executive Summary & Feasibility

### Is this a good idea?
**Yes, exceptionally good.** In fact, our underlying base model—**Qwen2.5-VL-3B-Instruct** (developed by Alibaba)—is one of the world's strongest open-weight vision-language models for CJK (Chinese, Japanese, Korean) text recognition and document understanding.

### Supported Comic Traditions:
1. **Japanese Manga (日本語)**: Traditional Right-to-Left (RTL), vertical text columns (*tategaki*), furigana annotations.
2. **Korean Manhwa & Webtoons (한국어)**: Left-to-Right (LTR), vertical webtoon scroll structures, sound effect Hangul clusters.
3. **Chinese Manhua (中文)**: Simplified/Traditional Chinese, modern horizontal or classic vertical layout.
4. **English / Localized Comics**: Left-to-Right (LTR), standard horizontal balloon dialogues.

---

## 2. Core Technical Challenges & Solutions

| Challenge | Language | Solution |
| :--- | :--- | :--- |
| **Reading Order** | JA (RTL) vs. KO/EN (LTR) vs. Webtoons (Top-to-Bottom) | Dynamic Prompt Injection: Explicitly instruct reading direction based on selected comic type (`manga` = RTL, `webtoon/manhwa` = vertical top-to-bottom, `manhua/en` = standard). |
| **Furigana & Small Ruby Text** | Japanese | Add regex/prompt filter to ignore tiny pronunciation glosses (ruby) so dialogue doesn't duplicate words. |
| **Hangul Webtoon SFX** | Korean | Korean webtoons use heavy stylized SFX (*kugugugu*, *teok*). Expand `clean.py` filter rules for common Hangul onomatopoeia. |
| **Cross-Lingual Translation** | All 4 Languages | Allow two output modes: **Native Transcription** (original language) and **Dual Mode** (original text + English translation side-by-side). |

---

## 3. Architecture & Data Flow

```
[User Uploads Manga Pages (JPG/PNG/ZIP)]
                   │
                   ▼
     [Language & Format Selector]
   (Auto-Detect | EN | JA | ZH | KO)
                   │
                   ▼
     [Language-Aware Prompt Builder]
  (Injects reading order & CJK balloon rules)
                   │
                   ▼
      [Qwen2.5-VL + LoRA Adapter]
  (Visual Character Memory + Text Extraction)
                   │
                   ▼
     [Multilingual Normalizer (clean.py)]
   (Filters SFX in EN/JA/ZH/KO, normalizes char1/char2)
                   │
                   ▼
       [Interactive UI in app.py]
  - Visual Side-by-Side Page & Speech Balloons
  - Character Color Badges (char1, char2, NARRATION)
  - Optional: Translation Toggle & TTS (Text-to-Speech)
```

---

## 4. Extended Output Schema

To support multilingual manga while preserving compatibility with the existing evaluation pipeline:

```json
{
  "sequence_id": "custom_upload_01",
  "language": "ja",
  "reading_order": "right_to_left",
  "pages": [
    [
      {
        "speaker": "char1",
        "text": "何をしているんだ、お前は？！",
        "translation": "What are you doing?!",
        "box": [120, 450, 230, 580]
      },
      {
        "speaker": "NARRATION",
        "text": "その日、世界は静かに崩壊を始めた。",
        "translation": "On that day, the world began to quietly crumble.",
        "box": [50, 50, 150, 300]
      }
    ]
  ]
}
```

---

## 5. Step-by-Step Implementation Roadmap

### Phase 1: Language-Aware Prompt Templates (`src/mangaspeak/prompts.py`)
- Add a `language: Literal["en", "ja", "zh", "ko", "auto"]` parameter to `build_page_messages()`.
- Inject language-specific layout cues:
  - **`ja`**: *"Read right-to-left, top-to-bottom. Distinguish vertical text from horizontal balloons. Ignore furigana and sound effects (katakana/hiragana SFX)."*
  - **`ko`**: *"Read top-to-bottom webtoon flow. Ignore Hangul sound-effect bursts. Tag speaker identities consistently."*
  - **`zh`**: *"Read standard Chinese text panels. Support both Simplified and Traditional characters."*
  - **`en`**: Current production prompt.

### Phase 2: Multilingual Cleaner Rules (`src/mangaspeak/clean.py`)
- Add unicode block regexes for CJK characters:
  - Hiragana / Katakana (`\u3040-\u30ff`)
  - Hangul (`\uac00-\ud7af`)
  - CJK Unified Ideographs (`\u4e00-\u9fff`)
- Extend the SFX blacklist to cover common Japanese onomatopoeia (`ドッ`, `バァン`, `ゴゴゴ`, `ドン`), Korean SFX (`콰쾅`, `쿠구구`, `퍽`), and Chinese SFX (`轰`, `啪`).

### Phase 3: Interactive Upload Tab in `app.py`
Add a dedicated **"Upload & Read Any Manga"** tab to the Streamlit app:
1. **File Uploader:** Drag and drop 1 to 5 images (or a `.zip` archive).
2. **Language Controls:** Radio buttons for `English`, `Japanese (日本語)`, `Chinese (中文)`, `Korean (한국어)`, or `Auto-Detect`.
3. **Translation Toggle:** Checkbox to generate instant English translations alongside original dialogue.
4. **Live Execution:** Runs the loaded Qwen2.5-VL model with carry-forward visual memory.
5. **Interactive Viewer:** Display rendered pages with speaker avatars and dialogue cards matching our dark manga UI theme.

### Phase 4: Optional Speech Synthesis (TTS)
- Connect dialogues to edge TTS or browser speech synthesis so users can click a speaker card to "listen" to the character's line in their native language or English!

---

## 6. Execution Priority

Given the immediate **8-hour deadline for your 3 tasks**:
1. **Right Now**: Let the current model training finish (Epoch 1 or 2) and submit your 3 primary task deliverables (`test_predictions_v2.jsonl`, `scores_v2.json`, reports).
2. **Post-Submission**: Follow Phases 1–3 above to turn this into a flagship portfolio project with live CJK webtoon reading.
