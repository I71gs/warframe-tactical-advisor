from __future__ import annotations
import math
from typing import Any
from src.models.player import Player
from src.core.weapon_database import WEAPONS

class MasteryPlanner:
    """Calculates Mastery Rank benchmarks, XP deficits, leveling recommendations, and timeframe projections."""

    def calculate_plan(self, player: Player) -> dict[str, Any]:
        mr = player.mastery_rank
        
        # Cumulative XP formula: XP = 2500 * (MR^2)
        current_rank_xp = 2500 * (mr ** 2)
        next_rank_xp = 2500 * ((mr + 1) ** 2)
        xp_needed = next_rank_xp - current_rank_xp
        
        # Suggest leveling items (items that the player does not currently own)
        owned_weapons = {w.lower() for w in player.owned_weapons}
        
        suggested_weapons = []
        for w in WEAPONS:
            if w["name"].lower() not in owned_weapons:
                suggested_weapons.append({
                    "name": w["name"],
                    "category": w.get("category", "Primary"),
                    "xp_gain": 3000,
                    "source": w.get("acquisition", "Dojo/Market")
                })
                
        # Limit to top 5 recommendations
        suggested_weapons = suggested_weapons[:5]
        
        # Suggest frames to level
        completed_quests = {q.lower() for q in player.completed_quests}
        suggested_frames = []
        if "angels of the zariman" not in completed_quests:
            suggested_frames.append({"name": "Wisp", "xp_gain": 6000, "source": "Ropalolyst (Jupiter)"})
            suggested_frames.append({"name": "Saryn", "xp_gain": 6000, "source": "Kela De Thaym (Sedna)"})
            
        if player.mastery_rank < 10:
            suggested_frames.append({"name": "Rhino", "xp_gain": 6000, "source": "Jackal (Venus)"})
            
        # Add basic fallbacks if list is empty
        if not suggested_frames:
            suggested_frames.append({"name": "Mirage Prime", "xp_gain": 6000, "source": "Void Relics"})
            suggested_frames.append({"name": "Mesa Prime", "xp_gain": 6000, "source": "Void Relics"})

        # Time estimate based on average daily leveling speed of 10,000 XP (approx 1-2 items per day)
        daily_cap = 12000
        days_to_next = max(1, math.ceil(xp_needed / daily_cap))
        
        return {
            "current_mr": mr,
            "next_mr": mr + 1,
            "xp_needed": xp_needed,
            "days_estimate": f"≈ {days_to_next} days" if days_to_next > 1 else "≈ 1 day",
            "weapons_to_level": suggested_weapons,
            "frames_to_build": suggested_frames
        }
