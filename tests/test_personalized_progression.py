from src.models.player import Player
from src.core.personalized_progression_engine import PersonalizedProgressionEngine

def test_personalized_progression_story_focus() -> None:
    # Player has completed zero quests
    player = Player(
        mastery_rank=5,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False
    )
    
    ppe = PersonalizedProgressionEngine()
    result = ppe.analyze_profile(player)
    
    assert "Complete Quest: The Second Dream" in result["focus"]
    assert "Crucial storyline" in result["why"]
    assert result["eta"] == "5 hours"
    assert result["power_gain"] == "+15%"

def test_personalized_progression_steel_path_focus() -> None:
    # Player has completed story and unlocked arbitrations, but not Steel Path
    player = Player(
        mastery_rank=12,
        completed_quests=["The Second Dream", "The War Within", "The Sacrifice", "The New War", "Angels of the Zariman"],
        steel_path_unlocked=False,
        arbitrations_unlocked=True,
        owned_mods=["Galvanized Chamber", "Galvanized Aptitude"],
        helminth_unlocked=True
    )
    
    ppe = PersonalizedProgressionEngine()
    result = ppe.analyze_profile(player)
    
    assert result["focus"] == "Unlock Steel Path"
    assert "Acolytes" in result["why"]
    assert result["eta"] == "10 hours"
    assert result["power_gain"] == "+25%"
