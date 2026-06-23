from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine

class PersonalizedProgressionEngine:
    """Analyzes player account state and generates tailored focus directions with gain estimations."""

    def analyze_profile(self, player: Player) -> dict[str, Any]:
        completed_quests = {q.lower() for q in player.completed_quests}
        owned_mods = {m.lower() for m in player.owned_mods}
        owned_arcanes = {a.lower() for a in player.owned_arcanes}
        owned_weapons = {w.lower() for w in player.owned_weapons}

        # 1. Main Story Progress
        story_order = [
            ("The Second Dream", "5 hours", "+15%"),
            ("The War Within", "6 hours", "+18%"),
            ("The Sacrifice", "4 hours", "+12%"),
            ("The New War", "12 hours", "+30%"),
            ("Angels of the Zariman", "4 hours", "+15%"),
        ]

        for quest_name, eta, gain in story_order:
            if quest_name.lower() not in completed_quests:
                return {
                    "focus": f"Complete Quest: {quest_name}",
                    "why": f"Crucial storyline progression required to access later systems and high-tier zones.",
                    "eta": eta,
                    "power_gain": gain
                }

        # 2. Star Chart / Arbitrations
        if not player.arbitrations_unlocked:
            return {
                "focus": "Unlock Arbitrations",
                "why": "Clear all nodes on the normal Star Chart. Essential to farm Vitus Essence for Galvanized mods.",
                "eta": "8 hours",
                "power_gain": "+20%"
            }

        # 3. Helminth System
        if not player.helminth_unlocked:
            return {
                "focus": "Unlock Helminth System",
                "why": "Requires Rank 3 standing with Entrati in Necralisk. Infuse custom abilities to maximize Warframe synergies.",
                "eta": "6 hours",
                "power_gain": "+12%"
            }

        # 4. Galvanized Mods
        if "galvanized chamber" not in owned_mods or "galvanized aptitude" not in owned_mods:
            return {
                "focus": "Acquire Galvanized Mods",
                "why": "Farm Arbitrations for Vitus Essence. These mods offer massive multishot and status scaling.",
                "eta": "5 hours",
                "power_gain": "+25%"
            }

        # 5. Steel Path Difficulty
        if not player.steel_path_unlocked:
            return {
                "focus": "Unlock Steel Path",
                "why": "Talk to Teshin at any relay. Opens high-level missions, Acolytes, and weapon arcane slots.",
                "eta": "10 hours",
                "power_gain": "+25%"
            }

        # 6. Weapon Mastery Rank Lock
        if player.mastery_rank < 14:
            return {
                "focus": "Reach Mastery Rank 14",
                "why": "Zariman Incarnon weapons (Phenmor, Laetum) require MR 14 to craft and use.",
                "eta": "15 hours",
                "power_gain": "+20%"
            }

        # 7. Weapon Arcanes
        if "primary merciless" not in owned_arcanes:
            return {
                "focus": "Farm Primary Merciless Arcane",
                "why": "Kill Steel Path Acolytes. Provides up to +360% base damage scaling for primary weapons.",
                "eta": "4 hours",
                "power_gain": "+30%"
            }

        # 8. Meta Weapon Acquisition
        if "phenmor" not in owned_weapons:
            return {
                "focus": "Acquire Phenmor Rifle",
                "why": "Purchase blueprint from Cavalero on Zariman. One of the strongest primary weapons in the meta.",
                "eta": "8 hours",
                "power_gain": "+35%"
            }

        # 9. Endgame Builds & Optimization
        pe = ProgressionEngine()
        build_score = pe.get_build_score(player)
        if build_score < 95.0:
            return {
                "focus": "Optimize Endgame Builds",
                "why": "Equip maxed mods/arcanes on meta weapons. Maximize simulated output damage.",
                "eta": "10 hours",
                "power_gain": f"+{round(100 - build_score, 1)}%"
            }

        return {
            "focus": "Fully Optimized",
            "why": "All main story, meta weapons, mods, and systems are unlocked and optimized.",
            "eta": "0 hours",
            "power_gain": "+0%"
        }
