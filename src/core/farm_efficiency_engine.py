from __future__ import annotations
from typing import Any
from src.models.player import Player

class FarmEfficiencyEngine:
    """Calculates prioritized, optimized farming sequences to advance accounts efficiently."""

    def get_routes(self, player: Player) -> list[dict[str, Any]]:
        completed_quests = {q.lower() for q in player.completed_quests}
        owned_weapons = {w.lower() for w in player.owned_weapons}
        owned_mods = {m.lower() for m in player.owned_mods}
        owned_arcanes = {a.lower() for a in player.owned_arcanes}

        routes = []

        # 1. Star Chart & Arbitrations Route
        is_arb_done = player.arbitrations_unlocked
        routes.append({
            "name": "Steel Path Readiness Route (Galvanized Mods)",
            "priority": "CRITICAL" if not is_arb_done else "COMPLETED",
            "efficiency": "96%",
            "duration": "15 hours",
            "active": not is_arb_done,
            "steps": [
                "Clear all remaining normal Star Chart nodes to access Arbitrations.",
                "Run Arbitration alerts to collect Vitus Essence drops.",
                "Purchase 'Galvanized Chamber' & 'Galvanized Diffusion' from Arbiter vendor.",
                "Max out Galvanized mods to boost weapon damage multishot."
            ]
        })

        # 2. Zariman Weapons Route
        is_zariman_unlocked = "angels of the zariman" in completed_quests
        is_weapons_done = "phenmor" in owned_weapons and "laetum" in owned_weapons
        routes.append({
            "name": "Zariman Incarnon Arsenal Route",
            "priority": "HIGH" if (is_zariman_unlocked and not is_weapons_done) else ("MEDIUM" if not is_zariman_unlocked else "COMPLETED"),
            "efficiency": "92%",
            "duration": "18 hours",
            "active": is_zariman_unlocked and not is_weapons_done,
            "steps": [
                "Complete 'Angels of the Zariman' story quest.",
                "Run Chrysalith bounties for Voidplume Pinions & Gyre components.",
                "Earn Standing with Holdfasts to reach Rank 3 (Cavalero blueprints).",
                "Craft Phenmor and Laetum, then complete their evolution challenges."
            ]
        })

        # 3. SP Acolytes Route
        is_sp_done = player.steel_path_unlocked
        is_arcanes_done = "primary merciless" in owned_arcanes
        routes.append({
            "name": "Gun Arcane Optimization Route (Acolytes)",
            "priority": "HIGH" if (is_sp_done and not is_arcanes_done) else ("LOW" if not is_sp_done else "COMPLETED"),
            "efficiency": "88%",
            "duration": "10 hours",
            "active": is_sp_done and not is_arcanes_done,
            "steps": [
                "Unlock Steel Path difficulty by visiting Teshin.",
                "Complete Steel Path Daily Incursions for guaranteed Steel Essence.",
                "Defeat spawned SP Acolytes (Violence, Malice) for Arcane drops.",
                "Merge duplicates to rank 'Primary Merciless' to Rank 5."
            ]
        })

        # 4. Helminth & Custom Synergies Route
        is_helminth_done = player.helminth_unlocked
        routes.append({
            "name": "Endgame Loadout Synergy Route (Helminth)",
            "priority": "MEDIUM" if not is_helminth_done else "COMPLETED",
            "efficiency": "85%",
            "duration": "12 hours",
            "active": is_helminth_done is False,
            "steps": [
                "Raise standing with Entrati in Necralisk to Rank 3.",
                "Purchase the Helminth Segment blueprint from Son.",
                "Subjugate duplicate Warframes to extract signature active skills.",
                "Infuse abilities (e.g. Roar/Eclipse) onto your primary meta loadout."
            ]
        })

        # Sort active routes first, then sort by priority level
        priority_weights = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "COMPLETED": 0}
        routes.sort(key=lambda r: (-1 if r["active"] else 0, -priority_weights.get(r["priority"], 0)))
        return routes
