from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, date
from typing import Any
from src.utils.logger import logger

ROOT = Path(__file__).resolve().parents[2]
LOGS_FILE = ROOT / "snapshots" / "session_logs.json"

class SessionAnalytics:
    """Aggregates daily productivity logs: session durations, efficiency, and resource yields."""

    def __init__(self, logs_filepath: Path | str | None = None) -> None:
        self.filepath = Path(logs_filepath) if logs_filepath else LOGS_FILE
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def load_logs(self) -> list[dict[str, Any]]:
        """Load session logs from the local JSON file."""
        if not self.filepath.exists():
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Failed to load session logs: %s", e)
            return []

    def save_logs(self, logs: list[dict[str, Any]]) -> None:
        """Save session logs to the local JSON file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=4)
        except Exception as e:
            logger.error("Failed to save session logs: %s", e)

    def log_session(self, duration_minutes: int, tasks_completed: int, tasks_total: int, resources: dict[str, int]) -> dict[str, Any]:
        """Logs a new session activity and returns the session details."""
        logs = self.load_logs()
        
        # Calculate efficiency: percentage of completed tasks relative to total tasks
        efficiency = round(tasks_completed / tasks_total * 100.0, 1) if tasks_total > 0 else 100.0
        
        session_record = {
            "timestamp": datetime.now().isoformat(),
            "date": str(date.today()),
            "duration": duration_minutes,
            "tasks_completed": tasks_completed,
            "tasks_total": tasks_total,
            "efficiency": efficiency,
            "resources": resources
        }
        
        logs.append(session_record)
        self.save_logs(logs)
        return session_record

    def get_daily_productivity(self) -> dict[str, Any]:
        """Aggregates session records for the current day."""
        today_str = str(date.today())
        logs = self.load_logs()
        
        today_logs = [log for log in logs if log.get("date") == today_str]
        
        total_duration = sum(log["duration"] for log in today_logs)
        total_completed = sum(log["tasks_completed"] for log in today_logs)
        total_tasks = sum(log["tasks_total"] for log in today_logs)
        
        avg_efficiency = 0.0
        if today_logs:
            avg_efficiency = round(sum(log["efficiency"] for log in today_logs) / len(today_logs), 1)
            
        aggregated_resources = {}
        for log in today_logs:
            for r, val in log.get("resources", {}).items():
                aggregated_resources[r] = aggregated_resources.get(r, 0) + val
                
        return {
            "date": today_str,
            "sessions_count": len(today_logs),
            "total_duration_minutes": total_duration,
            "total_tasks_completed": total_completed,
            "total_tasks": total_tasks,
            "average_efficiency": avg_efficiency,
            "resources_collected": aggregated_resources
        }

    def get_historical_efficiency(self) -> list[dict[str, Any]]:
        """Compiles history of efficiency ratings over time."""
        logs = self.load_logs()
        # Group by date
        daily_stats = {}
        for log in logs:
            d = log["date"]
            if d not in daily_stats:
                daily_stats[d] = []
            daily_stats[d].append(log["efficiency"])
            
        history = []
        for d, effs in sorted(daily_stats.items()):
            history.append({
                "date": d,
                "average_efficiency": round(sum(effs) / len(effs), 1)
            })
        return history
