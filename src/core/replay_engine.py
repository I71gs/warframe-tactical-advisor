from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.snapshot_repository import SnapshotRepository

class ReplayEngine:
    """Evaluates progression milestones and compiles speed telemetry from profile logs."""

    def get_timeline_data(self, player: Player, repo: SnapshotRepository | None = None) -> list[dict[str, Any]]:
        """Maps milestones to their unlock statuses and resolution dates."""
        repo = repo or SnapshotRepository()
        snapshots = repo.list_snapshots() # sorted dates

        # Milestones definition
        milestones = [
            {"id": "mr3", "name": "MR3", "check": lambda p: p.mastery_rank >= 3, "desc": "Mastery Rank 3 achieved. Early weapon restrictions unlocked."},
            {"id": "second_dream", "name": "Second Dream", "check": lambda p: "the second dream" in {q.lower() for q in p.completed_quests}, "desc": "The Second Dream quest completed. Transference unlocked."},
            {"id": "war_within", "name": "War Within", "check": lambda p: "the war within" in {q.lower() for q in p.completed_quests}, "desc": "The War Within quest completed. Full Operator capabilities unlocked."},
            {"id": "new_war", "name": "The New War", "check": lambda p: "the new war" in {q.lower() for q in p.completed_quests}, "desc": "The New War quest completed. Sentient Bow and Zariman access unlocked."},
            {"id": "steel_path", "name": "Steel Path", "check": lambda p: p.steel_path_unlocked, "desc": "Steel Path difficulty unlocked. Acolyte Arcanes farm accessible."},
            {"id": "archons", "name": "Archons", "check": lambda p: "the new war" in {q.lower() for q in p.completed_quests} and p.steel_path_unlocked and p.mastery_rank >= 5, "desc": "Archon Hunts unlocked. Crimson, Azure, and Amber Archon Shards farm accessible."}
        ]

        timeline = []
        
        # We find the earliest snapshot date for each milestone
        for ms in milestones:
            unlocked_date = None
            
            # Check snapshots first
            for date_str in snapshots:
                snap_player = repo.restore_snapshot(date_str)
                if snap_player and ms["check"](snap_player):
                    unlocked_date = date_str
                    break
            
            # Fallback to current player state if not found in snapshots but unlocked now
            status = "locked"
            if ms["check"](player):
                status = "unlocked"
                if not unlocked_date:
                    unlocked_date = "Active (No history)"
            
            timeline.append({
                "name": ms["name"],
                "status": status,
                "date_unlocked": unlocked_date or "Pending",
                "description": ms["desc"]
            })
            
        return timeline

    def calculate_progression_speed(self, timeline: list[dict[str, Any]]) -> str:
        """Calculates days elapsed between milestones as a speed indicator."""
        unlocked = [t for t in timeline if t["status"] == "unlocked" and t["date_unlocked"] not in ["Pending", "Active (No history)"]]
        if len(unlocked) < 2:
            return "Insufficient snapshot history to calculate velocity."
            
        from datetime import datetime
        try:
            dates = [datetime.strptime(t["date_unlocked"], "%Y-%m-%d") for t in unlocked]
            delta = max(dates) - min(dates)
            days = delta.days
            return f"Unlocked {len(unlocked)} major milestones over {days} days ({round(days / len(unlocked), 1)} days per milestone average)."
        except Exception:
            return "Active profile speed tracking enabled."
