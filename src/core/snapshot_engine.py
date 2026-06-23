from __future__ import annotations
import time
from datetime import date
from typing import Any
from src.core.cache_manager import CacheManager
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine

class SnapshotEngine:
    """Manages recording, loading, and structuring historical snapshots of account progression."""

    def __init__(self) -> None:
        self.cm = CacheManager()
        self.pe = ProgressionEngine()

    def get_snapshots(self) -> list[dict[str, Any]]:
        """Load and return all snapshots sorted by timestamp ascending."""
        history = self.cm.load_cache("history").get("data", {})
        snapshots = history.get("snapshots", [])
        return sorted(snapshots, key=lambda s: s.get("timestamp", 0))

    def record_snapshot(self, player: Player) -> dict[str, Any] | None:
        """Create a daily progression log containing core scoring metrics."""
        history = self.cm.load_cache("history")
        history_data = history.get("data", {})
        
        today_str = str(date.today())
        snapshots = history_data.get("snapshots", [])
        
        # Avoid duplicates on the same calendar day
        for s in snapshots:
            if s.get("date") == today_str:
                return s
                
        snapshot = {
            "timestamp": time.time(),
            "date": today_str,
            "readiness": self.pe.get_readiness_score(player),
            "story": self.pe.get_story_score(player),
            "mods": self.pe.get_mod_score(player),
            "arcanes": self.pe.get_arcane_score(player),
            "weapons": self.pe.get_weapon_score(player),
            "build_score": self.pe.get_build_score(player),
            "mr": player.mastery_rank
        }
        
        snapshots.append(snapshot)
        history_data["snapshots"] = snapshots
        self.cm.save_cache("history", history_data)
        return snapshot

    def clear_history(self) -> None:
        """Wipes the history snapshots cache completely."""
        self.cm.clear_cache("history")
