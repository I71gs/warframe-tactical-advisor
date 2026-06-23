from src.core.search_engine import SearchEngine

def test_search_engine_basic() -> None:
    se = SearchEngine()
    
    # Searching for "phenmor" should return the weapon Phenmor
    res = se.search("Phenmor")
    assert len(res) > 0
    assert res[0]["name"] == "Phenmor"
    assert res[0]["category"] == "WEAPON"
    
    # Case-insensitive substring search for "merciless"
    res_arcane = se.search("merciless")
    assert len(res_arcane) > 0
    assert any(r["name"] == "Primary Merciless" for r in res_arcane)
    
    # Searching for an empty string should return empty list
    assert se.search("") == []
    
    # Search for an invalid query
    assert se.search("nonexistent_item_query_string") == []
