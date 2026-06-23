from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.build_database import BuildDatabase

class BuildRecommender:
    """Evaluates player mod and arcane inventory against high-tier build templates, computing progress metrics."""

    def __init__(self) -> None:
        self.db = BuildDatabase()

    def recommend_build(self, player: Player, weapon_name: str) -> dict[str, Any] | None:
        build = self.db.get_build_for_weapon(weapon_name)
        if not build:
            return None

        player_mods = {m.lower() for m in player.owned_mods}
        player_arcanes = {a.lower() for a in player.owned_arcanes}

        owned_items = []
        missing_items = []

        # Check mods
        for mod in build["mods"]:
            if mod.lower() in player_mods:
                owned_items.append(f"Mod: {mod}")
            else:
                missing_items.append(f"Mod: {mod}")

        # Check arcane
        arcane = build["arcane"]
        if arcane.lower() in player_arcanes:
            owned_items.append(f"Arcane: {arcane}")
        else:
            missing_items.append(f"Arcane: {arcane}")

        # Score calculations
        total_slots = len(build["mods"]) + 1 # mods + arcane
        owned_slots = len(owned_items)
        potential = build["rating"]
        
        current_score = (owned_slots / total_slots) * potential if total_slots > 0 else 0.0
        gain = potential - current_score

        return {
            "weapon": build["weapon"],
            "owned": owned_items,
            "missing": missing_items,
            "current_score": round(current_score, 1),
            "potential_score": potential,
            "gain": f"+{round(gain, 1)}%",
            "element": build["element"]
        }
export_recommender = BuildRecommender()
