from __future__ import annotations
from src.core.app_context import AppContext

def test_event_bus_pub_sub() -> None:
    context = AppContext()
    event_payload = None

    def callback(data: dict) -> None:
        nonlocal event_payload
        event_payload = data

    context.event_bus.subscribe("TEST_EVENT", callback)
    context.event_bus.publish("TEST_EVENT", {"status": "ok"})

    assert event_payload is not None
    assert event_payload["status"] == "ok"
