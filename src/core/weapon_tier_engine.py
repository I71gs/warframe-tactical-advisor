from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.weapon_database import WEAPONS
from src.core.build_simulator import BuildSimulator

class WeaponTierEngine:
    """Dynamically categorizes weapons into tiers (S, A, B, C) based on base meta ratings and personalized inventory checks."""

    def get_weapon_tiers(self, player: Player) -> dict[str, list[dict[str, Any]]]:
        tiers = {"S": [], "A": [], "B": [], "C": []}
        owned_weapons = {w.lower() for w in player.owned_weapons}
        sim = BuildSimulator()
        
        # Weapon strengths and custom notes definitions
        strengths_db = {
            "phenmor": "Incarnon mode, Devastating Attrition (+2000% damage on non-critical hits).",
            "laetum": "Incarnon secondary, extreme fire rate and AOE explosion in Incarnon form.",
            "felarx": "Incarnon shotgun, high shell velocity, devastating close-quarter burst.",
            "torid": "Incarnon beam transition, high status application, toxic chaining beams.",
            "nataruk": "Infinite ammo bow, perfect release critical multiplier, extreme punch through.",
            "burston incarnon": "Fast burst rifle, Incarnon transformation into a high-capacity bullet hose.",
            "latron incarnon": "Bouncing explosive puncture disk projectile, high armor strip potential.",
            "kuva bramma": "Cluster bomb launcher bow, massive area-of-effect clear, high raw damage.",
            "kuva nukor": "Chaining radiation beam, extreme critical multiplier, premium primer.",
            "lex prime": "Pistol sniper, pocket-sized high-crit pocket railgun.",
            "glaive prime": "Forced slash proc explosion, premium melee clearing weapon."
        }

        for weapon in WEAPONS:
            name = weapon["name"]
            name_lower = name.lower()
            meta_rating = weapon.get("meta_rating", 50)
            owned = name_lower in owned_weapons
            
            # Determine base meta tier
            if meta_rating >= 90:
                base_tier = "S"
            elif meta_rating >= 80:
                base_tier = "A"
            elif meta_rating >= 70:
                base_tier = "B"
            else:
                base_tier = "C"

            # Determine personalized tier (drops if missing key build mods)
            pers_tier = base_tier
            build_res = sim.simulate_build(player, name_lower)
            weakness = []
            
            if build_res:
                missing = build_res["missing"]
                if missing:
                    weakness.append(f"Missing build components: {', '.join(missing)}")
                    # Drop personalized tier if missing more than half the build or critical parts
                    if build_res["current_score"] < 50:
                        tier_order = ["S", "A", "B", "C"]
                        curr_idx = tier_order.index(base_tier)
                        pers_idx = min(curr_idx + 1, 3) # drop by one tier
                        pers_tier = tier_order[pers_idx]
            else:
                if not owned:
                    weakness.append("Not owned. Farm to add this meta weapon to loadout.")

            strengths = strengths_db.get(name_lower, "Solid general meta weapon.")

            weapon_info = {
                "name": name,
                "meta_rating": meta_rating,
                "base_tier": base_tier,
                "personalized_tier": pers_tier,
                "owned": owned,
                "strengths": strengths,
                "weaknesses": " / ".join(weakness) if weakness else "Fully optimized build!"
            }
            
            tiers[base_tier].append(weapon_info)

        # Sort within tiers by meta rating
        for tier in tiers:
            tiers[tier].sort(key=lambda w: w["meta_rating"], reverse=True)
            
        return tiers
