from __future__ import annotations
from typing import Any
from src.models.player import Player

def check_builds(player: Player) -> list[dict[str, Any]]:
    """Evaluates missing meta mods and arcanes inside player inventory."""
    rules_applied = []
    owned_mods = {m.lower() for m in player.owned_mods}
    owned_arcanes = {a.lower() for a in player.owned_arcanes}
    
    # Rule 1: Galvanized Chamber
    if "galvanized chamber" not in owned_mods:
        rules_applied.append({
            "rule_name": "Galvanized Chamber Upgrade",
            "condition": "Missing Galvanized Chamber mod",
            "task": "Acquire 'Galvanized Chamber' mod from Arbitrations",
            "eta": "2-3 hours",
            "power_gain": "+50% Multishot on kill (Stacking)",
            "prerequisites": "Arbitrations unlocked, 20x Vitus Essence",
            "follow_up": "Max level the mod using Endo and Credits."
        })
        
    # Rule 2: Galvanized Aptitude
    if "galvanized aptitude" not in owned_mods:
        rules_applied.append({
            "rule_name": "Galvanized Aptitude Upgrade",
            "condition": "Missing Galvanized Aptitude mod",
            "task": "Acquire 'Galvanized Aptitude' mod from Arbitrations",
            "eta": "2-3 hours",
            "power_gain": "+40% Direct damage scaling per status stack",
            "prerequisites": "Arbitrations unlocked, 20x Vitus Essence",
            "follow_up": "Fit status weapon builds to maximize multiplier."
        })

    # Rule 3: Primary Merciless
    if "primary merciless" not in owned_arcanes:
        rules_applied.append({
            "rule_name": "Primary Merciless Arcane",
            "condition": "Missing Primary Merciless arcane",
            "task": "Farm Steel Path Acolytes for Primary Merciless",
            "eta": "3-5 hours",
            "power_gain": "+30% Damage on kill (Max 12 stacks, +360% total)",
            "prerequisites": "Steel Path unlocked",
            "follow_up": "Forma primary weapons to fit Arcane Adapter."
        })
        
    return rules_applied
