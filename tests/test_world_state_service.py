from __future__ import annotations
import time
from src.core.app_context import AppContext
from src.services.world_state_service import WorldStateService

def test_world_state_service_fallback() -> None:
    context = AppContext()
    service = WorldStateService(context)
    
    # Test fallback structure
    state = service._get_fallback_state()
    assert state["cetus"]["isDay"] is True
    assert "timeLeft" in state["cetus"]
    assert len(state["fissures"]) == 2
    assert state["fissures"][0]["node"] == "E Prime (Earth)"
    assert len(state["alerts"]) == 1

def test_world_state_service_caching() -> None:
    context = AppContext()
    service = WorldStateService(context)
    
    # Manually seed cached state
    cached_mock = {"cetus": {"isDay": False, "timeLeft": "5m", "shortString": "Night"}}
    service.cached_state = cached_mock
    service.last_fetch_time = time.time()
    
    # Must retrieve cached version without requesting api
    state = service.get_world_state()
    assert state == cached_mock
