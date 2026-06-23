from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.resource_engine import ResourceEngine

def check_resources(player: Player) -> list[dict[str, Any]]:
    """Evaluates resource stockpile targets and generates optimization tasks."""
    rules_applied = []
    
    # Load owned resources using ResourceEngine
    re = ResourceEngine()
    owned = re.load_owned_resources()
    
    # Rule 1: Voidplumes
    if owned.get("Voidplumes", 0) < 15:
        rules_applied.append({
            "rule_name": "Voidplumes Harvesting",
            "condition": "Voidplumes count is low (< 15)",
            "task": "Farm Voidplumes on Zariman Bounties",
            "eta": "1-2 hours",
            "power_gain": "+25% (Acquire evolving Zariman primary weapons)",
            "prerequisites": "Angels of Zariman completed",
            "follow_up": "Deliver to Cavalero to upgrade Standing."
        })
        
    # Rule 2: Entrati Lanthorns
    if owned.get("Entrati Lanthorn", 0) < 8:
        rules_applied.append({
            "rule_name": "Entrati Lanthorn Collection",
            "condition": "Entrati Lanthorns count is low (< 8)",
            "task": "Farm Entrati Lanthorns on Zariman Exterminate/Mobile Defense",
            "eta": "2 hours",
            "power_gain": "+20% (Incarnon weapon crafting requirement)",
            "prerequisites": "Angels of Zariman completed",
            "follow_up": "Use Smeeta Kavat or Resource Booster for double drops."
        })
        
    # Rule 3: Credits
    if owned.get("Credits", 0) < 100000:
        rules_applied.append({
            "rule_name": "Credits Farming",
            "condition": "Credits count is low (< 100,000)",
            "task": "Farm Index (Neptune) or Dark Sectors",
            "eta": "30 mins",
            "power_gain": "+15% (Required for Mod Fusion, Crafting, and Trading)",
            "prerequisites": "Neptune star chart unlocked",
            "follow_up": "Max out high-priority Galvanized rifle mods."
        })
        
    return rules_applied
