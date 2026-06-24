from __future__ import annotations
import tempfile
import shutil
from pathlib import Path
from src.models.player import Player
from src.core.snapshot_repository import SnapshotRepository

def test_snapshot_repository_lifecycle() -> None:
    temp_dir = tempfile.mkdtemp()
    try:
        repo = SnapshotRepository(snapshots_dir=temp_dir)
        player = Player(
            mastery_rank=10,
            completed_quests=["The Second Dream"],
            owned_mods=["serration"],
            owned_arcanes=[],
            owned_weapons=["Phenmor"],
            steel_path_unlocked=False,
            arbitrations_unlocked=False,
            helminth_unlocked=False
        )
        
        # Test Save
        filepath = repo.save_snapshot(player, date_str="2026-06-20")
        assert filepath.exists()
        
        # Test List
        snapshots = repo.list_snapshots()
        assert "2026-06-20" in snapshots
        
        # Test Get
        data = repo.get_snapshot("2026-06-20")
        assert data is not None
        assert data["player"]["mastery_rank"] == 10
        
        # Test Restore
        restored = repo.restore_snapshot("2026-06-20")
        assert restored is not None
        assert restored.mastery_rank == 10
        assert "The Second Dream" in restored.completed_quests
        
        # Test Compare
        player2 = Player(
            mastery_rank=11,
            completed_quests=["The Second Dream", "The War Within"],
            owned_mods=["serration", "galvanized chamber"],
            owned_arcanes=[],
            owned_weapons=["Phenmor", "Laetum"],
            steel_path_unlocked=True,
            arbitrations_unlocked=False,
            helminth_unlocked=False
        )
        repo.save_snapshot(player2, date_str="2026-06-21")
        
        diff = repo.compare_snapshots("2026-06-20", "2026-06-21")
        assert diff is not None
        assert diff["mastery_rank_change"] == 1
        assert "The War Within" in diff["quests"]["added"]
        assert "Laetum" in diff["weapons"]["added"]
        assert "galvanized chamber" in diff["mods"]["added"]
        
    finally:
        shutil.rmtree(temp_dir)

def test_snapshot_repository_missing_file() -> None:
    repo = SnapshotRepository(snapshots_dir="/non/existent/dir")
    assert repo.get_snapshot("2026-06-20") is None
    assert repo.restore_snapshot("2026-06-20") is None

def test_snapshot_repository_invalid_json() -> None:
    temp_dir = tempfile.mkdtemp()
    try:
        repo = SnapshotRepository(snapshots_dir=temp_dir)
        invalid_file = Path(temp_dir) / "2026-06-20.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            f.write("invalid json payload")
            
        assert repo.get_snapshot("2026-06-20") is None
        assert repo.restore_snapshot("2026-06-20") is None
    finally:
        shutil.rmtree(temp_dir)
