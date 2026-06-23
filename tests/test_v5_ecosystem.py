from __future__ import annotations
import sys
import time
from pathlib import Path
from PySide6.QtWidgets import QWidget, QApplication
from src.core.app_context import AppContext
from src.services.cache_service import CacheService
from src.services.notification_service import NotificationService
from src.core.search_engine_v2 import SearchEngineV2
from src.gui.widgets.command_palette_dialog import CommandPaletteDialog
from src.core.plugin_registry import PluginRegistry
from src.core.plugin_api import PluginAPI
from src.core.weapon_database import WEAPONS
from src.core.build_database import BUILDS
from src.core.farming_database import FARMING_DATA

class MockTab(QWidget):
    pass

def test_cache_service(tmp_path: Path) -> None:
    context = AppContext()
    cache_file = tmp_path / "app_cache.json"
    cache = CacheService(context, cache_file=cache_file)
    
    # Simple set and get
    cache.set("test_key", "test_val")
    assert cache.get("test_key") == "test_val"
    
    # TTL expiration
    cache.set("expire_key", "expire_val", ttl_seconds=1)
    assert cache.get("expire_key") == "expire_val"
    time.sleep(1.1)
    assert cache.get("expire_key") is None
    
    # Disk reloading
    cache2 = CacheService(context, cache_file=cache_file)
    assert cache2.get("test_key") == "test_val"
    
    # Clear volatile vs wiki/search
    cache.set("wiki_article_saryn", "saryn wiki content")
    cache.set("search_query_laetum", "laetum search content")
    cache.set("progression_score", 98)
    
    # Trigger PROFILE_UPDATED
    context.event_bus.publish("PROFILE_UPDATED")
    
    # Volatile should be cleared, wiki/search retained
    assert cache.get("progression_score") is None
    assert cache.get("wiki_article_saryn") == "saryn wiki content"
    assert cache.get("search_query_laetum") == "laetum search content"

def test_search_engine_v2() -> None:
    context = AppContext()
    se = SearchEngineV2(context)
    
    # 1. Search existing weapon
    res = se.search("Phenmor")
    assert len(res) > 0
    assert any(r["category"] == "WEAPON" and r["name"] == "Phenmor" for r in res)
    assert any(r["category"] == "BUILD" and r["name"] == "Phenmor Build" for r in res)
    
    # 2. Search relic
    res_relic = se.search("Axi G1")
    assert len(res_relic) > 0
    assert any(r["category"] == "RELIC" and "Axi G1" in r["name"] for r in res_relic)
    
    # 3. Search resource
    res_res = se.search("Voidplumes")
    assert len(res_res) > 0
    assert any(r["category"] == "RESOURCE" and r["name"] == "Voidplumes" for r in res_res)
    
    # 4. Search daily task
    res_task = se.search("Zariman Bounties")
    assert len(res_task) > 0
    assert any(r["category"] == "DAILY TASK" for r in res_task)

def test_plugin_sdk_and_registry() -> None:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
    api = PluginAPI()
    registry = PluginRegistry()
    registry.clear()
    
    # 1. Register weapon
    custom_weapon = {
        "name": "Dynamic Custom Weapon",
        "type": "Primary",
        "acquisition": "Dynamic Source",
        "meta_rating": 80,
        "category": "Rifle"
    }
    api.register_weapon(custom_weapon)
    assert any(w["name"] == "Dynamic Custom Weapon" for w in WEAPONS)
    assert any(w["name"] == "Dynamic Custom Weapon" for w in registry.weapons)
    
    # 2. Register build
    custom_build = {
        "weapon": "Dynamic Custom Weapon",
        "mods": ["Serration"],
        "arcane": "None",
        "element": "None",
        "rating": 85
    }
    api.register_build(custom_build)
    assert any(b["weapon"] == "Dynamic Custom Weapon" for b in BUILDS)
    assert any(b["weapon"] == "Dynamic Custom Weapon" for b in registry.builds)
    
    # 3. Register farming
    custom_farm = {"source": "Dynamic Node", "estimated_time": "30 mins"}
    api.register_farming("Dynamic Custom Weapon", custom_farm)
    assert "dynamic custom weapon" in FARMING_DATA
    assert FARMING_DATA["dynamic custom weapon"]["source"] == "Dynamic Node"
    
    # 4. Register command
    cmd_called = False
    def cmd_cb() -> None:
        nonlocal cmd_called
        cmd_called = True
    api.register_command("Test Dynamic Command", cmd_cb)
    assert len(registry.commands) == 1
    assert registry.commands[0]["label"] == "Test Dynamic Command"
    
    # 5. Register tab
    api.register_tab(MockTab, "Dynamic Custom Tab")
    assert len(registry.tabs) == 1
    assert registry.tabs[0]["title"] == "Dynamic Custom Tab"
    
    # 6. Test Event Bus propagation
    event_payload = None
    def event_cb(data: dict) -> None:
        nonlocal event_payload
        event_payload = data
        
    api.subscribe_event("PLUGIN_TEST_EVENT", event_cb)
    api.publish_event("PLUGIN_TEST_EVENT", {"ok": True})
    assert event_payload == {"ok": True}

def test_command_palette_dialog() -> None:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
    dialog = CommandPaletteDialog()
    
    # Check default commands are populated
    dialog.search_input.setText("")
    assert dialog.list_widget.count() > 0
    
    # Search for backup command
    dialog.search_input.setText("Backup")
    assert dialog.list_widget.count() > 0
    
    # Search for an item and verify results from search engine show up
    dialog.search_input.setText("Phenmor")
    assert dialog.list_widget.count() > 0
    labels = [dialog.list_widget.item(i).text() for i in range(dialog.list_widget.count())]
    assert any("Phenmor" in l for l in labels)
