from __future__ import annotations
from src.core.plugin_registry import PluginRegistry

def test_plugin_sdk_features() -> None:
    registry = PluginRegistry()
    registry.clear()

    # Register weapon
    registry.register_weapon({
        "name": "Test SDK Weapon",
        "type": "Primary",
        "acquisition": "Test Source",
        "meta_rating": 75,
        "category": "Rifle"
    })
    assert any(w["name"] == "Test SDK Weapon" for w in registry.weapons)

def test_plugin_registry_clear() -> None:
    registry = PluginRegistry()
    registry.register_weapon({"name": "Trash Weapon"})
    assert len(registry.weapons) > 0
    registry.clear()
    assert len(registry.weapons) == 0

def test_plugin_registry_weapons() -> None:
    registry = PluginRegistry()
    registry.clear()
    registry.register_weapon({"name": "Custom Sword", "type": "Melee"})
    assert any(w["name"] == "Custom Sword" for w in registry.weapons)

def test_plugin_registry_builds() -> None:
    registry = PluginRegistry()
    registry.clear()
    registry.register_build({"weapon": "Custom Sword", "rating": 90})
    assert any(b["weapon"] == "Custom Sword" for b in registry.builds)

def test_plugin_registry_routes() -> None:
    registry = PluginRegistry()
    registry.clear()
    registry.register_route({"weapon": "Custom Sword", "source": "Test"})
    assert any(r["weapon"] == "Custom Sword" for r in registry.routes)

def test_plugin_registry_themes() -> None:
    registry = PluginRegistry()
    registry.clear()
    registry.register_theme("Cyan Void", {"PRIMARY": "#00ffff"})
    assert "Cyan Void" in registry.themes

def test_plugin_registry_singleton() -> None:
    r1 = PluginRegistry()
    r2 = PluginRegistry()
    assert r1 is r2
