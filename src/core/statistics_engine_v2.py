from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine
from src.core.snapshot_repository import SnapshotRepository
from src.core.weapon_database import WEAPONS

class StatisticsEngineV2:
    """Compiles historical growth curves, story/weapon clearance stats, and mod/build scores."""

    def __init__(self, repo: SnapshotRepository | None = None) -> None:
        self.repo = repo or SnapshotRepository()
        self.pe = ProgressionEngine()

    def get_growth_data(self, player: Player) -> list[dict[str, Any]]:
        """Compiles historical readiness scores across all saved snapshots."""
        growth = []
        snapshots = self.repo.list_snapshots()
        for date_str in snapshots:
            snap_player = self.repo.restore_snapshot(date_str)
            if snap_player:
                growth.append({
                    "date": date_str,
                    "readiness": self.pe.get_readiness_score(snap_player),
                    "story": self.pe.get_story_score(snap_player),
                    "mods": self.pe.get_mod_score(snap_player),
                    "weapons": self.pe.get_weapon_score(snap_player),
                    "mastery": self.pe.get_mastery_score(snap_player),
                    "builds": self.pe.get_build_score(snap_player)
                })
        
        # Add current state if not already present
        from datetime import date
        today_str = str(date.today())
        if not any(g["date"] == today_str for g in growth):
            growth.append({
                "date": today_str,
                "readiness": self.pe.get_readiness_score(player),
                "story": self.pe.get_story_score(player),
                "mods": self.pe.get_mod_score(player),
                "weapons": self.pe.get_weapon_score(player),
                "mastery": self.pe.get_mastery_score(player),
                "builds": self.pe.get_build_score(player)
            })
        return growth

    def get_clearance_statistics(self, player: Player) -> dict[str, Any]:
        """Compiles story and weapon clearance ratios."""
        from src.core.quest_graph import QuestGraph
        graph = QuestGraph()
        total_quests = len(graph.dependencies)
        completed_quests = len([q for q in player.completed_quests if q in graph.dependencies])
        
        owned_weapons = {w.lower() for w in player.owned_weapons}
        total_weapons = len(WEAPONS)
        owned_weapons_count = sum(1 for w in WEAPONS if w["name"].lower() in owned_weapons)
        
        return {
            "quests_total": total_quests,
            "quests_completed": completed_quests,
            "quests_ratio": round(completed_quests / total_quests if total_quests else 0.0, 3),
            "weapons_total": total_weapons,
            "weapons_owned": owned_weapons_count,
            "weapons_ratio": round(owned_weapons_count / total_weapons if total_weapons else 0.0, 3)
        }

    def get_scores_breakdown(self, player: Player) -> dict[str, float]:
        """Compiles mod and build sub-scores."""
        return {
            "story": self.pe.get_story_score(player),
            "mods": self.pe.get_mod_score(player),
            "arcanes": self.pe.get_arcane_score(player),
            "weapons": self.pe.get_weapon_score(player),
            "mastery": self.pe.get_mastery_score(player),
            "unlocks": self.pe.get_unlock_score(player),
            "builds": self.pe.get_build_score(player),
            "readiness": self.pe.get_readiness_score(player)
        }
