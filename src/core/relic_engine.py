from __future__ import annotations
from typing import Any

RELIC_DATA = [
    {
        "item": "Glaive Prime Blueprint",
        "relic": "Axi G1",
        "rarity": "Rare (Gold)",
        "best_refinement": "Radiant",
        "drop_chance": "10.0%",
        "best_farm": "Apollo (Lua, Disruption)"
    },
    {
        "item": "Braton Prime Barrel",
        "relic": "Meso B1",
        "rarity": "Common (Bronze)",
        "best_refinement": "Intact",
        "drop_chance": "25.3%",
        "best_farm": "Io (Jupiter, Defense)"
    },
    {
        "item": "Lex Prime Receiver",
        "relic": "Neo L1",
        "rarity": "Uncommon (Silver)",
        "best_refinement": "Flawless",
        "drop_chance": "11.0%",
        "best_farm": "Ukko (Void, Capture)"
    },
    {
        "item": "Orthos Prime Blade",
        "relic": "Lith O1",
        "rarity": "Common (Bronze)",
        "best_refinement": "Intact",
        "drop_chance": "25.3%",
        "best_farm": "Hepit (Void, Capture)"
    },
    {
        "item": "Saryn Prime Blueprint",
        "relic": "Axi S1",
        "rarity": "Rare (Gold)",
        "best_refinement": "Radiant",
        "drop_chance": "10.0%",
        "best_farm": "Apollo (Lua, Disruption)"
    }
]

class RelicEngine:
    """Calculates optimal void relic refinements and farming routes for prime rewards."""

    def search_relics(self, query: str) -> list[dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return RELIC_DATA
        return [r for r in RELIC_DATA if q in r["item"].lower() or q in r["relic"].lower()]
