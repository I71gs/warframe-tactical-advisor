from __future__ import annotations
from src.core.search_engine_v3 import SearchEngineV3
from src.core.app_context import AppContext
from src.core.plugin_registry import PluginRegistry

def test_search_v3_relevance() -> None:
    context = AppContext()
    se = SearchEngineV3(context)
    res = se.search("phenmor")
    assert len(res) > 0
    assert "phenmor" in res[0]["name"].lower()

def test_search_v3_wisp_boost() -> None:
    context = AppContext()
    se = SearchEngineV3(context)
    res = se.search("wisp")
    assert len(res) > 0
    assert any("wisp" in r["name"].lower() for r in res)

def test_search_v3_archons_boost() -> None:
    context = AppContext()
    se = SearchEngineV3(context)
    res = se.search("archons")
    assert len(res) > 0
    assert any("archon" in r["name"].lower() for r in res)

def test_search_v3_custom_route() -> None:
    context = AppContext()
    se = SearchEngineV3(context)
    pr = PluginRegistry()
    pr.register_route({
        "weapon": "SearchV3 Test Weapon",
        "source": "Test Fissure",
        "estimated_time": "1 hour"
    })
    res = se.search("SearchV3 Test Weapon")
    assert len(res) > 0
    assert any("SearchV3 Test Weapon Route" in r["name"] for r in res)

def test_search_v3_galvanized_chamber_boost() -> None:
    context = AppContext()
    se = SearchEngineV3(context)
    res = se.search("galvanized chamber")
    assert len(res) > 0
    assert any("galvanized chamber" in r["name"].lower() for r in res)

def test_search_v3_empty_query() -> None:
    context = AppContext()
    se = SearchEngineV3(context)
    assert se.search("") == []
    assert se.search("   ") == []
