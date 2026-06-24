from __future__ import annotations
from typing import Any
from src.core.snapshot_repository import SnapshotRepository
from src.core.progression_engine import ProgressionEngine

class HistoryEngine:
    """Compiles growth trends (MR, daily quest activity, relic unlocks, build crafting count) from historical snapshots."""
    
    def __init__(self, repo: SnapshotRepository | None = None) -> None:
        self.repo = repo or SnapshotRepository()
        self.pe = ProgressionEngine()

    def get_growth_trends(self) -> dict[str, list[dict[str, Any]]]:
        """
        Compiles trends over all available snapshots.
        Returns a dictionary of metrics lists, where each list item has {"date": str, "value": float/int}.
        """
        dates = self.repo.list_snapshots()
        
        mr_trend = []
        quest_activity = []
        relic_unlocks = []
        build_crafting = []
        
        prev_quests = set()
        prev_weapons = set()
        prev_mods = set()
        prev_arcanes = set()
        
        for date_str in dates:
            snap = self.repo.get_snapshot(date_str)
            if not snap or "player" not in snap:
                continue
            
            pdata = snap["player"]
            
            # 1. MR
            mr = pdata.get("mastery_rank", 1)
            mr_trend.append({"date": date_str, "value": mr})
            
            # 2. Daily quest activity (difference in completed quests count)
            quests = set(pdata.get("completed_quests", []))
            new_quests = len(quests - prev_quests) if prev_quests else len(quests)
            quest_activity.append({"date": date_str, "value": new_quests})
            prev_quests = quests
            
            # 3. Relic unlocks (derived from changes in owned_weapons / owned_arcanes)
            weapons = set(pdata.get("owned_weapons", []))
            arcanes = set(pdata.get("owned_arcanes", []))
            new_unlocks = len(weapons - prev_weapons) + len(arcanes - prev_arcanes)
            if not prev_weapons and not prev_arcanes:
                new_unlocks = len(weapons) + len(arcanes)
            relic_unlocks.append({"date": date_str, "value": new_unlocks})
            prev_weapons = weapons
            prev_arcanes = arcanes
            
            # 4. Build crafting count (derived from changes in owned_mods)
            mods = set(pdata.get("owned_mods", []))
            new_mods = len(mods - prev_mods) if prev_mods else len(mods)
            build_crafting.append({"date": date_str, "value": new_mods})
            prev_mods = mods
            
        return {
            "mr": mr_trend,
            "quest_activity": quest_activity,
            "relic_unlocks": relic_unlocks,
            "build_crafting": build_crafting
        }
