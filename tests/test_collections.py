from src.core.collection_engine import CollectionEngine
from src.models.player import Player

def test_collection_status() -> None:
    ce = CollectionEngine()
    player = Player(
        mastery_rank=5,
        completed_quests=["angels of the zariman"],
        owned_weapons=["Phenmor"],
        owned_mods=["Galvanized Chamber"],
        owned_arcanes=["Primary Merciless"]
    )
    status = ce.get_collection_status(player)
    assert "warframes" in status
    assert "weapons" in status
    assert "mods" in status
    assert "arcanes" in status
    assert status["weapons"]["owned"] >= 1
    assert status["mods"]["owned"] >= 1
    assert status["arcanes"]["owned"] >= 1
    assert status["overall_pct"] > 0
