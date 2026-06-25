from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Any
from src.models.player import Player
from src.utils.logger import logger

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOTS_DIR = ROOT / "snapshots"

class SnapshotRepository:
    """Manages profile state saves, restores, and comparisons over historical date records."""

    def __init__(self, snapshots_dir: Path | str | None = None) -> None:
        self.snapshots_dir = Path(snapshots_dir) if snapshots_dir else SNAPSHOTS_DIR
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def save_snapshot(self, player: Player, date_str: str | None = None) -> Path:
        """Saves player state representation into YYYY-MM-DD.json format."""
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        filepath = self.snapshots_dir / f"{date_str}.json"
        
        state = {
            "metadata": {
                "date": date_str,
                "timestamp": datetime.now().isoformat(),
                "app_version": "8.0.0"
            },
            "player": {
                "mastery_rank": player.mastery_rank,
                "completed_quests": player.completed_quests,
                "owned_mods": player.owned_mods,
                "owned_arcanes": player.owned_arcanes,
                "owned_weapons": player.owned_weapons,
                "steel_path_unlocked": player.steel_path_unlocked,
                "arbitrations_unlocked": player.arbitrations_unlocked,
                "helminth_unlocked": player.helminth_unlocked
            }
        }
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
            logger.info("Saved progress snapshot for date: %s", date_str)
        except Exception as e:
            logger.error("Failed to save snapshot file %s: %s", filepath.name, e)
            
        return filepath

    def get_snapshot(self, date_str: str) -> dict[str, Any] | None:
        """Retrieves raw JSON state for a given date."""
        filepath = self.snapshots_dir / f"{date_str}.json"
        if not filepath.exists():
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Failed to load snapshot file %s: %s", filepath.name, e)
            return None

    def list_snapshots(self) -> list[str]:
        """Returns sorted list of available date strings."""
        files = self.snapshots_dir.glob("*.json")
        dates = [f.stem for f in files]
        return sorted(dates)

    def restore_snapshot(self, date_str: str) -> Player | None:
        """Converts date snapshot back into a Player profile model."""
        data = self.get_snapshot(date_str)
        if not data or "player" not in data:
            return None
        pdata = data["player"]
        return Player(
            mastery_rank=pdata.get("mastery_rank", 1),
            completed_quests=pdata.get("completed_quests", []),
            owned_mods=pdata.get("owned_mods", []),
            owned_arcanes=pdata.get("owned_arcanes", []),
            owned_weapons=pdata.get("owned_weapons", []),
            steel_path_unlocked=bool(pdata.get("steel_path_unlocked", False)),
            arbitrations_unlocked=bool(pdata.get("arbitrations_unlocked", False)),
            helminth_unlocked=bool(pdata.get("helminth_unlocked", False))
        )

    def compare_snapshots(self, date1: str, date2: str) -> dict[str, Any] | None:
        """Computes diff analysis details comparing two snapshots."""
        snap1 = self.get_snapshot(date1)
        snap2 = self.get_snapshot(date2)
        if not snap1 or not snap2:
            return None
            
        p1 = snap1["player"]
        p2 = snap2["player"]
        
        # Calculate changes from snap1 to snap2
        mr_diff = p2.get("mastery_rank", 1) - p1.get("mastery_rank", 1)
        
        # Quests diff
        q1 = set(p1.get("completed_quests", []))
        q2 = set(p2.get("completed_quests", []))
        quests_added = list(q2 - q1)
        quests_removed = list(q1 - q2)
        
        # Weapons diff
        w1 = set(p1.get("owned_weapons", []))
        w2 = set(p2.get("owned_weapons", []))
        weapons_added = list(w2 - w1)
        weapons_removed = list(w1 - w2)

        # Mods diff
        m1 = set(p1.get("owned_mods", []))
        m2 = set(p2.get("owned_mods", []))
        mods_added = list(m2 - m1)
        mods_removed = list(m1 - m2)

        # Arcanes diff
        a1 = set(p1.get("owned_arcanes", []))
        a2 = set(p2.get("owned_arcanes", []))
        arcanes_added = list(a2 - a1)
        arcanes_removed = list(a1 - a2)

        return {
            "mastery_rank_change": mr_diff,
            "quests": {"added": quests_added, "removed": quests_removed},
            "weapons": {"added": weapons_added, "removed": weapons_removed},
            "mods": {"added": mods_added, "removed": mods_removed},
            "arcanes": {"added": arcanes_added, "removed": arcanes_removed}
        }
