from __future__ import annotations
from PySide6.QtWidgets import QApplication
from src.core.search_engine_v3 import SearchEngineV3
from src.gui.search_tab import SearchTab
from src.core.settings_manager import SettingsManager

# Ensure QApplication is initialized for widget tests
app = QApplication.instance() or QApplication([])

def test_search_v3_aliases_and_tags() -> None:
    engine = SearchEngineV3()
    results_alias = engine.search("sp")
    assert len(results_alias) > 0
    sp_matches = [r for r in results_alias if "steel path" in r["name"].lower() or "steel path" in r["details"].lower()]
    assert len(sp_matches) > 0
    
    results_tag = engine.search("incarnon")
    assert len(results_tag) > 0
    phenmor_res = next((r for r in results_tag if r["name"] == "Phenmor"), None)
    assert phenmor_res is not None
    assert phenmor_res["relevance"] >= 40

def test_search_v3_empty() -> None:
    engine = SearchEngineV3()
    assert engine.search("") == []
    assert engine.search("   ") == []

def test_search_v3_alias_expansion() -> None:
    engine = SearchEngineV3()
    results = engine.search("galvanized")
    assert len(results) > 0
    mod_names = [r["name"].lower() for r in results if r["category"] == "MOD"]
    assert any("galvanized chamber" in name for name in mod_names)

def test_search_v4_typo_tolerance() -> None:
    engine = SearchEngineV3()
    # Typo tolerance matching: "phenmro" -> "Phenmor"
    res1 = engine.search("phenmro")
    assert len(res1) > 0
    assert any(r["name"] == "Phenmor" for r in res1)

    # "wips" -> "Wisp"
    res2 = engine.search("wips")
    assert len(res2) > 0
    assert any(r["name"] == "Wisp" for r in res2)

def test_search_v4_indexing_categories() -> None:
    engine = SearchEngineV3()
    # Check that categories are correctly set up
    results = engine.search("Carrier")
    assert any(r["category"] == "COMPANION" for r in results)

    results = engine.search("Lith")
    assert any(r["category"] == "RELIC" for r in results)

    results = engine.search("Endo")
    assert any(r["category"] == "RESOURCE" for r in results)

def test_search_v4_rich_preview_panel() -> None:
    tab = SearchTab()
    # Test preview data retrieval helper
    item = {
        "name": "Phenmor",
        "category": "WEAPON",
        "details": "Details here",
        "wiki_url": "https://warframe.fandom.com/wiki/Phenmor",
        "raw_data": {"mastery_required": 14, "acquisition": "Zariman"}
    }
    preview = tab.get_rich_preview_data(item)
    assert preview["name"] == "Phenmor"
    assert preview["category"] == "WEAPON"
    assert "Mastery Rank 14" in preview["mr_required"]
    assert "Zariman" in preview["acquisition"]
    assert "Voidgel Orbs" in preview["crafting"]

def test_search_v4_settings_persistence() -> None:
    # Clear any existing settings to prevent pollution from previous runs
    settings = SettingsManager()
    settings.update(relic_filters={})
    settings.save()
    
    from src.gui.relic_tab import RelicTab
    tab = RelicTab()
    
    # Verify defaults
    assert tab.chip_all.isChecked() is True
    assert tab.chip_lith.isChecked() is False
    assert tab.chip_meso.isChecked() is False
    
    # Toggle Lith and Meso chips via user click simulation
    tab.chip_lith.click()
    tab.chip_meso.click()
    
    # Instantiate a fresh settings manager to load the saved state from disk
    fresh_settings = SettingsManager()
    saved = fresh_settings.get("relic_filters", {})
    assert saved.get("lith") is True
    assert saved.get("meso") is True
    assert saved.get("all") is False
