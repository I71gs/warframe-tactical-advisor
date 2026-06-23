from __future__ import annotations
from src.core.codex_engine import CodexEngine
from src.core.player_loader import PlayerLoader

def test_codex_engine_search() -> None:
    engine = CodexEngine()
    
    # Empty query returns all entries
    all_entries = engine.search("")
    assert len(all_entries) > 0

    # Search for specific weapon
    res = engine.search("Phenmor")
    assert len(res) > 0
    assert any(entry["name"] == "Phenmor" for entry in res)

    # Search for specific frame
    res_wisp = engine.search("Wisp")
    assert len(res_wisp) > 0
    assert any(entry["name"] == "Wisp" for entry in res_wisp)

def test_codex_details() -> None:
    engine = CodexEngine()
    player = PlayerLoader().load_player()
    
    details = engine.get_details("Phenmor", player)
    assert details is not None
    assert details["name"] == "Phenmor"
    assert "owned" in details

    details_invalid = engine.get_details("NonExistentCodexEntry", player)
    assert details_invalid is None
