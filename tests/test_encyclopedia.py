from src.core.encyclopedia_engine import EncyclopediaEngine
from src.models.player import Player

def test_encyclopedia_search() -> None:
    ee = EncyclopediaEngine()
    results = ee.search("Wisp")
    assert len(results) == 1
    assert results[0]["name"] == "Wisp"

    all_items = ee.search("")
    assert len(all_items) > 0

def test_encyclopedia_details() -> None:
    ee = EncyclopediaEngine()
    player = Player(mastery_rank=10, owned_weapons=["Phenmor"])
    details = ee.get_details("Phenmor", player)
    assert details is not None
    assert details["owned"] is True

    details_missing = ee.get_details("Laetum", player)
    assert details_missing is not None
    assert details_missing["owned"] is False
