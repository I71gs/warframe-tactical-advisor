from __future__ import annotations
import tempfile
import shutil
from src.models.player import Player
from src.core.goal_history_engine import GoalHistoryEngine
from src.core.snapshot_repository import SnapshotRepository

def test_goal_history_engine() -> None:
    temp_dir = tempfile.mkdtemp()
    try:
        repo = SnapshotRepository(snapshots_dir=temp_dir)
        engine = GoalHistoryEngine(repo=repo)
        
        # Player who completed some goals
        player = Player(
            mastery_rank=16,
            completed_quests=["The Sacrifice", "The War Within", "The New War", "Angels of the Zariman"],
            steel_path_unlocked=True,
            arbitrations_unlocked=True,
            owned_weapons=["Phenmor", "Laetum"],
            owned_mods=["galvanized chamber", "serration"],
            owned_arcanes=["primary merciless"]
        )
        
        history = engine.get_goal_history(player)
        assert len(history) > 0
        
        # "Finish Main Story" should be completed for this player
        main_story_goal = next(g for g in history if g["goal"] == "Finish Main Story")
        assert main_story_goal["completed"] is True
        assert main_story_goal["power_rating"] >= 0.0
        
    finally:
        shutil.rmtree(temp_dir)

def test_goal_history_engine_pending() -> None:
    engine = GoalHistoryEngine()
    player = Player(mastery_rank=1, completed_quests=[])
    history = engine.get_goal_history(player)
    # A fresh player should have pending targets
    for g in history:
        assert g["completed"] is False
        assert g["date_completed"] == "Pending"
