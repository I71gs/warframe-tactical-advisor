from src.models.player import Player
from src.core.achievement_engine import AchievementEngine

def test_achievement_badges() -> None:
    ae = AchievementEngine()
    
    # Starting player with zero achievements unlocked
    player = Player(
        mastery_rank=1,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False,
        owned_mods=[],
        owned_arcanes=[],
        owned_weapons=[]
    )
    
    badges = ae.get_badges(player)
    assert all(b["unlocked"] is False for b in badges)
    
    # Advanced player with all achievements unlocked
    player_adv = Player(
        mastery_rank=14,
        completed_quests=["The Second Dream", "The War Within", "The Sacrifice", "The New War", "Angels of the Zariman"],
        steel_path_unlocked=True,
        arbitrations_unlocked=True,
        owned_mods=["Galvanized Chamber", "Galvanized Aptitude"],
        owned_arcanes=[],
        owned_weapons=["Phenmor"]
    )
    
    badges_adv = ae.get_badges(player_adv)
    # Story Master, Steel Path, Archon Hunter, Incarnon Collector, Mod Master should be unlocked
    core_badge_ids = {"story_master", "steel_path", "archon_hunter", "incarnon_collector", "mod_master"}
    for b in badges_adv:
        if b["id"] in core_badge_ids:
            assert b["unlocked"] is True
