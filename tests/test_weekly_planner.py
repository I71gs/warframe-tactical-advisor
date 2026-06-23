from pathlib import Path
from src.models.player import Player
from src.core.weekly_planner import WeeklyPlanner

def test_weekly_planner_flow(tmp_path: Path) -> None:
    state_file = tmp_path / "weekly_state.json"
    wp = WeeklyPlanner(state_path=state_file)
    
    # Initially missing items/quests
    player = Player(
        mastery_rank=8,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False,
        owned_mods=[],
        owned_arcanes=[],
        owned_weapons=[]
    )
    
    state = wp.get_weekly_state(player)
    assert "week" in state
    assert len(state["goals"]) > 0
    # All goals should be incomplete initially
    assert all(g["completed"] is False for g in state["goals"])
    
    # Now create player who has completed some goals
    player_updated = Player(
        mastery_rank=14,
        completed_quests=["Angels of the Zariman"],
        steel_path_unlocked=True,
        arbitrations_unlocked=True,
        owned_mods=["Galvanized Chamber"],
        owned_arcanes=[],
        owned_weapons=[]
    )
    
    # Reload weekly state - it should dynamically check profile and update completed status!
    state_updated = wp.get_weekly_state(player_updated)
    
    # Verify that the goals matching completed actions are marked True
    for g in state_updated["goals"]:
        text = g["text"].lower()
        if "angels of zariman" in text or "galvanized chamber" in text or "steel path" in text:
            assert g["completed"] is True
