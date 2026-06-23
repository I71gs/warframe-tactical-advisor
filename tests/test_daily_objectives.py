from pathlib import Path
from src.models.player import Player
from src.core.daily_objectives_engine import DailyObjectivesEngine

def test_daily_objectives_generation_and_persistence(tmp_path: Path) -> None:
    state_file = tmp_path / "daily_state.json"
    doe = DailyObjectivesEngine(state_path=state_file)
    
    player = Player(
        mastery_rank=8,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False,
        owned_mods=[],
        owned_arcanes=[],
        owned_weapons=[]
    )
    
    # Generate daily objectives
    state = doe.get_daily_objectives(player)
    assert "date" in state
    assert len(state["objectives"]) >= 3
    
    # Verify persistence
    assert state_file.exists()
    
    # Modify completion status and save
    state["objectives"][0]["completed"] = True
    doe.save_daily_state(state)
    
    # Reload and verify
    reloaded = doe.get_daily_objectives(player)
    assert reloaded["objectives"][0]["completed"] is True
