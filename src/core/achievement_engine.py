from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Any
from src.models.player import Player

ROOT = Path(__file__).resolve().parents[2]
HISTORY_FILE = ROOT / "src" / "resources" / "data" / "achievement_history.json"

class AchievementEngine:
    """Evaluates player achievements dynamically and persists unlock history on disk."""

    def __init__(self, history_file: Path | str | None = None) -> None:
        self.history_file = Path(history_file) if history_file else HISTORY_FILE
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def load_history(self) -> dict[str, str]:
        """Loads persistent unlock dates from JSON file."""
        if not self.history_file.exists():
            return {}
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_history(self, history: dict[str, str]) -> None:
        """Saves unlock dates to JSON file."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4)
        except Exception:
            pass

    def get_badges(self, player: Player) -> list[dict[str, Any]]:
        completed_quests = {q.lower() for q in player.completed_quests}
        owned_weapons = {w.lower() for w in player.owned_weapons}
        owned_mods = {m.lower() for m in player.owned_mods}

        # Check resource counts
        from src.core.resource_engine import ResourceEngine
        res_owned = ResourceEngine().load_owned_resources()
        credits_count = res_owned.get("Credits", 0)
        endo_count = res_owned.get("Endo", 0)
        forma_count = res_owned.get("Forma", 0)

        badges = [
            {
                "id": "story_master",
                "name": "Story Master",
                "description": "Unlock and complete all core cinematic quests up to Angels of Zariman.",
                "requirement": "Complete quests: The Second Dream, The War Within, The Sacrifice, The New War, and Angels of Zariman.",
                "unlocked": all(q in completed_quests for q in ["the second dream", "the war within", "the sacrifice", "the new war", "angels of the zariman"])
            },
            {
                "id": "steel_path",
                "name": "Steel Path Initiate",
                "description": "Cross the threshold into the high-difficulty Steel Path Star Chart.",
                "requirement": "Unlock Steel Path difficulty via Teshin.",
                "unlocked": player.steel_path_unlocked
            },
            {
                "id": "archon_hunter",
                "name": "Archon Hunter",
                "description": "Prepare yourself to hunt the deadly Archons weekly.",
                "requirement": "Reach Mastery Rank 12+ and complete 'The New War' quest.",
                "unlocked": player.mastery_rank >= 12 and "the new war" in completed_quests
            },
            {
                "id": "incarnon_collector",
                "name": "Incarnon Collector",
                "description": "Obtain top-meta Zariman evolving weapons.",
                "requirement": "Own either the Phenmor or Laetum Incarnon weapons.",
                "unlocked": "phenmor" in owned_weapons or "laetum" in owned_weapons
            },
            {
                "id": "mod_master",
                "name": "Mod Master",
                "description": "Add Arbitration powerhouses to your primary arsenal.",
                "requirement": "Own the 'Galvanized Chamber' and 'Galvanized Aptitude' mods.",
                "unlocked": "galvanized chamber" in owned_mods and "galvanized aptitude" in owned_mods
            },
            # Veteran Badges
            {
                "id": "veteran_tactician",
                "name": "Veteran Tactician",
                "description": "Demonstrate long-term dedication and deep tactical understanding of the Origin System.",
                "requirement": "Reach Mastery Rank 20+.",
                "unlocked": player.mastery_rank >= 20
            },
            {
                "id": "star_chart_vanquisher",
                "name": "Star Chart Vanquisher",
                "description": "Conquer all high-level challenges in the solar system.",
                "requirement": "Unlock Steel Path, Arbitrations, and Helminth systems.",
                "unlocked": player.steel_path_unlocked and player.arbitrations_unlocked and player.helminth_unlocked
            },
            # Resource Milestones
            {
                "id": "millionaire",
                "name": "Milestone: Millionaire",
                "description": "Amass a fortune of credits to cover costly foundry operations.",
                "requirement": "Own 1,000,000+ Credits.",
                "unlocked": credits_count >= 1000000
            },
            {
                "id": "endo_hoarder",
                "name": "Milestone: Endo Hoarder",
                "description": "Acquire sufficient raw fusion power to max out primordial mods.",
                "requirement": "Own 50,000+ Endo.",
                "unlocked": endo_count >= 50000
            },
            {
                "id": "forma_fanatic",
                "name": "Milestone: Forma Fanatic",
                "description": "Stockpile polar alignment catalysts for intensive weapon customization.",
                "requirement": "Own 10+ Forma.",
                "unlocked": forma_count >= 10
            }
        ]

        # Update persistent history
        history = self.load_history()
        updated = False
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for b in badges:
            bid = b["id"]
            if b["unlocked"]:
                if bid not in history:
                    history[bid] = now_str
                    updated = True
                b["unlocked_at"] = history[bid]
            else:
                b["unlocked_at"] = "Not Unlocked Yet"

        if updated:
            self.save_history(history)

        return badges
