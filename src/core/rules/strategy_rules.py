from __future__ import annotations
from typing import Any
from src.models.player import Player

def check_strategy(player: Player) -> list[dict[str, Any]]:
    """Evaluates high-level accounts strategies including mastery ranks and loadout synergies."""
    rules_applied = []
    
    # Rule 1: Mastery Rank 14 bottleneck
    if player.mastery_rank < 14:
        rules_applied.append({
            "rule_name": "Mastery Rank 14 Target",
            "condition": "Mastery Rank is less than 14",
            "task": "Build and level items to reach Mastery Rank 14",
            "eta": "5-10 hours",
            "power_gain": "+30% (Unlocks all Zariman Incarnon weapons Phenmor/Laetum/Felarx)",
            "prerequisites": "Market/Dojo blueprints purchased",
            "follow_up": "Talk to Cavalero to buy evolving weapon blueprints."
        })
        
    # Rule 2: Weapon Ownership
    owned_weapons = {w.lower() for w in player.owned_weapons}
    if "phenmor" not in owned_weapons:
        rules_applied.append({
            "rule_name": "Acquire Phenmor",
            "condition": "Phenmor not owned",
            "task": "Run Zariman Bounties to acquire Phenmor blueprint",
            "eta": "2-4 hours",
            "power_gain": "+40% (Acquire top-meta single-target rifle)",
            "prerequisites": "Angels of Zariman completed, Cavalero Rank 3",
            "follow_up": "Unlock all 5 evolutions to unlock 2000% non-crit damage boost."
        })
        
    return rules_applied
