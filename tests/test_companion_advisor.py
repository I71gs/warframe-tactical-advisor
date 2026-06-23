from src.core.companion_engine import CompanionEngine
from src.models.player import Player

def test_companion_recommendation() -> None:
    ce = CompanionEngine()
    
    # Early game player gets Carrier Prime
    player_early = Player(mastery_rank=2)
    rec_early = ce.recommend_companion(player_early)
    assert rec_early["name"] == "Carrier Prime"

    # Endgame player gets Panzer Vulpaphyla
    player_late = Player(mastery_rank=18, steel_path_unlocked=True, completed_quests=["The Second Dream", "The New War"])
    rec_late = ce.recommend_companion(player_late)
    assert rec_late["name"] == "Panzer Vulpaphyla"

    assert len(ce.get_companions()) > 0
