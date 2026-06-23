from src.models.player import Player
from src.core.dependency_engine import DependencyEngine
from src.core.farming_planner import FarmingPlanner

def test_dependency_engine_checks() -> None:
    # Player with low MR and no quests
    player = Player(
        mastery_rank=5,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False
    )
    
    de = DependencyEngine()
    
    # Phenmor requires quest "Angels of the Zariman" and MR 14
    unmet = de.get_unmet_dependencies("Phenmor", player)
    assert "Mastery Rank 14+" in unmet
    assert "Quest: Angels of the Zariman" in unmet
    
    # Galvanized Chamber requires Arbitrations Unlocked and MR 10
    unmet_mod = de.get_unmet_dependencies("Galvanized Chamber", player)
    assert "Mastery Rank 10+" in unmet_mod
    assert "Arbitrations Unlocked" in unmet_mod

def test_dependency_engine_met() -> None:
    # Player who meets all requirements
    player = Player(
        mastery_rank=15,
        completed_quests=["The Second Dream", "The War Within", "The Sacrifice", "Chains of Harrow", "The New War", "Angels of the Zariman"],
        steel_path_unlocked=True,
        arbitrations_unlocked=True
    )
    
    de = DependencyEngine()
    assert de.is_item_unlocked("Phenmor", player) is True
    assert de.is_item_unlocked("Galvanized Chamber", player) is True
    assert de.is_item_unlocked("Primary Merciless", player) is True

def test_farming_planner_sequencing() -> None:
    # Player with quest completion but missing items for Steel Path
    player = Player(
        mastery_rank=12,
        completed_quests=["The Second Dream", "The War Within", "The Sacrifice", "Chains of Harrow", "The New War", "Angels of the Zariman"],
        owned_mods=[],
        owned_arcanes=[],
        owned_weapons=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=True
    )
    
    fp = FarmingPlanner()
    # Unlock Steel Path requires: Galvanized Chamber, Primary Merciless
    farm_path = fp.generate_farming_path(player, "Unlock Steel Path")
    
    # Verify we got items
    items = [x["item"] for x in farm_path]
    assert "Galvanized Chamber" in items
    assert "Primary Merciless" in items
    
    # Verify sequencing: priority 1 (Arbitrations) comes before priority 2 (Steel Path)
    assert farm_path[0]["item"] == "Galvanized Chamber"
    assert farm_path[1]["item"] == "Primary Merciless"
