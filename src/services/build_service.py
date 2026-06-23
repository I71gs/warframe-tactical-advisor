from __future__ import annotations
from typing import TYPE_CHECKING, Any
from src.core.build_simulator import BuildSimulator
from src.core.build_database import BuildDatabase
from src.core.build_recommender import BuildRecommender
from src.core.weapon_tier_engine import WeaponTierEngine
from src.core.team_synergy_engine import TeamSynergyEngine
from src.core.encyclopedia_engine import EncyclopediaEngine

if TYPE_CHECKING:
    from src.core.app_context import AppContext

class BuildService:
    """Manages meta builds, weapon tiers, loadout simulators, team synergy, and encyclopedia lookups."""

    def __init__(self, context: AppContext) -> None:
        self.context = context
        self.sim = BuildSimulator()
        self.db = BuildDatabase()
        self.recommender = BuildRecommender()
        self.tier_engine = WeaponTierEngine()
        self.synergy_engine = TeamSynergyEngine()
        self.encyclopedia = EncyclopediaEngine()

    def get_all_builds(self) -> list[dict[str, Any]]:
        return self.db.get_all_builds()

    def get_build_for_weapon(self, weapon_name: str) -> dict[str, Any] | None:
        return self.db.get_build_for_weapon(weapon_name)

    def simulate_build(self, weapon_name: str) -> dict[str, Any] | None:
        player = self.context.player_service.get_player()
        return self.sim.simulate_build(player, weapon_name)

    def get_recommendations(self) -> list[dict[str, Any]]:
        player = self.context.player_service.get_player()
        return self.recommender.recommend_builds(player)

    def get_weapon_tiers(self) -> dict[str, list[dict[str, Any]]]:
        player = self.context.player_service.get_player()
        return self.tier_engine.get_weapon_tiers(player)

    def calculate_team_synergy(self, frame: str, primary: str, secondary: str, melee: str) -> dict[str, Any]:
        player = self.context.player_service.get_player()
        return self.synergy_engine.calculate_synergy(player, frame, primary, secondary, melee)

    def search_encyclopedia(self, query: str) -> list[dict[str, Any]]:
        return self.encyclopedia.search(query)

    def get_encyclopedia_details(self, name: str) -> dict[str, Any] | None:
        player = self.context.player_service.get_player()
        return self.encyclopedia.get_details(name, player)
