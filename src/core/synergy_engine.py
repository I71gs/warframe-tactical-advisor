from __future__ import annotations
from typing import Any

class SynergyEngine:
    """Evaluates combat synergies between Warframes, weapons, arcanes, and mods."""

    def evaluate_synergy(
        self,
        warframe: str,
        primary: str,
        secondary: str,
        arcanes: list[str],
        mods: list[str]
    ) -> dict[str, Any]:
        wf = warframe.strip().lower()
        prim = primary.strip().lower()
        sec = secondary.strip().lower()
        arcs = {a.strip().lower() for a in arcanes}
        ms = {m.strip().lower() for m in mods}

        score = 50 # Baseline average
        reasons = []

        # 1. Warframe + Primary weapon synergies
        if wf in ("wisp", "harrow", "gauss") and prim in ("phenmor", "laetum", "felarx", "burston incarnon", "latron incarnon"):
            score += 25
            reasons.append(f"Excellent fire rate / attack speed synergy: {warframe} buffs accelerate Incarnon charging.")
        elif wf in ("saryn", "mirage") and prim in ("torid", "kuva bramma"):
            score += 25
            reasons.append(f"Excellent AOE/chaining synergy: {warframe}'s abilities spread status/damage clones extremely effectively with {primary}.")
        elif wf == "mesa" and sec == "kuva nukor":
            score += 15
            reasons.append("Good secondary primer synergy: Kuva Nukor applies multiple status indicators rapidly.")
        elif wf == "rhino" and prim == "nataruk":
            score += 5
            reasons.append("Rhino Roar provides direct multipliers, but has average combat utility with Nataruk.")
        else:
            reasons.append("Standard combat synergy between Warframe and weapon types.")

        # 2. Arcane + Weapon synergies
        if "primary merciless" in arcs and prim:
            score += 15
            reasons.append(f"Primary Merciless matches primary weapon: Stacks base damage on weapon kills.")
        if "secondary merciless" in arcs and sec:
            score += 15
            reasons.append(f"Secondary Merciless matches secondary weapon: Stacks secondary base damage.")
            
        # 3. Mod synergies
        if "galvanized chamber" in ms and "primary merciless" in arcs:
            score += 10
            reasons.append("Galvanized multishot scales cleanly with Merciless base damage stacks.")
        elif "galvanized chamber" in ms and not arcs:
            score -= 5
            reasons.append("Galvanized Chamber is highly optimized but lacks a matching primary arcane (e.g., Primary Merciless).")

        # Cap score
        score = min(max(score, 10), 100)

        # Classify rating
        if score >= 85:
            rating = "Excellent"
        elif score >= 70:
            rating = "Good"
        elif score >= 45:
            rating = "Average"
        else:
            rating = "Poor"

        return {
            "score": score,
            "rating": rating,
            "reasons": reasons
        }
