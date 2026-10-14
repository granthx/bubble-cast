"""
Data access and domain logic for Manga Speaker API.
Loads sequence metadata, test predictions, and development labels.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Base paths
ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT_DIR / "dataset"
TEST_PRED_FILE = ROOT_DIR / "test_predictions_7b.jsonl"
DEV_LABELS_FILE = DATASET_DIR / "development" / "labels.jsonl"
SEQUENCES_FILE = DATASET_DIR / "sequences.json"
README_FILE = ROOT_DIR / "README.md"

# Canonical series titles for sequences
SERIES_TITLES: Dict[str, str] = {
    # Tokyo Ghoul:re chapters
    "seq_81b1782990ab7950": "Tokyo Ghoul:re — Auction Disguise Operation",
    "seq_14469aeb38963085": "Tokyo Ghoul:re — Sasaki & Shirazu Investigation",
    "seq_e9ffbb64217c2fed": "Tokyo Ghoul:re — Quinx Squad Surgery Briefing",
    "seq_316bc7bd43ed6996": "Tokyo Ghoul:re — Sasaki Haise Squad Promise",
    "seq_cf7df70d4bba5da5": "Tokyo Ghoul:re — Auction Hall Surveillance",
    # Silver Spoon chapters
    "seq_6b18300406fa878f": "Silver Spoon — Komaba Dorm Departure",
    "seq_c780ac6d1dbd1242": "Silver Spoon — Farm Debt & Dreams",
    "seq_5303b549f62e9d3f": "Silver Spoon — High School Gate Farewell",
    "seq_d455cfd18edfb0ba": "Silver Spoon — Equestrian Stables Encounter",
    # Vagabond chapters
    "seq_e456a0394af99570": "Vagabond — Musashi Yoshioka Dojo Challenge",
    "seq_c5622aca7487a661": "Vagabond — Denshichiro Blizzard Duel (Part 1)",
    "seq_75aeca6c7131544b": "Vagabond — Denshichiro Blizzard Duel (Part 2)",
    # Mononoke chapters
    "seq_e04ef3d20fd0baa8": "Mononoke — Lady Mizue Manor Haunting",
    "seq_6aa313a0c0fa1c39": "Mononoke — Medicine Seller Exorcism",
    "seq_32c47ca11b40ca8a": "Mononoke — Spiritual Attack on Manor Guards",
}

# Editorial character profiles with visual appearance cues across panels
CHARACTER_PROFILES: Dict[str, Dict[str, Tuple[str, str]]] = {
    # Tokyo Ghoul:re chapters
    "seq_81b1782990ab7950": {
        "char1": ("Shirazu Gin", "Punk investigator with blonde hair & necktie in disguise"),
        "char2": ("Sasaki Haise", "Wavy black/white hair, CCG squad leader in dress disguise"),
        "char3": ("Tooru Mutsuki", "Slender investigator with eyepatch in disguise"),
        "char4": ("Saiko Yonebayashi", "Short gamer girl with twin tails"),
        "char5": ("Nightclub Guests", "Hostesses and onlookers in club"),
        "char6": ("Club Host / Staff", "Staff member discussing auction list"),
    },
    "seq_14469aeb38963085": {
        "char1": ("Shirazu Gin", "Striped scarf & blonde punk hair discussing Saiko's future"),
        "char2": ("Sasaki Haise", "Wavy black/white hair, squad leader responding with care"),
        "char3": ("Akira Mado", "Senior investigator speaking in flashback"),
        "char4": ("Academy Teacher", "Lecturer in flashback CCG classroom"),
        "char5": ("Sasaki Haise", "Mentor discussing Saiko's surgical past"),
        "char6": ("Senior Staff", "Medical staff discussing surgical risks"),
        "NARRATION": ("CCG Case File & Narrative", "Narration boxes explaining Saiko's backstory"),
    },
    "seq_e9ffbb64217c2fed": {
        "char1": ("Sasaki Haise", "Squad leader with wavy hair discussing memories"),
        "char2": ("Shirazu Gin", "Blonde squad member debating Saiko's family circumstances"),
        "char3": ("Tooru Mutsuki", "Investigator discussing his father"),
        "NARRATION": ("CCG Narrative Box", "Background context on the Quinx surgery"),
    },
    "seq_316bc7bd43ed6996": {
        "char1": ("Sasaki Haise", "Squad leader assuring the squad he will not abandon them"),
        "char2": ("Tooru Mutsuki", "Investigator celebrating victory with squad"),
        "char3": ("Saiko Yonebayashi", "Twin tails girl performing celebration dance"),
        "char4": ("Internal Thoughts", "Reflections on past memory loss"),
    },
    "seq_cf7df70d4bba5da5": {
        "char1": ("Roma Hoito", "Girl in sunglasses watching Haise from afar"),
        "char2": ("Nico", "Tall figure with bandana & lipstick observing Haise"),
        "char3": ("Auction Attendant", "Background staff member ordering guests to sit"),
    },
    # Silver Spoon chapters
    "seq_6b18300406fa878f": {
        "char1": ("Komaba Ichiro", "Muscular dairy farmer boy, short dark hair, packing dorm bags"),
        "char2": ("Hachiken Yugo", "Main protagonist, glasses, school uniform, questioning Komaba"),
    },
    "seq_c780ac6d1dbd1242": {
        "char1": ("Komaba Ichiro", "Work jacket, quietly explaining farm debts to Hachiken"),
        "char2": ("Hachiken Yugo", "Glasses, emotional expression, pleading with Komaba not to quit"),
        "char3": ("School Teacher", "Staff member outside loading moving truck"),
        "char4": ("Dorm Mates", "Students greeting Hachiken in hallway"),
        "char5": ("Classmates", "Boys asking about sick day and farm work"),
        "char6": ("Farm Supporters", "Thanking Komaba family for bacon gifts"),
    },
    "seq_5303b549f62e9d3f": {
        "char1": ("Komaba Ichiro", "Walking out through school gates with bags, waving goodbye"),
        "char2": ("Aki Mikage", "Girl with dark hair, looking sorrowfully at Komaba's departure"),
        "char3": ("Hachiken Yugo", "Screaming in frustration about giving up on baseball dreams"),
    },
    "seq_d455cfd18edfb0ba": {
        "char1": ("Vice Principal / Dog", "Dog barking in schoolyard"),
        "char2": ("Hachiken & Aki", "Hachiken with glasses talking to Aki Mikage by horse stable"),
        "char3": ("Aki Mikage", "Holding horse reins, telling Hachiken to let go of regret"),
    },
    # Vagabond chapters
    "seq_e456a0394af99570": {
        "char1": ("Miyamoto Musashi", "Bearded wandering ronin, wild black hair, issuing challenge"),
        "char2": ("Yoshioka Denshichiro", "Topknot master swordsman accepting formal challenge"),
        "char3": ("Denshichiro", "Final duel warning before Kyoto winter"),
    },
    "seq_c5622aca7487a661": {
        "char1": ("Miyamoto Musashi", "Ronin in snow duel, calculating blade distance"),
        "char2": ("Yoshioka Denshichiro", "Rival samurai swinging wooden sword in blizzard"),
        "char3": ("Dojo Spectators", "Samurai watching duel from gallery in silence"),
        "char4": ("Onlookers", "Crowd shouting encouragement in blizzard"),
    },
    "seq_75aeca6c7131544b": {
        "char1": ("Miyamoto Musashi", "Close-up of bearded face in deadly duel focus"),
        "char2": ("Yoshioka Denshichiro", "Sweating samurai facing Musashi's lethal posture"),
        "char3": ("Crowd Spectators", "Spectators cheering duel with bated breath"),
        "char4": ("Dojo Elders", "Urging Denshichiro to press forward"),
        "char5": ("Onlookers", "Shouting from sidelines"),
    },
    # Mononoke chapters
    "seq_e04ef3d20fd0baa8": {
        "char1": ("Lady Mizue", "Terrified noble geisha in patterned kimono"),
        "char2": ("Retainer / Attendant", "Shouting Mizue-sama in shock at strange omen"),
        "char3": ("Tamaki", "Elder retainer calling out in fear"),
        "char4": ("Household Retainers", "Attendants screaming in terror"),
    },
    "seq_6aa313a0c0fa1c39": {
        "char1": ("Lady Mizue", "Trapped in room screaming go away"),
        "char2": ("Retainer", "Bowing and pleading to atone for past errors"),
        "char3": ("Medicine Seller", "Mysterious traveler warning of supernatural spirit"),
    },
    "seq_32c47ca11b40ca8a": {
        "char1": ("Lady Mizue", "Horrified expression screaming across panels"),
        "char2": ("Attendant", "Shouting Mizue-sama from sliding doorway"),
        "char3": ("Medicine Seller", "Ordering guards to step back from spirit circle"),
        "char4": ("Guards", "Men fleeing spiritual attack"),
        "char5": ("Retainers", "Falling back in shock"),
    },
}

SPEAKER_PALETTE: Dict[str, Dict[str, str]] = {
    "NARRATION": {"label": "NARRATION", "color": "#FBBF24", "bg": "rgba(251, 191, 36, 0.12)", "border": "rgba(251, 191, 36, 0.35)", "icon": "📖"},
    "char1": {"label": "Char 1", "color": "#60A5FA", "bg": "rgba(96, 165, 250, 0.12)", "border": "rgba(96, 165, 250, 0.35)", "icon": "👤"},
    "char2": {"label": "Char 2", "color": "#F472B6", "bg": "rgba(244, 114, 182, 0.12)", "border": "rgba(244, 114, 182, 0.35)", "icon": "👤"},
    "char3": {"label": "Char 3", "color": "#C084FC", "bg": "rgba(192, 132, 252, 0.12)", "border": "rgba(192, 132, 252, 0.35)", "icon": "👤"},
    "char4": {"label": "Char 4", "color": "#FB923C", "bg": "rgba(251, 146, 60, 0.12)", "border": "rgba(251, 146, 60, 0.35)", "icon": "👤"},
    "char5": {"label": "Char 5", "color": "#38BDF8", "bg": "rgba(56, 189, 248, 0.12)", "border": "rgba(56, 189, 248, 0.35)", "icon": "👤"},
    "char6": {"label": "Char 6", "color": "#FACC15", "bg": "rgba(250, 204, 21, 0.12)", "border": "rgba(250, 204, 21, 0.35)", "icon": "👤"},
}


class MangaRepository:
    def __init__(self):
        self.sequences_meta: Dict[str, Dict[str, Any]] = {}
        self.test_predictions: Dict[str, List[List[Dict[str, str]]]] = {}
        self.dev_labels: Dict[str, List[List[Dict[str, str]]]] = {}
        self.load_all()

    def load_all(self):
        # 1. Sequences metadata
        if SEQUENCES_FILE.exists():
            with open(SEQUENCES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    self.sequences_meta[item["sequence_id"]] = item

        # 2. Test predictions (15 sequences)
        if TEST_PRED_FILE.exists():
            with open(TEST_PRED_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        obj = json.loads(line)
                        self.test_predictions[obj["sequence_id"]] = obj["pages"]

        # 3. Development labels (80 sequences)
        if DEV_LABELS_FILE.exists():
            with open(DEV_LABELS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        obj = json.loads(line)
                        self.dev_labels[obj["sequence_id"]] = obj["pages"]

    def get_sources(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "test",
                "label": "Test Predictions (7B Fine-Tuned)",
                "count": len(self.test_predictions),
                "description": "15 officially benchmarked test sequences with continuous character IDs and reading order.",
            },
            {
                "id": "dev",
                "label": "Development Archive (Ground Truth)",
                "count": len(self.dev_labels),
                "description": "80 gold development sequences from varied published manga chapters.",
            },
        ]

    def list_sequences(self, source: str = "test") -> List[Dict[str, Any]]:
        data_source = self.test_predictions if source == "test" else self.dev_labels
        items = []

        for seq_id, pages in sorted(data_source.items()):
            meta = self.sequences_meta.get(seq_id, {})
            title = SERIES_TITLES.get(seq_id, meta.get("title") or "Development Manga Chapter")
            total_lines = sum(len(p) for p in pages)
            unique_speakers = sorted(set(l.get("speaker", "char1") for p in pages for l in p))

            items.append({
                "sequence_id": seq_id,
                "title": title,
                "display_label": f"{seq_id}  ·  {title} ({total_lines} lines)",
                "page_count": len(pages),
                "total_lines": total_lines,
                "speaker_count": len(unique_speakers),
                "speakers": unique_speakers,
                "has_images": bool(meta.get("images")),
            })

        return items

    def get_sequence_detail(self, sequence_id: str, source: str = "test") -> Optional[Dict[str, Any]]:
        data_source = self.test_predictions if source == "test" else self.dev_labels
        if sequence_id not in data_source:
            return None

        pages_raw = data_source[sequence_id]
        meta = self.sequences_meta.get(sequence_id, {})
        images_rel = meta.get("images", [f"{source}/{sequence_id}/page{i+1}.png" for i in range(len(pages_raw))])
        
        # Build image URLs served by backend API
        image_urls = [f"/api/images/{p}" for p in images_rel]

        # Gather active speakers and character profiles
        profiles_map = CHARACTER_PROFILES.get(sequence_id, {})
        all_speakers = sorted(set(l.get("speaker", "char1") for p in pages_raw for l in p))
        total_lines = sum(len(p) for p in pages_raw)

        characters = []
        for spk in all_speakers:
            s_norm = spk.lower()
            if s_norm.startswith("character"):
                s_norm = "char" + s_norm[len("character"):]
            elif s_norm == "narration":
                s_norm = "NARRATION"

            palette = SPEAKER_PALETTE.get(s_norm, {
                "label": spk,
                "color": "#65D6A6",
                "bg": "rgba(101, 214, 166, 0.12)",
                "border": "rgba(101, 214, 166, 0.35)",
                "icon": "👤",
            })

            profile = profiles_map.get(spk) or profiles_map.get(s_norm)
            name = profile[0] if profile else spk.title()
            desc = profile[1] if profile else "Active speaker detected in sequential panels"
            line_cnt = sum(1 for p in pages_raw for l in p if l.get("speaker") == spk)
            share_pct = round((line_cnt / max(1, total_lines)) * 100, 1)

            characters.append({
                "id": spk,
                "normalized_id": s_norm,
                "name": name,
                "description": desc,
                "lines_count": line_cnt,
                "dialogue_share_pct": share_pct,
                "color": palette["color"],
                "bg": palette["bg"],
                "border": palette["border"],
                "icon": palette["icon"],
            })

        # Format pages with dialogue items
        pages = []
        for p_idx, p_lines in enumerate(pages_raw):
            dialogue_items = []
            for b_idx, line in enumerate(p_lines, 1):
                spk = line.get("speaker", "char1")
                s_norm = spk.lower()
                if s_norm.startswith("character"):
                    s_norm = "char" + s_norm[len("character"):]
                elif s_norm == "narration":
                    s_norm = "NARRATION"

                palette = SPEAKER_PALETTE.get(s_norm, {
                    "label": spk,
                    "color": "#65D6A6",
                    "bg": "rgba(101, 214, 166, 0.12)",
                    "border": "rgba(101, 214, 166, 0.35)",
                    "icon": "👤",
                })
                profile = profiles_map.get(spk) or profiles_map.get(s_norm)
                name = profile[0] if profile else spk.title()

                dialogue_items.append({
                    "order_index": b_idx,
                    "speaker": spk,
                    "speaker_name": name,
                    "color": palette["color"],
                    "bg": palette["bg"],
                    "border": palette["border"],
                    "icon": palette["icon"],
                    "text": line.get("text", ""),
                })

            pages.append({
                "page_number": p_idx + 1,
                "image_url": image_urls[p_idx] if p_idx < len(image_urls) else None,
                "image_rel": images_rel[p_idx] if p_idx < len(images_rel) else None,
                "dialogues": dialogue_items,
                "is_silent": len(dialogue_items) == 0,
            })

        title = SERIES_TITLES.get(sequence_id, meta.get("title") or "Development Manga Chapter")

        return {
            "sequence_id": sequence_id,
            "title": title,
            "source": source,
            "total_lines": total_lines,
            "speaker_count": len(all_speakers),
            "page_count": len(pages),
            "characters": characters,
            "pages": pages,
        }


# Singleton repo instance
repo = MangaRepository()
