from pathlib import Path
from src.models.player import Player
from src.core.long_term_planner import LongTermPlanner

def test_long_term_planner_milestones(tmp_path: Path) -> None:
    state_file = tmp_path / "timeline_state.json"
    ltp = LongTermPlanner(state_path=state_file)
    
    # Early game player
    player = Player(
        mastery_rank=5,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False,
        owned_mods=[],
        owned_arcanes=[],
        owned_weapons=[]
    )
    
    state = ltp.get_timeline_state(player)
    assert state["current_index"] == 0
    assert "The New War Complete" in state["target_milestone"]
    assert "Complete quest: The New War" in state["requirements_remaining"]
    assert state_file.exists()
    
    # Late game player (just needs to unlock steel path)
    player_late = Player(
        mastery_rank=11,
        completed_quests=["The Second Dream", "The War Within", "The Sacrifice", "Chains of Harrow", "The New War"],
        steel_path_unlocked=False,
        arbitrations_unlocked=True,
        owned_mods=[],
        owned_arcanes=[],
        owned_weapons=[]
    )
    state_late = ltp.get_timeline_state(player_late)
    assert state_late["current_index"] == 2
    assert "Steel Path Access" in state_late["target_milestone"]
    assert "Teshin" in state_late["requirements_remaining"][0]
