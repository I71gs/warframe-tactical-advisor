from __future__ import annotations
from typing import Any
from datetime import datetime, date
from src.models.player import Player
from src.core.goal_planner import GoalPlanner
from src.core.goal_cost_engine import GoalCostEngine
from src.core.snapshot_repository import SnapshotRepository

class GoalHistoryEngine:
    """Tracks target goal achievements, dates, completion times, and power ratings."""

    def __init__(self, repo: SnapshotRepository | None = None) -> None:
        self.repo = repo or SnapshotRepository()
        self.planner = GoalPlanner()
        self.cost_engine = GoalCostEngine()

    def get_goal_history(self, player: Player) -> list[dict[str, Any]]:
        """Scans goals and compiles complete history and status for each goal."""
        goals = ["Unlock Steel Path", "Become Archon Ready", "Reach Endgame", "Finish Main Story"]
        history = []
        snapshots = self.repo.list_snapshots()

        for goal in goals:
            current_plan = self.planner.get_goal_plan(player, goal)
            is_completed = all(step["completed"] for step in current_plan)
            
            # Find earliest date completed across snapshots
            completion_date = None
            if is_completed:
                # Walk snapshots in chronological order
                for date_str in snapshots:
                    snap_player = self.repo.restore_snapshot(date_str)
                    if snap_player:
                        snap_plan = self.planner.get_goal_plan(snap_player, goal)
                        if all(step["completed"] for step in snap_plan):
                            completion_date = date_str
                            break
                if not completion_date:
                    completion_date = "Active (No history)"

            # Cost and power details
            cost_details = self.cost_engine.calculate_cost(player, goal)
            
            # Try to convert power gain string to numeric value (power rating)
            power_rating = 0.0
            try:
                # e.g., "+35% Readiness Score" or similar
                gain_str = cost_details.get("power_gain", "0")
                digits = "".join(c for c in gain_str if c.isdigit() or c == '.')
                if digits:
                    power_rating = float(digits)
            except Exception:
                pass

            history.append({
                "goal": goal,
                "completed": is_completed,
                "date_completed": completion_date or "Pending",
                "time_required": cost_details.get("time", "Unknown"),
                "difficulty": cost_details.get("difficulty", "Medium"),
                "power_rating": power_rating,
                "power_gain_desc": cost_details.get("power_gain", "N/A"),
                "steps_total": len(current_plan),
                "steps_completed": sum(1 for s in current_plan if s["completed"])
            })

        return history
