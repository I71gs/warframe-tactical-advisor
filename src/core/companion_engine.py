from __future__ import annotations
from typing import Any
from src.models.player import Player

try:
    from src.core.data_loader import load_json
    COMPANIONS = load_json('data/companions.json')
except Exception:
    COMPANIONS = [
        {
            "name": "Panzer Vulpaphyla",
            "synergy": "95%",
            "survivability": "100% (Infinite Revives)",
            "utility": "98% (Viral Spreading)",
            "rationale": "Uses Viral Quills to spread status stacks. Devolution mod ensures it revives itself automatically after dying, providing permanent radar and item vacuum."
        },
        {
            "name": "Nautilus",
            "synergy": "90%",
            "survivability": "75%",
            "utility": "92% (Grouping CC)",
            "rationale": "Cordon pulls enemies together in a tight cluster, synergizing perfectly with AoE explosive weapons (Kuva Bramma) or high-punch through rifles (Phenmor)."
        },
        {
            "name": "Carrier Prime",
            "synergy": "80%",
            "survivability": "85%",
            "utility": "80% (Ammo Case)",
            "rationale": "Converts unused ammo drops into active primary weapon ammo. Essential for ammo-hungry weapons like Kuva Bramma or heavy machineguns."
        },
        {
            "name": "Diriga",
            "synergy": "85%",
            "survivability": "70%",
            "utility": "85% (Status Spreader)",
            "rationale": "Arc Coil shocks multiple nearby targets, enabling rapid status application to trigger weapon damage multipliers (Galvanized Aptitude)."
        }
    ]

class CompanionEngine:
    """Evaluates companion ratings and recommends optimal options based on loadouts."""

    def get_companions(self) -> list[dict[str, Any]]:
        return COMPANIONS

    def recommend_companion(self, player: Player) -> dict[str, Any]:
        # Recommend based on progression stage: early game gets Carrier, late game gets Panzer
        from src.core.progression_engine import ProgressionEngine
        stage = ProgressionEngine().determine_stage(player)
        
        if stage in ["early_game", "mid_game"]:
            return COMPANIONS[2] # Carrier Prime
        else:
            return COMPANIONS[0] # Panzer Vulpaphyla
