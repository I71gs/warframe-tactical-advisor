from src.models.player import Player
from src.core.account_rating_engine import AccountRatingEngine

def test_account_rating_grades() -> None:
    are = AccountRatingEngine()
    
    # Early game player
    player_early = Player(
        mastery_rank=2,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False
    )
    
    res = are.get_rating(player_early)
    assert res["grade"] == "Beginner"
    assert res["color"] == "#ef4444"
    assert "Starting" in res["description"]
    
    # Late game veteran player
    player_vet = Player(
        mastery_rank=15,
        completed_quests=["The Second Dream", "The War Within", "The Sacrifice", "Chains of Harrow", "The New War", "Angels of the Zariman"],
        steel_path_unlocked=True,
        arbitrations_unlocked=True,
        owned_mods=["Serration", "Split Chamber", "Galvanized Chamber", "Galvanized Aptitude"],
        owned_arcanes=["Primary Merciless"],
        owned_weapons=["Phenmor", "Laetum", "Felarx", "Torid", "Kuva Bramma"],
        helminth_unlocked=True
    )
    
    res_vet = are.get_rating(player_vet)
    # The readiness score will be high, resulting in a Veteran/Endgame/Legendary grade
    assert res_vet["grade"] in ("Veteran", "Endgame", "Legendary")
