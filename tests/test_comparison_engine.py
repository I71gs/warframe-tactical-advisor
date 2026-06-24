from __future__ import annotations
import pytest
import unittest.mock
from src.core.save_manager import SaveManager
from src.core.comparison_engine import ComparisonEngine
from src.database.database import DatabaseManager

def test_comparison_load_profile(tmp_path) -> None:
    sm = SaveManager(profiles_dir=tmp_path)
    sm.create_profile("acc1")
    engine = ComparisonEngine()
    
    with unittest.mock.patch("src.core.save_manager.PROFILES_DIR", tmp_path):
        player = engine.load_player_profile("acc1")
        assert player.mastery_rank == 1

def test_comparison_differentials(tmp_path) -> None:
    sm = SaveManager(profiles_dir=tmp_path)
    sm.create_profile("acc1")
    sm.create_profile("acc2")
    
    db1 = DatabaseManager(db_path=sm.get_profile_db_path("acc1"))
    db1.save_player(5, True, False, False)
    db1.add_completed_quest("The Second Dream")
    db1.connection.close()

    db2 = DatabaseManager(db_path=sm.get_profile_db_path("acc2"))
    db2.save_player(10, True, True, True)
    db2.add_completed_quest("The Second Dream")
    db2.add_completed_quest("The War Within")
    db2.connection.close()

    engine = ComparisonEngine()
    with unittest.mock.patch("src.core.save_manager.PROFILES_DIR", tmp_path):
        report = engine.compare_profiles("acc1", "acc2")
        assert report["differentials"]["mastery_diff"] == 5
        assert "the war within" in report["differentials"]["quests_p2_only"]

def test_comparison_resources(tmp_path) -> None:
    sm = SaveManager(profiles_dir=tmp_path)
    sm.create_profile("acc1")
    sm.create_profile("acc2")
    
    from src.core.resource_engine import ResourceEngine
    re1 = ResourceEngine(state_path=tmp_path / "acc1" / "resource_state.json")
    re1.save_owned_resources({"Endo": 1000})
    
    re2 = ResourceEngine(state_path=tmp_path / "acc2" / "resource_state.json")
    re2.save_owned_resources({"Endo": 5000})
    
    engine = ComparisonEngine()
    with unittest.mock.patch("src.core.save_manager.PROFILES_DIR", tmp_path):
        report = engine.compare_profiles("acc1", "acc2")
        assert report["resources"]["Endo"]["diff"] == 4000

def test_comparison_strength_rankings(tmp_path) -> None:
    sm = SaveManager(profiles_dir=tmp_path)
    sm.create_profile("acc1")
    sm.create_profile("acc2")
    
    db1 = DatabaseManager(db_path=sm.get_profile_db_path("acc1"))
    db1.save_player(20, True, True, True)
    db1.connection.close()

    db2 = DatabaseManager(db_path=sm.get_profile_db_path("acc2"))
    db2.save_player(1, False, False, False)
    db2.connection.close()

    engine = ComparisonEngine()
    with unittest.mock.patch("src.core.save_manager.PROFILES_DIR", tmp_path):
        report = engine.compare_profiles("acc1", "acc2")
        assert report["strength_rankings"] == ["acc1", "acc2"]
