from src.models.player import Player
from src.core.milestone_engine import MilestoneEngine

def test_milestone_engine_early_game() -> None:
    player = Player(
        mastery_rank=5,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False
    )
    
    me = MilestoneEngine()
    milestones = me.get_milestones(player)
    
    # Immediate milestone should be next quest: The Second Dream
    assert "The Second Dream" in milestones["immediate"]["label"]
    assert milestones["immediate"]["completed"] is False
    
    # Short term should be complete New War
    assert "The New War" in milestones["short_term"]["label"]
    assert milestones["short_term"]["completed"] is False

def test_milestone_engine_completed() -> None:
    player = Player(
        mastery_rank=16,
        completed_quests=["The Second Dream", "The War Within", "The Sacrifice", "Chains of Harrow", "The New War", "Angels of the Zariman"],
        steel_path_unlocked=True,
        arbitrations_unlocked=True,
        owned_mods=["Galvanized Chamber", "Galvanized Aptitude"],
        owned_arcanes=["Primary Merciless"],
        owned_weapons=["Phenmor"]
    )
    
    me = MilestoneEngine()
    milestones = me.get_milestones(player)
    
    # Quests are done
    assert milestones["immediate"]["completed"] is True
    # New war/arbitrations done
    assert milestones["short_term"]["completed"] is True
