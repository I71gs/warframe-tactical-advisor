from __future__ import annotations
import tempfile
import os
from src.models.player import Player
from src.services.import_export_service import ImportExportService

def test_import_export_service() -> None:
    service = ImportExportService()
    
    # Create temp files
    fd_json, path_json = tempfile.mkstemp(suffix=".json")
    os.close(fd_json)
    fd_csv, path_csv = tempfile.mkstemp(suffix=".csv")
    os.close(fd_csv)
    
    try:
        # Test exports
        service.export_to_json(path_json)
        assert os.path.exists(path_json)
        
        service.export_to_csv(path_csv)
        assert os.path.exists(path_csv)
        
        # Test imports
        player_json = service.import_from_json(path_json)
        assert player_json is not None
        assert player_json.mastery_rank >= 0
        
        player_csv = service.import_from_csv(path_csv)
        assert player_csv is not None
        assert player_csv.mastery_rank >= 0
        
        # Test merge
        other_player = Player(
            mastery_rank=20,
            completed_quests=["The Sacrifice"],
            owned_mods=["test_mod"],
            owned_arcanes=[],
            owned_weapons=[],
            steel_path_unlocked=True
        )
        
        # We can test merge logic by saving a backup of current player
        current_db_player = service.import_from_json(path_json)
        
        # Run merge
        service.merge_profiles(other_player)
        
        # Verify merged state
        from src.core.player_loader import PlayerLoader
        merged = PlayerLoader().load_player()
        assert merged.mastery_rank >= 20
        assert "The Sacrifice" in merged.completed_quests
        assert "test_mod" in merged.owned_mods
        assert merged.steel_path_unlocked is True
        
        # Restore backup to keep database clean
        service.restore_profile(current_db_player)
        
    finally:
        if os.path.exists(path_json):
            os.remove(path_json)
        if os.path.exists(path_csv):
            os.remove(path_csv)

def test_import_export_invalid_csv() -> None:
    fd_csv, path_csv = tempfile.mkstemp(suffix=".csv")
    os.close(fd_csv)
    try:
        service = ImportExportService()
        with open(path_csv, "w", encoding="utf-8") as f:
            f.write("Type,Name,Value\n")
            f.write("Attribute,mastery_rank,12\n")
            f.write("MalformedRow\n") # missing values
            f.write("Mod,serration,Owned\n")
            
        player = service.import_from_csv(path_csv)
        assert player.mastery_rank == 12
        assert "serration" in player.owned_mods
    finally:
        if os.path.exists(path_csv):
            os.remove(path_csv)
