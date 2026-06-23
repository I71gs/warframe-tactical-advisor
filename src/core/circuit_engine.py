from __future__ import annotations
from datetime import date
from typing import Any
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine

ROTATIONS = {
    0: ["Braton Incarnon", "Paris Incarnon", "Kunai Incarnon", "Skana Incarnon"],
    1: ["Latron Incarnon", "Furis Incarnon", "Furax Incarnon", "Strun Incarnon"],
    2: ["Lex Incarnon", "Magistar Incarnon", "Boltor Incarnon", "Bronco Incarnon", "Ceramic Dagger Incarnon"],
    3: ["Torid Incarnon", "Dual Toxocyst Incarnon", "Dual Cestra Incarnon", "Miter Incarnon"],
    4: ["Burston Incarnon", "Dread Incarnon", "Despair Incarnon", "Hate Incarnon"]
}

class CircuitEngine:
    """Calculates weekly Circuit rotation cycles and recommends optimal rewards."""

    def get_weekly_rotation(self) -> dict[str, Any]:
        year, week, _ = date.today().isocalendar()
        rot_idx = week % 5
        return {
            "week_label": f"Week {rot_idx + 1} Rotation",
            "items": ROTATIONS[rot_idx]
        }

    def get_circuit_recommendation(self, player: Player) -> dict[str, Any]:
        rot = self.get_weekly_rotation()
        owned_weapons = {w.lower() for w in player.owned_weapons}
        
        # Primary focus: recommend item from rotation that the player is missing
        recommendation = None
        priority = "LOW"
        
        # Priority mapping of rotation items
        meta_weights = {
            "torid incarnon": "CRITICAL",
            "latron incarnon": "HIGH",
            "lex incarnon": "HIGH",
            "burston incarnon": "HIGH",
            "strun incarnon": "MEDIUM"
        }
        
        for item in rot["items"]:
            # Check if name without " Incarnon" is owned
            name_base = item.replace(" Incarnon", "").lower()
            if name_base not in owned_weapons:
                rec_priority = meta_weights.get(item.lower(), "MEDIUM")
                if recommendation is None or priority == "LOW" or (rec_priority in ["CRITICAL", "HIGH"] and priority != "CRITICAL"):
                    recommendation = item
                    priority = rec_priority
                    
        if not recommendation:
            recommendation = rot["items"][0]
            priority = "LOW"
            
        # Circuit Readiness
        pe = ProgressionEngine()
        readiness_rating = 0.0
        readiness_status = "Locked"
        
        if player.steel_path_unlocked:
            # Average score based on Mods, Arcanes, and Builds scores
            readiness_rating = round((pe.get_mod_score(player) + pe.get_arcane_score(player) + pe.get_build_score(player)) / 3, 1)
            if readiness_rating >= 80.0:
                readiness_status = "Fully Prepared"
            elif readiness_rating >= 50.0:
                readiness_status = "Moderate Preparedness"
            else:
                readiness_status = "Underprepared"
        else:
            readiness_status = "Locked (Requires Steel Path)"

        return {
            "week": rot["week_label"],
            "rotation_items": rot["items"],
            "recommended_pick": recommendation,
            "priority": priority,
            "readiness_score": readiness_rating,
            "readiness_status": readiness_status
        }
