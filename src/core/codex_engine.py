from __future__ import annotations
from typing import Any
from src.models.player import Player

FALLBACK_CODEX_ENTRIES = [
    {
        "name": "Phenmor",
        "category": "WEAPON",
        "variants": "Phenmor (Incarnon)",
        "incarnons": "Evolution I: Incarnon Form, Evolution II: Rapid Wrath (+20% fire rate), Evolution III: Ready Retaliation (+100% reload speed), Evolution IV: Devastating Attrition (50% chance for +2000% damage on non-critical hits)",
        "acquisition": "Cavalero Vendor (Zariman Chrysalith) for Standings",
        "details": "High-powered semi-automatic rifle that transforms into a full-automatic void machine gun."
    },
    {
        "name": "Dakra Prime",
        "category": "WEAPON",
        "variants": "Dakra Prime",
        "incarnons": "None",
        "acquisition": "Void Fissures / Prime Vault (Sample Plugin custom injection)",
        "details": "A masterwork sword known for high slash damage and excellent critical scaling."
    },
    {
        "name": "Torid",
        "category": "WEAPON",
        "variants": "Torid, Torid Incarnon",
        "incarnons": "Evolution I: Incarnon Form, Evolution II: Final Fusillade, Evolution III: Swift Wing, Evolution IV: Commodore's Fortune (+20% Crit Chance)",
        "acquisition": "Bio Lab Research (Clan Dojo)",
        "details": "Launches toxic spores that explode into gas clouds. Becomes a chaining beam weapon in Incarnon form."
    },
    {
        "name": "Wisp",
        "category": "WARFRAME",
        "abilities": "Reservoirs (Vitality, Haste, Shock), Wil-O-Wisp, Breach Surge, Sol Gate",
        "passive": "Phased: Wisp becomes invisible to enemies while in the air.",
        "helminth": "Breach Surge (Subsumable)",
        "acquisition": "Ropalolyst Assassination (Jupiter)",
        "details": "Dimensional traveler warframe that supports allies with reservoirs and blinds enemies with Breach Surge."
    },
    {
        "name": "Saryn",
        "category": "WARFRAME",
        "abilities": "Spores, Molt, Toxic Lash, Miasma",
        "passive": "Potency: Status effects inflicted by Saryn last 25% longer.",
        "helminth": "Molt (Subsumable)",
        "acquisition": "Kela De Thaym Assassination (Sedna)",
        "details": "Toxin and viral spreader frame capable of clearing maps of enemies using Spores."
    },
    {
        "name": "Galvanized Chamber",
        "category": "MOD",
        "effects": "+80% Multishot (+30% Multishot on kill, stacks up to 5 times)",
        "farming": "Arbitrations Vendor (Vitus Essence Store)",
        "details": "Essential primary rifle multishot mod scaling with enemy kills."
    },
    {
        "name": "Serration",
        "category": "MOD",
        "effects": "+165% Base Damage (at Max Rank 10)",
        "farming": "Star Chart missions, Spy missions, and Survival nodes",
        "details": "Core primary rifle base damage multiplier mod."
    },
    {
        "name": "Entrati Lanthorn",
        "category": "RESOURCE",
        "uses": "Crafting Zariman weapons (Phenmor, Laetum, Felarx) and Gyre warframe parts.",
        "best_farms": "Zariman Chrysalith Bounties, extraction containers, or deploying resource extractors on Zariman.",
        "details": "A rare glowing lantern used for Zariman void engineering recipes."
    },
    {
        "name": "Credits",
        "category": "RESOURCE",
        "uses": "Mod upgrades, weapon blueprint purchases, crafting costs, and trade tax.",
        "best_farms": "The Index (Neptune), Profit-Taker Orb (Fortuna), or Dark Sector missions.",
        "details": "The universal primary currency used throughout the Origin System."
    }
]

def load_codex_entries() -> list[dict[str, Any]]:
    from src.core.data_loader import load_json
    from src.core.weapon_database import WEAPONS
    entries = []
    
    # 1. Warframes
    try:
        wfs = load_json('data/warframes.json')
        for w in wfs:
            abs_str = ", ".join(w["abilities"]) if isinstance(w.get("abilities"), list) else w.get("abilities", "")
            entries.append({
                "name": w["name"],
                "category": "WARFRAME",
                "abilities": abs_str or "Unknown",
                "passive": w.get("passive", "Unknown"),
                "helminth": w.get("subsumed") or w.get("helminth") or "Unknown",
                "acquisition": w.get("acquisition", "Unknown"),
                "details": w.get("description") or f"A battle-ready Warframe: {w['name']}."
            })
    except Exception:
        pass
        
    # 2. Weapons
    for w in WEAPONS:
        has_inc = "Incarnon" in w.get("acquisition", "") or "Cavalero" in w.get("acquisition", "")
        entries.append({
            "name": w["name"],
            "category": "WEAPON",
            "variants": f"{w['name']}, {w['name']} Prime" + (f", {w['name']} Incarnon" if has_inc else ""),
            "incarnons": "Incarnon Form and Evolutions supported." if has_inc else "None",
            "acquisition": w.get("acquisition", "Unknown"),
            "details": f"High performance {w.get('category', 'weapon')} category weapon."
        })
        
    # 3. Mods
    try:
        mods = load_json('data/mods.json')
        for m in mods:
            entries.append({
                "name": m["name"],
                "category": "MOD",
                "effects": m.get("effects", "Standard mod effects."),
                "farming": m.get("source", "Unknown"),
                "details": m.get("details") or f"Mod category: {m.get('category')}."
            })
    except Exception:
        pass
        
    # 4. Resources
    resources = [
        {
            "name": "Entrati Lanthorn",
            "category": "RESOURCE",
            "uses": "Crafting Zariman weapons (Phenmor, Laetum, Felarx) and Gyre warframe parts.",
            "best_farms": "Zariman Chrysalith Bounties, extraction containers, or deploying resource extractors on Zariman.",
            "details": "A rare glowing lantern used for Zariman void engineering recipes."
        },
        {
            "name": "Credits",
            "category": "RESOURCE",
            "uses": "Mod upgrades, weapon blueprint purchases, crafting costs, and trade tax.",
            "best_farms": "The Index (Neptune), Profit-Taker Orb (Fortuna), or Dark Sector missions.",
            "details": "The universal primary currency used throughout the Origin System."
        }
    ]
    entries.extend(resources)
    
    # 5. Companions
    try:
        companions = load_json('data/companions.json')
        for c in companions:
            entries.append({
                "name": c["name"],
                "category": "COMPANION",
                "abilities": c.get("utility", "Standard companion abilities."),
                "acquisition": c.get("acquisition", "Unknown"),
                "details": c.get("rationale") or f"A loyal companion of type {c.get('type')}."
            })
    except Exception:
        pass
        
    # 6. Quests
    try:
        quests = load_json('data/quests.json')
        for q in quests:
            reqs = ", ".join(q.get("requires", [])) if isinstance(q.get("requires"), list) else q.get("requires", "")
            entries.append({
                "name": q["name"],
                "category": "QUEST",
                "details": f"Main story quest node. Prerequisite: {reqs or 'None'}",
                "acquisition": "Quest Log"
            })
    except Exception:
        pass
        
    return entries

class CodexEngine:
    """Offline codex information compiler for weapons, frames, mods, and resources."""

    def __init__(self) -> None:
        from src.core.codex_database_v2 import CODEX_ENTRIES_V2
        entries = load_codex_entries()
        if not entries:
            entries = FALLBACK_CODEX_ENTRIES
        self.all_entries = entries + CODEX_ENTRIES_V2

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return self.all_entries
        return [entry for entry in self.all_entries if q in entry["name"].lower() or q in entry["category"].lower() or q in entry.get("details", "").lower()]

    def get_details(self, name: str, player: Player) -> dict[str, Any] | None:
        name_lower = name.lower()
        for entry in self.all_entries:
            if entry["name"].lower() == name_lower:
                details = entry.copy()
                # Determine ownership based on player profile
                owned = False
                if entry["category"] == "WEAPON":
                    owned = name_lower in {w.lower() for w in player.owned_weapons}
                elif entry["category"] == "WARFRAME":
                    # Wisp and Saryn mock checks
                    owned = name_lower in ["wisp", "saryn"]
                elif entry["category"] == "MOD":
                    owned = name_lower in {m.lower() for m in player.owned_mods}
                elif entry["category"] == "RESOURCE":
                    from src.core.resource_engine import ResourceEngine
                    res_owned = ResourceEngine().load_owned_resources()
                    owned = res_owned.get(name, 0) > 0
                elif entry["category"] in ["FOCUS", "RAILJACK", "NECRAMECH", "COMPANION"]:
                    owned = name_lower in {w.lower() for w in player.owned_weapons}
                details["owned"] = owned
                return details
        return None
