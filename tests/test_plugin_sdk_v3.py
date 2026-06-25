from __future__ import annotations
import pytest
from src.core.plugin_registry import PluginRegistry
from src.core.plugin_api import PluginAPI

def test_plugin_api_menu() -> None:
    api = PluginAPI()
    registry = PluginRegistry()
    registry.clear()
    api.register_menu("My Custom Menu", [{"label": "Action 1", "action": lambda: None}])
    assert len(registry.menus) == 1
    assert registry.menus[0]["title"] == "My Custom Menu"

def test_plugin_api_settings() -> None:
    api = PluginAPI()
    registry = PluginRegistry()
    registry.clear()
    schema = {"enabled": "bool"}
    api.register_settings_section("My Section", schema)
    assert len(registry.settings_sections) == 1
    assert registry.settings_sections[0]["section"] == "My Section"

def test_plugin_api_context_hooks() -> None:
    api = PluginAPI()
    registry = PluginRegistry()
    registry.clear()
    def my_hook(data): return data
    api.register_context_hook("PRE_LOAD", my_hook)
    assert "PRE_LOAD" in registry.context_hooks
    assert registry.context_hooks["PRE_LOAD"][0] == my_hook

def test_plugin_api_clear() -> None:
    api = PluginAPI()
    registry = PluginRegistry()
    registry.clear()
    api.register_menu("Menu", [])
    registry.clear()
    assert len(registry.menus) == 0
