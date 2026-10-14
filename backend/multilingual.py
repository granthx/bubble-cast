"""
Multilingual Comic Studio data and metadata for 4 global comic traditions.
"""
from typing import Any, Dict, List

MULTILINGUAL_TRADITIONS: List[Dict[str, Any]] = [
    {
        "id": "japanese_manga",
        "title": "Japanese Manga (日本語)",
        "flag": "🇯🇵",
        "reading_flow": "Right-to-Left (RTL) Panels · Vertical Text (縦書き)",
        "language": "Japanese (日本語)",
        "font_family": "'Noto Sans JP', sans-serif",
        "description": "Traditional right-to-left panel flow with vertical speech column orientation, furigana annotations, and character identity continuity across sequential pages.",
        "pages": [
            {
                "page_number": 1,
                "dialogues": [
                    {"speaker": "NARRATION", "speaker_name": "Narration", "text": "その日、星々が静かに空を覆い尽くした。", "trans": "On that day, stars silently blanketed the night sky."},
                    {"speaker": "char1", "speaker_name": "Protagonist", "text": "何をしているんだ、お前は？！", "trans": "What in the world are you doing?!"},
                    {"speaker": "char2", "speaker_name": "Companion", "text": "待て！あいつが来るぞ...", "trans": "Wait! That monster is approaching..."},
                ],
            },
            {
                "page_number": 2,
                "dialogues": [
                    {"speaker": "char1", "speaker_name": "Protagonist", "text": "逃げる気はない！", "trans": "I have no intention of running away!"},
                    {"speaker": "char2", "speaker_name": "Companion", "text": "無茶をするな、まだ間に合う！", "trans": "Don't be reckless, there's still time to retreat!"},
                ],
            },
            {
                "page_number": 3,
                "dialogues": [
                    {"speaker": "char3", "speaker_name": "Rival", "text": "ふっ... ここまで辿り着いたか。", "trans": "Heh... so you managed to reach this inner chamber."},
                    {"speaker": "NARRATION", "speaker_name": "Narration", "text": "運命の歯車が狂い始める。", "trans": "The gears of destiny begin their fateful turn."},
                ],
            },
        ],
    },
    {
        "id": "korean_manhwa",
        "title": "Korean Manhwa & Webtoons (한국어)",
        "flag": "🇰🇷",
        "reading_flow": "Top-to-Bottom Vertical Scroll · Clean Speech Bubbles",
        "language": "Korean (한국어)",
        "font_family": "'Noto Sans KR', sans-serif",
        "description": "Continuous vertical scrolling format optimized for digital and mobile viewports, full-color panels, and expressive stylized Korean typography.",
        "pages": [
            {
                "page_number": 1,
                "dialogues": [
                    {"speaker": "NARRATION", "speaker_name": "Narration", "text": "모든 것이 무너지기 시작했던 그 날 아침.", "trans": "That cold morning when everything began to crumble."},
                    {"speaker": "char1", "speaker_name": "Hero", "text": "진짜로 가버린 거야...?", "trans": "Did you really just abandon us...?"},
                ],
            },
            {
                "page_number": 2,
                "dialogues": [
                    {"speaker": "char2", "speaker_name": "Departing Friend", "text": "더 이상 뒤를 돌아보지 마.", "trans": "Do not look back any longer."},
                    {"speaker": "char1", "speaker_name": "Hero", "text": "하지만 약속했잖아! 함께 있겠다고!", "trans": "But you promised! You promised we would stand together!"},
                ],
            },
            {
                "page_number": 3,
                "dialogues": [
                    {"speaker": "char2", "speaker_name": "Departing Friend", "text": "미안해. 이것이 내 마지막 선택이야.", "trans": "I'm sorry. This is my final choice."},
                    {"speaker": "NARRATION", "speaker_name": "Narration", "text": "그리고 문이 닫혔다.", "trans": "And behind him, the heavy iron door closed."},
                ],
            },
        ],
    },
    {
        "id": "chinese_manhua",
        "title": "Chinese Manhua (中文)",
        "flag": "🇨🇳",
        "reading_flow": "Modern Left-to-Right Narrative Panels · Dynamic Action",
        "language": "Chinese (中文)",
        "font_family": "'Noto Sans SC', sans-serif",
        "description": "Dynamic martial arts and fantasy (Xianxia/Wuxia) panel compositions with vibrant color palettes and modern horizontal reading order.",
        "pages": [
            {
                "page_number": 1,
                "dialogues": [
                    {"speaker": "NARRATION", "speaker_name": "Narration", "text": "三百年后，天剑重现世间。", "trans": "Three hundred years later, the Heavenly Sword reappeared in the realm."},
                    {"speaker": "char1", "speaker_name": "Swordsman", "text": "这股剑意... 绝非寻常修士所能拥有！", "trans": "This sword intent... is definitely beyond any ordinary cultivator!"},
                ],
            },
            {
                "page_number": 2,
                "dialogues": [
                    {"speaker": "char2", "speaker_name": "Opponent", "text": "阁下究竟是何方神圣？", "trans": "Who on earth is your honorable self?"},
                    {"speaker": "char1", "speaker_name": "Swordsman", "text": "你还不配知道我的名字。", "trans": "You are not yet worthy of knowing my true name."},
                ],
            },
            {
                "page_number": 3,
                "dialogues": [
                    {"speaker": "char2", "speaker_name": "Opponent", "text": "好狂妄的口气！接招！", "trans": "What arrogant words! Take this blow!"},
                    {"speaker": "NARRATION", "speaker_name": "Narration", "text": "风云突变，山河变色。", "trans": "The winds surged as mountains and rivers changed color."},
                ],
            },
        ],
    },
    {
        "id": "english_comics",
        "title": "English / Localized Comics",
        "flag": "🇺🇸",
        "reading_flow": "Standard Left-to-Right Reading Order (LTR)",
        "language": "English",
        "font_family": "'Plus Jakarta Sans', sans-serif",
        "description": "Western comic layout with left-to-right reading order, uppercase hand-lettered speech balloon conventions, and contextual sound effects.",
        "pages": [
            {
                "page_number": 1,
                "dialogues": [
                    {"speaker": "char1", "speaker_name": "Komaba", "text": "I'm heading out now. Make sure the calves are fed.", "trans": None},
                    {"speaker": "char2", "speaker_name": "Hachiken", "text": "Wait, Komaba! You can't just leave without saying goodbye!", "trans": None},
                ],
            },
            {
                "page_number": 2,
                "dialogues": [
                    {"speaker": "char1", "speaker_name": "Komaba", "text": "The family farm debt won't wait for graduation.", "trans": None},
                    {"speaker": "char2", "speaker_name": "Hachiken", "text": "There must be another way... we can find investors!", "trans": None},
                ],
            },
            {
                "page_number": 3,
                "dialogues": [
                    {"speaker": "char1", "speaker_name": "Komaba", "text": "Thanks, Hachiken. But this is my responsibility now.", "trans": None},
                    {"speaker": "NARRATION", "speaker_name": "Narration", "text": "The school gates clicked shut in the autumn wind.", "trans": None},
                ],
            },
        ],
    },
]
