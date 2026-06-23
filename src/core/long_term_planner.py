from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine

ROOT = Path(__file__).resolve().parents[2]
TIMELINE_STATE_PATH = ROOT / 'timeline_state.json'

class LongTermPlanner:
    """Manages player progression milestones, providing a 30-day roadmap view."""

    def __init__(self, state_path: Path | str | None = None) -> None:
        self.state_path = Path(state_path) if state_path else TIMELINE_STATE_PATH

    def get_timeline_state(self, player: Player) -> dict[str, Any]:
        """Calculates milestones, maps player's current progression position, and returns the plan."""
        pe = ProgressionEngine()
        stage = pe.determine_stage(player)
        
        milestones = [
            {"id": "story", "label": "The New War Complete", "description": "Finish the main cinematic story arc."},
            {"id": "arbitrations", "label": "Arbitrations Unlocked", "description": "Clear all nodes on the normal Star Chart."},
            {"id": "steel_path", "label": "Steel Path Access", "description": "Unlock Steel Path difficulty and Acolyte farming."},
            {"id": "archons", "label": "Archon Hunts Ready", "description": "Equip high-meta weapons and reach MR12+."},
            {"id": "endgame", "label": "Endgame Optimization", "description": "Acquire Zariman Incarnons, complete builds, and max out power."}
        ]

        # Determine current active milestone index
        current_idx = 0
        target_milestone = milestones[0]
        est_days = 30
        
        completed_quests = {q.lower() for q in player.completed_quests}
        
        if "the new war" in completed_quests:
            current_idx = 1
            target_milestone = milestones[1]
            est_days = 20
        if player.arbitrations_unlocked:
            current_idx = 2
            target_milestone = milestones[2]
            est_days = 15
        if player.steel_path_unlocked:
            current_idx = 3
            target_milestone = milestones[3]
            est_days = 10
        if player.mastery_rank >= 12 and "primary merciless" in {a.lower() for a in player.owned_arcanes}:
            current_idx = 4
            target_milestone = milestones[4]
            est_days = 5
        if current_idx == 4 and len(player.owned_weapons) >= 5: # check meta build completion
            current_idx = 5
            target_milestone = {"id": "max", "label": "Fully Optimized", "description": "Maxed out build optimization."}
            est_days = 0

        # Calculate remaining requirements for the target milestone
        remaining_reqs = []
        if current_idx == 0:
            if "the war within" not in completed_quests: remaining_reqs.append("Complete quest: The War Within")
            if "the sacrifice" not in completed_quests: remaining_reqs.append("Complete quest: The Sacrifice")
            if "the new war" not in completed_quests: remaining_reqs.append("Complete quest: The New War")
        elif current_idx == 1:
            remaining_reqs.append("Clear all remaining Star Chart nodes to access Arbitrations")
        elif current_idx == 2:
            remaining_reqs.append("Talk to Teshin at any relay to unlock Steel Path")
        elif current_idx == 3:
            if player.mastery_rank < 12: remaining_reqs.append("Reach Mastery Rank 12")
            if "primary merciless" not in {a.lower() for a in player.owned_arcanes}: remaining_reqs.append("Acquire Primary Merciless arcane")
        elif current_idx == 4:
            remaining_reqs.append("Farm Cavalero on Zariman for Phenmor / Laetum")
            remaining_reqs.append("Optimize weapon build scores to 95%")

        payload = {
            "current_stage": stage.upper().replace("_", " "),
            "current_index": current_idx,
            "target_milestone": target_milestone["label"],
            "estimated_time": f"{est_days} days" if est_days > 0 else "Fully Optimized",
            "requirements_remaining": remaining_reqs,
            "milestones": milestones
        }

        self._save_state(payload)
        return payload

    def _save_state(self, state_data: dict[str, Any]) -> None:
        try:
            with open(self.state_path, 'w', encoding='utf-8') as fh:
                json.dump(state_data, fh, indent=4)
        except Exception:
            pass
