from __future__ import annotations
from typing import Any
from src.core.synergy_database import SynergyDatabase

class TeamSynergyEngine:
    """Evaluates loadout configurations for combat synergies and lists strengths/weaknesses."""

    def __init__(self) -> None:
        self.db = SynergyDatabase()

    def evaluate_composition(self, warframe: str, primary: str, secondary: str, melee: str) -> dict[str, Any]:
        """Calculates synergy score and analyzes strengths/weaknesses of the loadout."""
        wf = warframe.strip()
        prim = primary.strip()
        sec = secondary.strip()
        mel = melee.strip()

        # Retrieve individual weapon synergies
        syn_primary = self.db.get_synergy(wf, prim)
        syn_secondary = self.db.get_synergy(wf, sec)

        # Base score is the average of primary and secondary synergies, plus minor melee adjustment
        base_score = (syn_primary["score"] + syn_secondary["score"]) / 2
        
        # Melee adjustments (e.g. Praedos gets a Zariman bonus, Glaive Prime gets a high rating)
        melee_bonus = 0
        melee_desc = "Standard melee."
        if mel.lower() == "praedos":
            melee_bonus = 5
            melee_desc = "Praedos utility passive speed synergizes with run-and-gun playstyles."
        elif mel.lower() == "glaive prime":
            melee_bonus = 7
            melee_desc = "Glaive Prime forced slash procs offer top-tier heavy attack scaling."

        final_score = min(100.0, base_score + melee_bonus)
        
        # Rating levels
        if final_score >= 90:
            rating = "Excellent"
        elif final_score >= 75:
            rating = "Good"
        elif final_score >= 60:
            rating = "Average"
        else:
            rating = "Poor"

        # Determine Strengths and Weaknesses
        strengths = []
        weaknesses = []

        if syn_primary["rating"] == "Excellent" or syn_secondary["rating"] == "Excellent":
            strengths.append("High specialized ability scaling.")
        else:
            strengths.append("Decent multi-purpose versatility.")

        if final_score >= 90:
            strengths.append("Extreme burst damage potential.")
            strengths.append("Optimized reload and speed utility.")
            weaknesses.append("Energy dependent (ability reliant).")
            weaknesses.append("Requires active upkeep of buffs.")
        else:
            strengths.append("Reliable defensive baseline.")
            weaknesses.append("Lacks specialized status/crit multipliers.")
            weaknesses.append("Sub-optimal clearing speeds for Steel Path.")

        if melee_bonus > 0:
            strengths.append(f"Melee Utility: {melee_desc}")
            
        return {
            "score": round(final_score, 1),
            "rating": rating,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "primary_rationale": syn_primary["rationale"],
            "secondary_rationale": syn_secondary["rationale"]
        }
