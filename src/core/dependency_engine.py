from __future__ import annotations
from src.models.player import Player

class DependencyEngine:
    """Resolves and evaluates prerequisites for weapons, mods, and arcanes."""

    def __init__(self) -> None:
        # Prerequisite definitions
        # Format: {item_name_lower: {"quests": [...], "mr": int, "other": [check_flags]}}
        self._prereqs = {
            "phenmor": {
                "quests": ["Angels of the Zariman"],
                "mr": 14,
                "other": []
            },
            "laetum": {
                "quests": ["Angels of the Zariman"],
                "mr": 14,
                "other": []
            },
            "felarx": {
                "quests": ["Angels of the Zariman"],
                "mr": 14,
                "other": []
            },
            "galvanized chamber": {
                "quests": ["Angels of the Zariman"], # Zariman completes main star chart
                "mr": 10,
                "other": ["arbitrations_unlocked"]
            },
            "galvanized aptitude": {
                "quests": ["Angels of the Zariman"],
                "mr": 10,
                "other": ["arbitrations_unlocked"]
            },
            "primary merciless": {
                "quests": ["Angels of the Zariman"],
                "mr": 10,
                "other": ["steel_path_unlocked"]
            },
            "secondary merciless": {
                "quests": ["Angels of the Zariman"],
                "mr": 10,
                "other": ["steel_path_unlocked"]
            },
            "kuva bramma": {
                "quests": ["The War Within"],
                "mr": 15,
                "other": []
            },
            "kuva nukor": {
                "quests": ["The War Within"],
                "mr": 13,
                "other": []
            },
            "latron incarnon": {
                "quests": ["Angels of the Zariman"],
                "mr": 12,
                "other": ["steel_path_unlocked"] # Steel Path Circuit
            },
            "burston incarnon": {
                "quests": ["Angels of the Zariman"],
                "mr": 12,
                "other": ["steel_path_unlocked"] # Steel Path Circuit
            },
            "torid": {
                "quests": [],
                "mr": 4,
                "other": []
            },
            "nataruk": {
                "quests": ["The New War"],
                "mr": 0,
                "other": []
            }
        }

    def get_unmet_dependencies(self, item_name: str, player: Player) -> list[str]:
        """Return a list of unmet dependencies/prerequisites for an item."""
        name_lower = item_name.strip().lower()
        
        # If we have recommendations named "Acquire Phenmor", strip the prefix
        if name_lower.startswith("acquire "):
            name_lower = name_lower[len("acquire "):].strip()
            
        if name_lower not in self._prereqs:
            return []

        requirements = self._prereqs[name_lower]
        unmet = []

        # Check Mastery Rank
        if player.mastery_rank < requirements["mr"]:
            unmet.append(f"Mastery Rank {requirements['mr']}+")

        # Check Quests
        completed_quests = {q.lower() for q in player.completed_quests}
        for quest in requirements["quests"]:
            if quest.lower() not in completed_quests:
                unmet.append(f"Quest: {quest}")

        # Check other status flags
        for flag in requirements["other"]:
            if flag == "arbitrations_unlocked" and not player.arbitrations_unlocked:
                unmet.append("Arbitrations Unlocked")
            elif flag == "steel_path_unlocked" and not player.steel_path_unlocked:
                unmet.append("Steel Path Unlocked")
            elif flag == "helminth_unlocked" and not player.helminth_unlocked:
                unmet.append("Helminth System Unlocked")

        return unmet

    def is_item_unlocked(self, item_name: str, player: Player) -> bool:
        """Check if all dependencies for an item are met."""
        return len(self.get_unmet_dependencies(item_name, player)) == 0
