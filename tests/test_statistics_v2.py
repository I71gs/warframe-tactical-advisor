from __future__ import annotations
import tempfile
import shutil
from src.models.player import Player
from src.core.statistics_engine_v2 import StatisticsEngineV2
from src.core.snapshot_repository import SnapshotRepository

def test_statistics_engine_v2() -> None:
    temp_dir = tempfile.mkdtemp()
    try:
        repo = SnapshotRepository(snapshots_dir=temp_dir)
        stats = StatisticsEngineV2(repo=repo)
        
        player = Player(
            mastery_rank=15,
            completed_quests=["The Second Dream", "The War Within", "The New War"],
            owned_weapons=["Phenmor", "Laetum"],
            owned_mods=["serration"]
        )
        
        # Save historical snapshots
        repo.save_snapshot(Player(mastery_rank=5), date_str="2026-06-01")
        
        # Test growth data
        growth = stats.get_growth_data(player)
        assert len(growth) >= 2
        
        # Test clearance statistics
        clearance = stats.get_clearance_statistics(player)
        assert "quests_total" in clearance
        assert "weapons_total" in clearance
        assert clearance["weapons_owned"] >= 2
        
        # Test scores breakdown
        breakdown = stats.get_scores_breakdown(player)
        assert "readiness" in breakdown
        assert "story" in breakdown
        assert "builds" in breakdown
        
    finally:
        shutil.rmtree(temp_dir)

def test_statistics_v2_breakdown_validation() -> None:
    stats = StatisticsEngineV2()
    player = Player(mastery_rank=30, steel_path_unlocked=True, arbitrations_unlocked=True, helminth_unlocked=True)
    breakdown = stats.get_scores_breakdown(player)
    assert breakdown["mastery"] == 100.0
    assert breakdown["unlocks"] == 100.0
