from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Callable
from src.models.player import Player

ROOT = Path(__file__).resolve().parents[2]
HISTORY_FILE = ROOT / "src" / "resources" / "data" / "achievement_history.json"


class AchievementEngine:
    """Evaluates player achievements dynamically, tracks custom milestones, and persists unlock history."""

    _custom_milestones: dict[str, Callable[[Player], bool]] = {}

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

    def check_all_achievements(self, player: Player) -> dict[str, bool]:
        """Convenience trigger to return a quick dict mapping badge ID to unlocked state."""
        badges = self.get_badges(player)
        return {b["id"]: b["unlocked"] for b in badges}

    @classmethod
    def custom_milestone_add(cls, name: str, condition_fn: Callable[[Player], bool]) -> None:
        """Allows users/plugins to define custom achievements dynamically."""
        cls._custom_milestones[name] = condition_fn

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

        # Basic badges
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
            {
                "id": "veteran_tactician",
                "name": "Veteran Tactician",
                "description": "Reach Mastery Rank 20+.",
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
            },
            # v10 Veteran Badges
            {
                "id": "steel_path_complete",
                "name": "Steel Path Complete",
                "description": "Complete every node on the Steel Path Star Chart.",
                "requirement": "Unlock Steel Path and reach Mastery Rank 15+.",
                "unlocked": player.steel_path_unlocked and player.mastery_rank >= 15
            },
            {
                "id": "all_incarnons",
                "name": "Incarnon Master",
                "description": "Master all standard evolving weapons.",
                "requirement": "Own Phenmor, Laetum, and Praedos.",
                "unlocked": "phenmor" in owned_weapons and "laetum" in owned_weapons and "praedos" in owned_weapons
            },
            {
                "id": "every_prime",
                "name": "Prime Collector",
                "description": "Gather a massive arsenal of gilded primes.",
                "requirement": "Own 15+ prime items.",
                "unlocked": sum(1 for w in owned_weapons if "prime" in w.lower()) >= 15
            },
            {
                "id": "every_companion",
                "name": "Menagerie Keeper",
                "description": "Collect companions, sentinels, and beasts.",
                "requirement": "Own 5+ companions or sentinels.",
                "unlocked": len(player.companion_inventory) >= 5 or sum(1 for w in owned_weapons if "taxon" in w.lower() or "carrier" in w.lower()) >= 3
            },
            {
                "id": "mr30",
                "name": "Grandmaster (MR30)",
                "description": "Achieve the rank of Grandmaster.",
                "requirement": "Reach Mastery Rank 30.",
                "unlocked": player.mastery_rank >= 30
            },
            {
                "id": "lr1_3",
                "name": "Legendary Master (LR1-3)",
                "description": "Surpass the Grandmaster rank to reach Legendary Master status.",
                "requirement": "Reach Mastery Rank 31+.",
                "unlocked": player.mastery_rank >= 31
            }
        ]

        # Add custom milestones
        for name, fn in self._custom_milestones.items():
            try:
                unlocked = fn(player)
            except Exception:
                unlocked = False
            badges.append({
                "id": f"custom_{name.lower().replace(' ', '_')}",
                "name": name,
                "description": "Custom user-defined milestone.",
                "requirement": "Custom rule logic.",
                "unlocked": unlocked
            })

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
