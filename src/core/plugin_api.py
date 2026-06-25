from __future__ import annotations
from typing import Any, Callable
from src.core.plugin_registry import PluginRegistry
from src.core.app_context import AppContext

class PluginAPI:
    """Public API for third-party plugins to interact with Warframe Tactical Advisor."""

    def __init__(self) -> None:
        self.registry = PluginRegistry()
        self.context = AppContext()

    def register_weapon(self, weapon_data: dict[str, Any]) -> None:
        """Register a custom weapon configuration."""
        self.registry.register_weapon(weapon_data)

    def register_build(self, build_data: dict[str, Any]) -> None:
        """Register a custom build configuration."""
        self.registry.register_build(build_data)

    def register_farming(self, weapon_name: str, farm_data: dict[str, Any]) -> None:
        """Register custom farming location and routes."""
        self.registry.register_farming(weapon_name, farm_data)

    def register_command(self, label: str, callback: Callable[[], None]) -> None:
        """Register a command palette command shortcut."""
        self.registry.register_command(label, callback)

    def register_tab(self, tab_class: type, title: str) -> None:
        """Register a custom UI tab class."""
        self.registry.register_tab(tab_class, title)

    def publish_event(self, event_name: str, data: dict[str, Any] | None = None) -> None:
        """Publish an event to the global Event Bus."""
        self.context.event_bus.publish(event_name, data or {})

    def subscribe_event(self, event_name: str, callback: Callable[[dict[str, Any]], None]) -> None:
        """Subscribe to an event on the global Event Bus."""
        self.context.event_bus.subscribe(event_name, callback)

    def get_player(self) -> Any:
        """Get the current Player model instance."""
        return self.context.player_service.get_player()

    def register_menu(self, menu_title: str, actions: list[dict[str, Any]]) -> None:
        """Register a custom window menu header with item actions."""
        self.registry.register_menu(menu_title, actions)

    def register_settings_section(self, section_name: str, schema: dict[str, Any]) -> None:
        """Register custom settings parameters."""
        self.registry.register_settings_section(section_name, schema)

    def register_context_hook(self, hook_name: str, callback: Callable[[Any], Any]) -> None:
        """Register a context middleware lifecycle hook callback."""
        self.registry.register_context_hook(hook_name, callback)
