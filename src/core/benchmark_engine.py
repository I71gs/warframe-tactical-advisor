from __future__ import annotations
from typing import Any
from src.models.player import Player

BENCHMARKS = {
    "MR10 (Midgame Gateway)": {
        "weapons": 5,
        "mods": 10,
        "arcanes": 1,
        "builds": 1,
        "progression": 5
    },
    "MR20 (Late Game Challenger)": {
        "weapons": 15,
        "mods": 25,
        "arcanes": 5,
        "builds": 3,
        "progression": 12
    },
    "Legendary (Endgame Veteran)": {
        "weapons": 30,
        "mods": 50,
        "arcanes": 12,
        "builds": 5,
        "progression": 18
    },
    "Endgame Specialist (Absolute Meta)": {
        "weapons": 45,
        "mods": 70,
        "arcanes": 20,
        "builds": 8,
        "progression": 22
    }
}

class BenchmarkEngine:
    """Computes comparison maps between the current player stats and target progression milestones."""

    def evaluate_player(self, player: Player) -> dict[str, dict[str, Any]]:
        # Calculate current player stats
        weapons_count = len(player.owned_weapons)
        mods_count = len(player.owned_mods)
        arcanes_count = len(player.owned_arcanes)
        quests_count = len(player.completed_quests)
        
        # Calculate matching builds count
        from src.core.build_database import BUILDS
        builds_count = 0
        owned_w_lower = {w.lower() for w in player.owned_weapons}
        for b in BUILDS:
            if b["weapon"].lower() in owned_w_lower:
                builds_count += 1

        current_stats = {
            "weapons": weapons_count,
            "mods": mods_count,
            "arcanes": arcanes_count,
            "builds": builds_count,
            "progression": quests_count
        }

        results = {}
        for target, targets in BENCHMARKS.items():
            results[target] = {
                "metrics": {
                    "weapons": {"current": weapons_count, "target": targets["weapons"], "pct": min(100, int(weapons_count / targets["weapons"] * 100)) if targets["weapons"] > 0 else 100},
                    "mods": {"current": mods_count, "target": targets["mods"], "pct": min(100, int(mods_count / targets["mods"] * 100)) if targets["mods"] > 0 else 100},
                    "arcanes": {"current": arcanes_count, "target": targets["arcanes"], "pct": min(100, int(arcanes_count / targets["arcanes"] * 100)) if targets["arcanes"] > 0 else 100},
                    "builds": {"current": builds_count, "target": targets["builds"], "pct": min(100, int(builds_count / targets["builds"] * 100)) if targets["builds"] > 0 else 100},
                    "progression": {"current": quests_count, "target": targets["progression"], "pct": min(100, int(quests_count / targets["progression"] * 100)) if targets["progression"] > 0 else 100}
                }
            }
        return results
