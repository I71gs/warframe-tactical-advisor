from __future__ import annotations
from src.core.app_context import AppContext

def test_services_initialization() -> None:
    context = AppContext()
    assert context.player_service is not None
    assert context.progression_service is not None
    assert context.resource_service is not None
    assert context.notification_service is not None
    assert context.analytics_service is not None
    assert context.llm_service is not None

def test_services_player_service() -> None:
    context = AppContext()
    player = context.player_service.get_player()
    assert player is not None
    assert hasattr(player, "mastery_rank")

def test_services_progression_service() -> None:
    context = AppContext()
    stage = context.progression_service.get_stage()
    assert isinstance(stage, str)

def test_services_resource_service() -> None:
    context = AppContext()
    resources = context.resource_service.get_owned_resources()
    assert isinstance(resources, dict)

def test_services_notification_service() -> None:
    context = AppContext()
    assert context.notification_service.context is context

def test_services_analytics_service() -> None:
    context = AppContext()
    context.analytics_service.track_tab_view("Test Tab")
    # Analytics shouldn't crash
    assert True

def test_services_llm_service() -> None:
    context = AppContext()
    advice = context.llm_service.ask("Phenmor")
    assert isinstance(advice, str)
