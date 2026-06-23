from __future__ import annotations
from typing import TYPE_CHECKING, Any
from src.core.resource_engine import ResourceEngine
from src.core.economy_engine import EconomyEngine
from src.core.relic_engine import RelicEngine
from src.core.incarnon_engine import IncarnonEngine
from src.core.circuit_engine import CircuitEngine
from src.core.duviri_engine import DuviriEngine
from src.core.companion_engine import CompanionEngine
from src.core.session_engine import SessionEngine
from src.core.farming_planner import FarmingPlanner
from src.core.collection_engine import CollectionEngine
from src.core.mastery_planner import MasteryPlanner

if TYPE_CHECKING:
    from src.core.app_context import AppContext

class ResourceService:
    """Manages owned resources, economy calculations, relics, incarnons, circuit cycles, Duviri upgrades, companion ratings, and session checklists."""

    def __init__(self, context: AppContext) -> None:
        self.context = context
        self.re = ResourceEngine()
        self.ee = EconomyEngine()
        self.relic_engine = RelicEngine()
        self.incarnon_engine = IncarnonEngine()
        self.circuit_engine = CircuitEngine()
        self.duviri_engine = DuviriEngine()
        self.companion_engine = CompanionEngine()
        self.session_engine = SessionEngine()
        self.farming_planner = FarmingPlanner()
        self.collection_engine = CollectionEngine()
        self.mastery_planner = MasteryPlanner()

    def get_owned_resources(self) -> dict[str, int]:
        return self.re.load_owned_resources()

    def save_owned_resources(self, owned: dict[str, int]) -> None:
        self.re.save_owned_resources(owned)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def get_resource_plan(self, target: str) -> list[dict[str, Any]]:
        return self.re.get_plan(target)

    def get_recipes(self) -> dict[str, dict[str, int]]:
        return self.re.get_recipes()

    def get_economy_plan(self) -> list[dict[str, Any]]:
        return self.ee.get_economy_plan()

    def search_relics(self, query: str) -> list[dict[str, Any]]:
        return self.relic_engine.search_relics(query)

    def get_incarnon_templates(self) -> list[str]:
        return self.incarnon_engine.get_templates()

    def get_incarnon_status(self, weapon_name: str) -> dict[str, Any]:
        player = self.context.player_service.get_player()
        return self.incarnon_engine.get_weapon_status(player, weapon_name)

    def get_incarnon_state(self) -> dict[str, Any]:
        return self.incarnon_engine.load_incarnon_state()

    def save_incarnon_state(self, state: dict[str, Any]) -> None:
        self.incarnon_engine.save_incarnon_state(state)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def get_circuit_recommendation(self) -> dict[str, Any]:
        player = self.context.player_service.get_player()
        return self.circuit_engine.get_circuit_recommendation(player)

    def get_duviri_state(self) -> dict[str, Any]:
        return self.duviri_engine.load_duviri_state()

    def get_duviri_progress(self, state: dict[str, Any]) -> float:
        return self.duviri_engine.get_progress_percentage(state)

    def get_duviri_recommendations(self, state: dict[str, Any]) -> list[str]:
        return self.duviri_engine.get_recommendations(state)

    def save_duviri_state(self, state: dict[str, Any]) -> None:
        self.duviri_engine.save_duviri_state(state)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def get_companions(self) -> list[dict[str, Any]]:
        return self.companion_engine.get_companions()

    def recommend_companion(self) -> dict[str, Any]:
        player = self.context.player_service.get_player()
        return self.companion_engine.recommend_companion(player)

    def generate_session_itinerary(self, duration_minutes: int) -> list[dict[str, Any]]:
        return self.session_engine.generate_itinerary(duration_minutes)

    def generate_farming_path(self, goal: str) -> list[dict[str, Any]]:
        player = self.context.player_service.get_player()
        return self.farming_planner.generate_farming_path(player, goal)

    def get_collection_status(self) -> dict[str, Any]:
        player = self.context.player_service.get_player()
        return self.collection_engine.get_collection_status(player)

    def get_mastery_plan(self) -> dict[str, Any]:
        player = self.context.player_service.get_player()
        return self.mastery_planner.calculate_plan(player)
