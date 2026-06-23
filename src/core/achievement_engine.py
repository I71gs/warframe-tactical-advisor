from __future__ import annotations
from typing import Any
from src.models.player import Player

class AchievementEngine:
    """Evaluates player achievements dynamically based on inventory, quests, and scores."""

    def get_badges(self, player: Player) -> list[dict[str, Any]]:
        completed_quests = {q.lower() for q in player.completed_quests}
        owned_weapons = {w.lower() for w in player.owned_weapons}
        owned_mods = {m.lower() for m in player.owned_mods}

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
            }
        ]
        return badges
