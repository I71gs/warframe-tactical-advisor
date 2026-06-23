from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QApplication
from src.gui.widgets.notification_widget import NotificationWidget

if TYPE_CHECKING:
    from src.core.app_context import AppContext

class NotificationService:
    """Manages system alerts and toast alerts triggered by background processes."""

    def __init__(self, context: AppContext) -> None:
        self.context = context
        # Subscribe to standard triggers
        self.context.event_bus.subscribe("NOTIFICATION", self.handle_notification)
        self.context.event_bus.subscribe("PLUGINS_LOADED", lambda data: self.show_toast("Custom plugins loaded successfully.", "success"))
        self.context.event_bus.subscribe("SNAPSHOT_CREATED", lambda data: self.show_toast("Progression snapshot created.", "info"))
        self.context.event_bus.subscribe("ACCOUNT_SWITCHED", lambda data: self.show_toast(f"Switched account to: {data.get('profile', '')}", "success"))

    def handle_notification(self, data: dict) -> None:
        msg = data.get("message", "")
        level = data.get("level", "info")
        duration = data.get("duration", 3000)
        self.show_toast(msg, level, duration)

    def show_toast(self, message: str, level: str = "info", duration_ms: int = 3000) -> None:
        """Create and show a toast popup matching current main window instance."""
        parent = None
        for widget in QApplication.topLevelWidgets():
            if widget.inherits("QMainWindow"):
                parent = widget
                break

        # Create and launch widget (only when QApplication is initialized and not in tests)
        import sys
        if 'pytest' not in sys.modules:
            toast = NotificationWidget(message, level, parent)
            toast.show_toast(duration_ms)
