from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine

class AccountRatingEngine:
    """Grades player profiles into logical skill tiers based on readiness scores."""

    def __init__(self) -> None:
        self.pe = ProgressionEngine()

    def get_rating(self, player: Player) -> dict[str, Any]:
        score = self.pe.get_readiness_score(player)
        
        if score < 30.0:
            grade = "Beginner"
            color = "#ef4444"  # Red
            desc = "Starting out. Focus on main story quests, unlocking planets, and clearing standard nodes."
        elif score < 60.0:
            grade = "Intermediate"
            color = "#ffb76b"  # Orange
            desc = "Mid-game adventurer. Complete narrative quests and start farming key primary mods."
        elif score < 80.0:
            grade = "Advanced"
            color = "#caa3ff"  # Light Purple
            desc = "Preparing for late-game. Clear normal Star Chart to unlock Arbitrations and buy Galvanized mods."
        elif score < 90.0:
            grade = "Veteran"
            color = "#00a3cc"  # Cyan
            desc = "Late-game tactician. Farm Steel Path Acolytes and acquire powerful arcanes and Meta items."
        elif score < 98.0:
            grade = "Endgame"
            color = "#ffd700"  # Gold
            desc = "Elite coach level. Optimize weapon builds and maximize synergies across full loadouts."
        else:
            grade = "Legendary"
            color = "#22c55e"  # Green
            desc = "Perfect execution. Complete mastery of all systems, quests, mods, and meta builds."

        return {
            "score": score,
            "grade": grade,
            "color": color,
            "description": desc
        }
