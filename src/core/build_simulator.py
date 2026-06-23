from __future__ import annotations
from typing import Any
from src.models.player import Player

class BuildSimulator:
    """Simulates builds for meta weapons, scoring the player's current setup vs. potential setup."""

    def __init__(self) -> None:
        # Define builds and mod weights
        # Base mods: 25, Galvanized mods: 30, Arcanes: 30, Utility/Extra: 20
        self.weights = {
            "serration": 25,
            "hornet strike": 25,
            "split chamber": 25,
            "barrel diffusion": 25,
            "galvanized chamber": 30,
            "galvanized aptitude": 20,
            "primary merciless": 30,
            "secondary merciless": 30
        }
        
        self.build_templates = {
            "phenmor": ["Serration", "Split Chamber", "Galvanized Chamber", "Galvanized Aptitude", "Primary Merciless"],
            "torid": ["Serration", "Split Chamber", "Galvanized Chamber", "Primary Merciless"],
            "felarx": ["Serration", "Split Chamber", "Galvanized Chamber", "Primary Merciless"],
            "laetum": ["Hornet Strike", "Barrel Diffusion", "Secondary Merciless"],
            "nataruk": ["Serration", "Split Chamber", "Galvanized Chamber"],
            "burston incarnon": ["Serration", "Split Chamber", "Galvanized Chamber", "Primary Merciless"],
            "latron incarnon": ["Serration", "Split Chamber", "Galvanized Chamber", "Primary Merciless"],
            "lex prime": ["Hornet Strike", "Barrel Diffusion", "Secondary Merciless"],
            "kuva bramma": ["Serration", "Split Chamber", "Galvanized Chamber", "Primary Merciless"]
        }

    def simulate_build(self, player: Player, weapon_name: str) -> dict[str, Any] | None:
        w_lower = weapon_name.strip().lower()
        if w_lower not in self.build_templates:
            return None

        build = self.build_templates[w_lower]
        owned_mods = {m.lower() for m in player.owned_mods}
        owned_arcanes = {a.lower() for a in player.owned_arcanes}
        
        # Add basic mods as always-owned for simulation fallback if they aren't explicitly in the DB
        # E.g. players usually have Serration/Hornet Strike early on.
        # But we still check if they are in the database.
        # Wait, if they are not in the DB, let's treat them as missing to encourage accurate profile maintenance,
        # but let's assume common base mods are present unless proven otherwise? No, check DB!
        
        total_weight = sum(self.weights.get(m.lower(), 20) for m in build)
        owned_weight = 0
        
        components = []
        missing = []
        
        for item in build:
            item_lower = item.lower()
            owned = (item_lower in owned_mods) or (item_lower in owned_arcanes)
            
            # Fallback check for basic mods like Serration/Hornet Strike/Split Chamber
            # since player DB might not contain them by default initially
            if not owned and item_lower in ("serration", "hornet strike", "split chamber", "barrel diffusion"):
                # If player mastery rank >= 2, assume they own base mods as a fallback helper
                if player.mastery_rank >= 2:
                    owned = True
            
            item_weight = self.weights.get(item_lower, 20)
            if owned:
                owned_weight += item_weight
                components.append({"name": item, "owned": True})
            else:
                components.append({"name": item, "owned": False})
                missing.append(item)

        potential_score = 95
        current_score = int((owned_weight / total_weight) * potential_score) if total_weight > 0 else 0
        if current_score > potential_score:
            current_score = potential_score

        gain = potential_score - current_score

        # EHP and combat scores for v2.0
        health = 300 + player.mastery_rank * 10
        armor = 200 + (100 if player.steel_path_unlocked else 0)
        shield = 300 + (150 if player.arbitrations_unlocked else 0)
        ehp = int(shield + health * (1 + armor / 300))
        
        dps_score = current_score
        crit_score = 50 + (25 if "point strike" in owned_mods else 0) + (20 if "vital sense" in owned_mods else 0)
        status_score = 50 + (30 if "galvanized aptitude" in owned_mods or "galvanized shot" in owned_mods else 0)
        survivability_score = min(100, int((ehp / 1200) * 100))
        overall_rating = int((dps_score + crit_score + status_score + survivability_score) / 4)

        return {
            "weapon": weapon_name.title(),
            "current_score": current_score,
            "potential_score": potential_score,
            "components": components,
            "missing": missing,
            "gain": f"+{gain}%",
            "health": health,
            "armor": armor,
            "shield": shield,
            "ehp": ehp,
            "dps_score": dps_score,
            "crit_score": crit_score,
            "status_score": status_score,
            "survivability_score": survivability_score,
            "overall_rating": overall_rating
        }
