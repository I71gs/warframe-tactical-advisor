from __future__ import annotations
from src.core.app_context import AppContext
from src.services.notification_service import NotificationService

def test_notification_service() -> None:
    context = AppContext()
    service = NotificationService(context)

    messages = []
    def callback(data: dict) -> None:
        messages.append(data.get("message"))

    context.event_bus.subscribe("NOTIFICATION", callback)
    service.notify("Test Message Notification")

    assert "Test Message Notification" in messages
