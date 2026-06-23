from __future__ import annotations
from typing import Any
from src.models.player import Player

ITEMS = [
    {
        "name": "Wisp",
        "category": "WARFRAME",
        "acquisition": "Assassination: Ropalolyst (Jupiter)",
        "synergies": "Phenmor, Laetum, Haste buffers",
        "builds": "Strength and Duration focus for Reservoir buffs.",
        "dependencies": "Requires Jupiter unlocked, Natah quest completed.",
    },
    {
        "name": "Saryn",
        "category": "WARFRAME",
        "acquisition": "Assassination: Kela De Thaym (Sedna)",
        "synergies": "Torid, Status-based weapons",
        "builds": "Range and Strength focus for Spore spread.",
        "dependencies": "Requires Sedna unlocked.",
    },
    {
        "name": "Phenmor",
        "category": "WEAPON",
        "acquisition": "Cavalero Vendor (Zariman Chrysalith)",
        "synergies": "Wisp, Volt, Devastation Evolution build",
        "builds": "Viral Heat build with non-critical damage scaling.",
        "dependencies": "Requires Mastery Rank 14, Angels of Zariman quest completed.",
    },
    {
        "name": "Laetum",
        "category": "WEAPON",
        "acquisition": "Cavalero Vendor (Zariman Chrysalith)",
        "synergies": "Mesa, secondary weapon buffers",
        "builds": "Viral Heat build with Overwhelming Attrition evolution.",
        "dependencies": "Requires Mastery Rank 14, Angels of Zariman quest completed.",
    },
    {
        "name": "Galvanized Chamber",
        "category": "MOD",
        "acquisition": "Arbitrations Vendor (Vitus Essence)",
        "synergies": "Primary rifle builds",
        "builds": "Essential primary weapon multishot mod scaling.",
        "dependencies": "Requires Star Chart completed, Arbitrations unlocked.",
    },
    {
        "name": "Primary Merciless",
        "category": "ARCANE",
        "acquisition": "Steel Path Acolytes drop",
        "synergies": "High fire rate primary guns",
        "builds": "Raw base damage scaling (+360%) at max rank 5.",
        "dependencies": "Requires Steel Path unlocked.",
    },
    {
        "name": "Entrati Lanthorn",
        "category": "RESOURCE",
        "acquisition": "Zariman missions, bounties, and extractors",
        "synergies": "Zariman weapon crafting",
        "builds": "Crafting material, farm with resource boosters.",
        "dependencies": "Requires Zariman unlocked.",
    }
]

class EncyclopediaEngine:
    """Offline encyclopedia lookup compiler for Warframe codex assets."""

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search encyclopedia items matching query."""
        q = query.strip().lower()
        if not q:
            return ITEMS
        return [item for item in ITEMS if q in item["name"].lower() or q in item["category"].lower()]

    def get_details(self, name: str, player: Player) -> dict[str, Any] | None:
        """Fetch item details and overlay player's ownership status."""
        for item in ITEMS:
            if item["name"].lower() == name.lower():
                # Verify status
                owned = False
                n_lower = name.lower()
                if item["category"] == "WARFRAME":
                    # Mock check for owned frame
                    owned = n_lower in ["wisp", "saryn"] # Assume Wisp/Saryn owned for basic profiles or checks
                elif item["category"] == "WEAPON":
                    owned = n_lower in {w.lower() for w in player.owned_weapons}
                elif item["category"] == "MOD":
                    owned = n_lower in {m.lower() for m in player.owned_mods}
                elif item["category"] == "ARCANE":
                    owned = n_lower in {a.lower() for a in player.owned_arcanes}
                elif item["category"] == "RESOURCE":
                    # Check resources state
                    from src.core.resource_engine import ResourceEngine
                    res_owned = ResourceEngine().load_owned_resources()
                    owned = res_owned.get(name, 0) > 0
                
                details = item.copy()
                details["owned"] = owned
                return details
        return None
