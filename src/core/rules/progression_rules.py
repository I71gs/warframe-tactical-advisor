from __future__ import annotations
from typing import Any
from src.models.player import Player

def check_progression(player: Player) -> list[dict[str, Any]]:
    """Evaluates player's quest and star chart milestones."""
    rules_applied = []
    completed = {q.lower() for q in player.completed_quests}
    
    # Rule 1: Second Dream
    if "the second dream" not in completed:
        rules_applied.append({
            "rule_name": "Second Dream Quest",
            "condition": "Second Dream not completed",
            "task": "Complete 'The Second Dream' quest",
            "eta": "1-2 hours",
            "power_gain": "+15% (Unlocks Focus Trees & Operator)",
            "prerequisites": "Complete Natah Quest & Uranus Junction",
            "follow_up": "Progress to 'The War Within' quest."
        })
        
    # Rule 2: The New War
    elif "the new war" not in completed:
        rules_applied.append({
            "rule_name": "New War Quest",
            "condition": "New War not completed",
            "task": "Complete 'The New War' quest",
            "eta": "4-6 hours",
            "power_gain": "+35% (Unlocks Zariman, Nataruk, Archon Hunts)",
            "prerequisites": "Own a Railjack and Necramech",
            "follow_up": "Access Angels of Zariman content."
        })
        
    # Rule 3: Arbitrations
    elif not player.arbitrations_unlocked:
        rules_applied.append({
            "rule_name": "Arbitrations Unlock",
            "condition": "Arbitrations locked but New War completed",
            "task": "Unlock Arbitrations by clearing all Star Chart nodes",
            "eta": "4-10 hours",
            "power_gain": "+45% (Unlocks Galvanized Mods, Grendel locs)",
            "prerequisites": "Clear all 240+ default nodes",
            "follow_up": "Farm Vitus Essence to buy Galvanized Chamber."
        })
        
    # Rule 4: Steel Path
    elif not player.steel_path_unlocked:
        rules_applied.append({
            "rule_name": "Steel Path Unlock",
            "condition": "Steel Path locked but Arbitrations unlocked",
            "task": "Unlock Steel Path: Talk to Teshin at any Relay",
            "eta": "15 mins",
            "power_gain": "+55% (Unlocks Acolyte Arcanes, Weapon Adapters)",
            "prerequisites": "Complete normal Star Chart nodes",
            "follow_up": "Farm SP incursions to build Primary Merciless."
        })
        
    return rules_applied
