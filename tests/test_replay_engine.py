from __future__ import annotations
import tempfile
import shutil
from src.models.player import Player
from src.core.replay_engine import ReplayEngine
from src.core.snapshot_repository import SnapshotRepository

def test_replay_engine_milestones() -> None:
    temp_dir = tempfile.mkdtemp()
    try:
        repo = SnapshotRepository(snapshots_dir=temp_dir)
        engine = ReplayEngine()
        
        player = Player(
            mastery_rank=8,
            completed_quests=["The Second Dream", "The War Within"],
            steel_path_unlocked=True
        )
        
        # Test timeline data without snapshots
        timeline = engine.get_timeline_data(player, repo)
        assert len(timeline) > 0
        
        # Unlocked milestone check
        mr3_milestone = next(t for t in timeline if t["name"] == "MR3")
        assert mr3_milestone["status"] == "unlocked"
        
        # Test progression speed calculations
        speed_msg = engine.calculate_progression_speed(timeline)
        assert "Insufficient" in speed_msg
        
        # Add snapshots to test speed calculations
        repo.save_snapshot(Player(mastery_rank=3), date_str="2026-06-01")
        repo.save_snapshot(Player(mastery_rank=3, completed_quests=["The Second Dream"]), date_str="2026-06-05")
        
        timeline_with_history = engine.get_timeline_data(player, repo)
        speed_msg_history = engine.calculate_progression_speed(timeline_with_history)
        assert "milestone" in speed_msg_history or "speed" in speed_msg_history or "average" in speed_msg_history
        
    finally:
        shutil.rmtree(temp_dir)

def test_replay_engine_empty_snapshots() -> None:
    engine = ReplayEngine()
    player = Player(mastery_rank=1, completed_quests=[])
    timeline = engine.get_timeline_data(player, SnapshotRepository(snapshots_dir="/non/existent"))
    assert len(timeline) > 0
    # Since there are no snapshots, speed should be insufficient
    speed = engine.calculate_progression_speed(timeline)
    assert "Insufficient" in speed
