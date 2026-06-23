from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine

class NextActionEngine:
    """Evaluates player progression, inventory gaps, and unlocks to resolve Today's Priority."""

    def determine_next_action(self, player: Player) -> dict[str, Any]:
        completed_quests = {q.lower() for q in player.completed_quests}
        owned_mods = {m.lower() for m in player.owned_mods}
        owned_arcanes = {a.lower() for a in player.owned_arcanes}
        owned_weapons = {w.lower() for w in player.owned_weapons}

        # 1. Main Quest line takes absolute priority
        quest_order = [
            ("The Second Dream", "Unlock Focus systems, Operator, and custom story nodes.", 15),
            ("The War Within", "Unlock Kuva Fortress, Riven mods, and Kuva Liches.", 20),
            ("Chains of Harrow", "Prerequisite for critical story unlocks.", 10),
            ("The Sacrifice", "Acquire Umbra Warframe and Umbra mods.", 15),
            ("The New War", "Access the late-game, Archon hunts, and Zariman content.", 30),
            ("Angels of the Zariman", "Unlock Cavalero and Incarnon weapon farming.", 25)
        ]
        
        for quest, reason, gain in quest_order:
            if quest.lower() not in completed_quests:
                return {
                    "priority": f"Complete Quest: {quest}",
                    "reason": reason,
                    "gain": f"+{gain}% Account Progression"
                }

        # 2. Star Chart Completion (Arbitrations Access)
        if not player.arbitrations_unlocked:
            return {
                "priority": "Clear Remaining Star Chart Nodes",
                "reason": "Complete all nodes to unlock Arbitrations for farming high-meta mods.",
                "gain": "+15% Progression Strength"
            }

        # 3. Critical Mods (Galvanized Chamber, etc.)
        if "galvanized chamber" not in owned_mods:
            return {
                "priority": "Farm Arbitrations",
                "reason": "Acquire Galvanized Chamber for massive primary weapon multishot increase.",
                "gain": "+18% Damage Potential"
            }
        if "galvanized aptitude" not in owned_mods:
            return {
                "priority": "Farm Arbitrations",
                "reason": "Acquire Galvanized Aptitude for status damage scaling.",
                "gain": "+12% Damage Potential"
            }

        # 4. Steel Path Unlock
        if not player.steel_path_unlocked:
            return {
                "priority": "Unlock Steel Path",
                "reason": "Talk to Teshin at any relay to access Steel Path missions and Acolytes.",
                "gain": "+20% Progress Rank"
            }

        # 5. Critical Arcanes (Primary Merciless)
        if "primary merciless" not in owned_arcanes:
            return {
                "priority": "Farm Steel Path Acolytes",
                "reason": "Acquire Primary Merciless arcane for stacking base weapon damage boosts.",
                "gain": "+25% Base Weapon Power"
            }

        # 6. Zariman Incarnons
        if "phenmor" not in owned_weapons:
            return {
                "priority": "Farm Zariman Bounties",
                "reason": "Acquire Phenmor blueprint and materials from Cavalero on the Zariman.",
                "gain": "+15% Primary Weapon Power"
            }
        if "laetum" not in owned_weapons:
            return {
                "priority": "Farm Zariman Bounties",
                "reason": "Acquire Laetum Incarnon secondary from Cavalero on the Zariman.",
                "gain": "+15% Secondary Weapon Power"
            }

        # 7. Default Endgame optimization
        return {
            "priority": "Optimize Endgame Builds",
            "reason": "Max out owned mods, arcanes, and form loadout synergies for high-level content.",
            "gain": "+5% Effectiveness"
        }
