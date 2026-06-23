from __future__ import annotations
import copy
from typing import Any
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine

class FutureProjectionEngine:
    """Simulates player progression impact on readiness scores under future scenarios."""

    def __init__(self) -> None:
        self.progression_engine = ProgressionEngine()

    def simulate(self, player: Player) -> dict[str, Any]:
        """Runs simulations for different scenarios and returns target score adjustments."""
        current_readiness = self.progression_engine.get_readiness_score(player)
        
        # Scenario 1: Acquire Phenmor
        player_phenmor = self._clone_player(player)
        if "phenmor" not in {w.lower() for w in player_phenmor.owned_weapons}:
            player_phenmor.owned_weapons.append("Phenmor")
        score_phenmor = self.progression_engine.get_readiness_score(player_phenmor)

        # Scenario 2: Unlock Steel Path & Farm Merciless
        player_sp = self._clone_player(player)
        player_sp.steel_path_unlocked = True
        player_sp.arbitrations_unlocked = True
        if "primary merciless" not in {a.lower() for a in player_sp.owned_arcanes}:
            player_sp.owned_arcanes.append("Primary Merciless")
        score_sp = self.progression_engine.get_readiness_score(player_sp)

        # Scenario 3: Complete Zariman Quest and get meta mods (Galvanized Chamber, Galvanized Aptitude)
        player_zariman = self._clone_player(player)
        if "angels of the zariman" not in {q.lower() for q in player_zariman.completed_quests}:
            player_zariman.completed_quests.append("Angels of Zariman")
        if "the new war" not in {q.lower() for q in player_zariman.completed_quests}:
            player_zariman.completed_quests.append("The New War")
        
        # Add basic galvanized mods
        for mod in ["Galvanized Chamber", "Galvanized Aptitude"]:
            if mod.lower() not in {m.lower() for m in player_zariman.owned_mods}:
                player_zariman.owned_mods.append(mod)
        score_zariman = self.progression_engine.get_readiness_score(player_zariman)

        return {
            "current_readiness": current_readiness,
            "projections": [
                {
                    "scenario": "Acquire Phenmor",
                    "readiness": score_phenmor,
                    "gain": round(max(0.0, score_phenmor - current_readiness), 1)
                },
                {
                    "scenario": "Unlock Steel Path & Farm Merciless",
                    "readiness": score_sp,
                    "gain": round(max(0.0, score_sp - current_readiness), 1)
                },
                {
                    "scenario": "Complete Zariman & Acquire Galvanized Mods",
                    "readiness": score_zariman,
                    "gain": round(max(0.0, score_zariman - current_readiness), 1)
                }
            ]
        }

    def _clone_player(self, player: Player) -> Player:
        return Player(
            mastery_rank=player.mastery_rank,
            completed_quests=copy.copy(player.completed_quests),
            owned_mods=copy.copy(player.owned_mods),
            owned_arcanes=copy.copy(player.owned_arcanes),
            owned_weapons=copy.copy(player.owned_weapons),
            steel_path_unlocked=player.steel_path_unlocked,
            arbitrations_unlocked=player.arbitrations_unlocked,
            helminth_unlocked=player.helminth_unlocked
        )
