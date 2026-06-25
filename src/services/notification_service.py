from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QApplication
from src.gui.widgets.notification_widget import NotificationWidget

if TYPE_CHECKING:
    from src.core.app_context import AppContext

class NotificationService:
    """Manages system alerts and toast alerts triggered by background processes with category filters."""

    def __init__(self, context: AppContext) -> None:
        self.context = context
        self.allowed_categories = {
            "system": True,
            "milestone": True,
            "alert": True,
            "backup": True,
            "goals": True
        }
        # Subscribe to standard triggers
        self.context.event_bus.subscribe("NOTIFICATION", self.handle_notification)
        self.context.event_bus.subscribe("PLUGINS_LOADED", lambda data: self.show_toast_filtered("Custom plugins loaded successfully.", "success", "system"))
        self.context.event_bus.subscribe("SNAPSHOT_CREATED", lambda data: self.show_toast_filtered("Progression snapshot created.", "info", "system"))
        self.context.event_bus.subscribe("ACCOUNT_SWITCHED", lambda data: self.show_toast_filtered(f"Switched account to: {data.get('profile', '')}", "success", "system"))
        
        # Phase 10 triggers
        self.context.event_bus.subscribe("DAILY_GOALS_RESET", lambda data: self.show_toast_filtered("Daily goals have been reset! Time for new targets.", "info", "goals"))
        self.context.event_bus.subscribe("BACKUP_CONFIRMATION", lambda data: self.show_toast_filtered("Backup completed successfully! Database secured.", "success", "backup"))

    def handle_notification(self, data: dict) -> None:
        msg = data.get("message", "")
        level = data.get("level", "info")
        duration = data.get("duration", 3000)
        category = data.get("category", "system")
        self.show_toast_filtered(msg, level, category, duration)

    def toggle_category(self, category: str, enabled: bool) -> None:
        """Enables/disables notifications for the specified category."""
        if category in self.allowed_categories:
            self.allowed_categories[category] = enabled

    def is_category_enabled(self, category: str) -> bool:
        return self.allowed_categories.get(category, True)

    def show_toast_filtered(self, message: str, level: str = "info", category: str = "system", duration_ms: int = 3000) -> None:
        """Shows toast alert only if the category is allowed."""
        if self.is_category_enabled(category):
            self.show_toast(message, level, duration_ms)

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

    def notify(self, message: str, level: str = "info", category: str = "system") -> None:
        """Helper to trigger notifications via event bus."""
        self.context.event_bus.publish("NOTIFICATION", {"message": message, "level": level, "category": category})
