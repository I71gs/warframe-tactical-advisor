from __future__ import annotations
from typing import Any
from src.core.snapshot_engine import SnapshotEngine
from src.core.progression_engine import ProgressionEngine
from src.models.player import Player

class PredictionEngine:
    """Uses linear extrapolation from historical snapshot growth to predict completion timeframes."""

    def __init__(self) -> None:
        self.se = SnapshotEngine()
        self.pe = ProgressionEngine()

    def predict_milestones(self, player: Player) -> dict[str, Any]:
        current_score = self.pe.get_readiness_score(player)
        snapshots = self.se.get_snapshots()

        # Calculate historical daily growth rate
        daily_growth = 2.0  # Default fallback velocity: 2% score growth per day
        if len(snapshots) >= 2:
            first = snapshots[0]
            last = snapshots[-1]
            elapsed_sec = last.get("timestamp", 0) - first.get("timestamp", 0)
            elapsed_days = elapsed_sec / 86400.0
            
            score_diff = last.get("readiness", 0.0) - first.get("readiness", 0.0)
            if elapsed_days > 0.05 and score_diff > 0: # Ensure at least ~1hr and positive growth
                daily_growth = max(0.5, score_diff / elapsed_days)

        # Steel Path Target (70% score or unlocked)
        sp_days = 0
        if not player.steel_path_unlocked and current_score < 70.0:
            sp_days = int((70.0 - current_score) / daily_growth)

        # Archon Hunts Target (85% score or ready)
        archon_days = 0
        if current_score < 85.0:
            archon_days = int((85.0 - current_score) / daily_growth)

        # Endgame Target (95% score)
        endgame_days = 0
        if current_score < 95.0:
            endgame_days = int((95.0 - current_score) / daily_growth)

        # Ensure logically increasing timeline
        if archon_days < sp_days:
            archon_days = sp_days + 2
        if endgame_days < archon_days:
            endgame_days = archon_days + 3

        return {
            "daily_growth_rate": round(daily_growth, 2),
            "days_to_steel_path": sp_days if not player.steel_path_unlocked else 0,
            "days_to_archons": archon_days,
            "days_to_endgame": endgame_days
        }
export_prediction = PredictionEngine()
