from __future__ import annotations
from src.core.search_engine_v3 import SearchEngineV3

def test_search_v3_aliases_and_tags() -> None:
    engine = SearchEngineV3()
    
    # Test that alias search matches target item
    results_alias = engine.search("sp")
    assert len(results_alias) > 0
    # "sp" maps to "steel path", so matches should include Steel Path goals or related tasks
    sp_matches = [r for r in results_alias if "steel path" in r["name"].lower() or "steel path" in r["details"].lower()]
    assert len(sp_matches) > 0
    
    # Test tags-based ranking boost
    results_tag = engine.search("incarnon")
    assert len(results_tag) > 0
    # Weapons tagged as "incarnon" (like Phenmor) should show up with high relevance
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
    # "galvanized" maps to several galvanized mods, which should be fetched
    mod_names = [r["name"].lower() for r in results if r["category"] == "MOD"]
    assert any("galvanized chamber" in name for name in mod_names)
