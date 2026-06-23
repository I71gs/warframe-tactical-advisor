from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.cache_manager import CacheManager
from src.core.progression_engine import ProgressionEngine

class TimelineReplayEngine:
    """Computes daily historic benchmarks and generates replay states for the slider."""

    def __init__(self) -> None:
        self.progression_engine = ProgressionEngine()

    def get_replay_data(self, player: Player) -> list[dict[str, Any]]:
        """Returns chronological steps representing the player's progression milestones."""
        cm = CacheManager()
        history = cm.load_cache("history")
        snapshots = history.get("data", {}).get("snapshots", [])
        
        if len(snapshots) >= 3:
            # Format real snapshots
            steps = []
            for idx, snap in enumerate(snapshots):
                steps.append({
                    "step_name": f"Day {idx + 1}",
                    "date": snap.get("date", "Unknown"),
                    "mastery_rank": int(snap.get("mastery", player.mastery_rank)),
                    "readiness": float(snap.get("readiness", 50.0)),
                    "milestone": "Custom Snapshot",
                    "details": f"Story Completion: {snap.get('story')}% | Builds: {snap.get('builds')}%"
                })
            return steps

        # Generates fallback simulation checklist to visualize progression replay
        fallback_steps = [
            {
                "step_name": "Day 1 (Initiate)",
                "date": "Day 1",
                "mastery_rank": 1,
                "readiness": 10.0,
                "milestone": "Vor's Prize",
                "details": "Tutorial complete. Mastery Rank 1. Basic Star Chart exploration."
            },
            {
                "step_name": "Day 7 (Acolyte)",
                "date": "Day 7",
                "mastery_rank": 5,
                "readiness": 30.0,
                "milestone": "The Second Dream",
                "details": "Completed The Second Dream. Unlocked Operator Focus system."
            },
            {
                "step_name": "Day 14 (Pathfinder)",
                "date": "Day 14",
                "mastery_rank": 8,
                "readiness": 55.0,
                "milestone": "The War Within",
                "details": "Completed The War Within and The Sacrifice. Unlocked Umbral mods."
            },
            {
                "step_name": "Day 21 (Vanguard)",
                "date": "Day 21",
                "mastery_rank": 10,
                "readiness": 70.0,
                "milestone": "The New War",
                "details": "Completed The New War. Unlocked Zariman content and Nataruk bow."
            },
            {
                "step_name": "Day 28 (Champion)",
                "date": "Day 28",
                "mastery_rank": 12,
                "readiness": 85.0,
                "milestone": "Steel Path Access",
                "details": "Steel Path unlocked. Farming Acolytes for Primary Merciless."
            },
            {
                "step_name": "Day 30 (Grandmaster)",
                "date": "Day 30",
                "mastery_rank": 14,
                "readiness": 95.0,
                "milestone": "Archon Hunts Ready",
                "details": "Meta Zariman weapons fully built. Ready for Archon Hunts and endgame."
            }
        ]
        return fallback_steps
