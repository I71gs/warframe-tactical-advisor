from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DUVIRI_STATE_PATH = ROOT / 'duviri_state.json'

class DuviriEngine:
    """Manages player tracking for Duviri Intrinsics, Pathos Clamps, and upgrade timelines."""

    def __init__(self, state_path: Path | str | None = None) -> None:
        self.state_path = Path(state_path) if state_path else DUVIRI_STATE_PATH

    def load_duviri_state(self) -> dict[str, Any]:
        default_state = {
            "intrinsics": {
                "Combat": 1,
                "Riding": 1,
                "Opportunity": 1,
                "Endurance": 1
            },
            "pathos_clamps_owned": 0
        }
        if not self.state_path.exists():
            return default_state
            
        try:
            with open(self.state_path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                if isinstance(data, dict):
                    # Merge keys to ensure compatibility
                    for k, v in data.items():
                        default_state[k] = v
        except Exception:
            pass
        return default_state

    def save_duviri_state(self, state: dict[str, Any]) -> None:
        try:
            with open(self.state_path, 'w', encoding='utf-8') as fh:
                json.dump(state, fh, indent=4)
        except Exception:
            pass

    def get_progress_percentage(self, state: dict[str, Any]) -> float:
        intrinsics = state.get("intrinsics", {})
        total_nodes = 40  # 4 categories * 10 levels each
        allocated_ranks = sum(min(10, int(v)) for v in intrinsics.values())
        return round((allocated_ranks / total_nodes) * 100, 1)

    def get_recommendations(self, state: dict[str, Any]) -> list[str]:
        intrinsics = state.get("intrinsics", {})
        recs = []
        
        # Priority checks
        opp = intrinsics.get("Opportunity", 1)
        if opp < 4:
            recs.append("Upgrade 'Opportunity' to Rank 4 (adds extra Warframe selection options in Teshin's Cave).")
        
        endur = intrinsics.get("Endurance", 1)
        if endur < 3:
            recs.append("Upgrade 'Endurance' to Rank 3 (+25% extra Health in Duviri).")
            
        combat = intrinsics.get("Combat", 1)
        if combat < 6:
            recs.append("Upgrade 'Combat' to Rank 6 (+50% Melee Damage boost).")
            
        if opp < 10:
            recs.append("Aim for 'Opportunity' Rank 10 to unlock direct merchant trade selections.")
            
        if len(recs) < 3:
            recs.append("Collect Pathos Clamps from Orowyrm boss fights to buy weapon adapters.")
            
        return recs[:3]
export_duviri = DuviriEngine()
