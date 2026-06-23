from src.models.player import Player
from src.core.gap_analyzer import GapAnalyzer
from src.core.next_action_engine import NextActionEngine
from src.core.goal_cost_engine import GoalCostEngine
from src.core.build_simulator import BuildSimulator
from src.core.weapon_tier_engine import WeaponTierEngine
from src.core.synergy_engine import SynergyEngine
from src.core.progression_engine import ProgressionEngine

def test_gap_analyzer() -> None:
    player = Player(
        mastery_rank=8,
        completed_quests=["The Second Dream"],
        owned_mods=["Serration"],
        owned_arcanes=[],
        owned_weapons=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False,
        helminth_unlocked=False
    )
    
    analyzer = GapAnalyzer()
    gaps = analyzer.analyze_gaps(player)
    
    # Must identify Steel Path, Arbitrations, and The War Within as gaps
    gap_names = {g["name"] for g in gaps}
    assert "Steel Path" in gap_names
    assert "Arbitrations" in gap_names
    assert "The War Within" in gap_names
    
    # Check severity levels
    quest_gap = next(g for g in gaps if g["name"] == "The War Within")
    assert quest_gap["severity"] == "CRITICAL"

def test_next_action_engine() -> None:
    player = Player(
        mastery_rank=8,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False
    )
    
    nae = NextActionEngine()
    action = nae.determine_next_action(player)
    # Since they have completed 0 quests, "The Second Dream" is the first priority
    assert "The Second Dream" in action["priority"]
    assert "+15% Account Progression" in action["gain"]

def test_goal_cost_engine() -> None:
    player = Player(
        mastery_rank=10,
        completed_quests=["The Second Dream", "The War Within", "The Sacrifice", "Chains of Harrow", "The New War", "Angels of the Zariman"],
        owned_mods=["Serration", "Split Chamber"],
        owned_arcanes=[],
        owned_weapons=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=True
    )
    
    gce = GoalCostEngine()
    cost = gce.calculate_cost(player, "Unlock Steel Path")
    # Needs: Galvanized Chamber, Primary Merciless, and SP unlock itself.
    assert cost["prerequisites"] > 0
    assert "hours" in cost["time"]
    assert cost["difficulty"] in ("Medium", "Hard")

def test_build_simulator() -> None:
    player = Player(
        mastery_rank=14,
        completed_quests=[],
        owned_mods=["Serration", "Split Chamber", "Galvanized Chamber"],
        owned_arcanes=[],
        owned_weapons=[]
    )
    
    sim = BuildSimulator()
    result = sim.simulate_build(player, "Phenmor")
    assert result is not None
    assert result["current_score"] < result["potential_score"]
    assert "Primary Merciless" in result["missing"]

def test_weapon_tier_engine() -> None:
    player = Player(
        mastery_rank=14,
        completed_quests=[],
        owned_mods=[],
        owned_arcanes=[],
        owned_weapons=["Phenmor"]
    )
    
    wte = WeaponTierEngine()
    tiers = wte.get_weapon_tiers(player)
    
    # Phenmor is in S-tier list
    s_tier_weapons = {w["name"] for w in tiers["S"]}
    assert "Phenmor" in s_tier_weapons
    
    phenmor_data = next(w for w in tiers["S"] if w["name"] == "Phenmor")
    assert phenmor_data["owned"] is True

def test_synergy_engine() -> None:
    se = SynergyEngine()
    
    # Check Wisp + Phenmor synergy
    res = se.evaluate_synergy(
        warframe="Wisp",
        primary="Phenmor",
        secondary="Laetum",
        arcanes=["Primary Merciless"],
        mods=["Galvanized Chamber"]
    )
    assert res["rating"] == "Excellent"
    assert res["score"] >= 85

def test_progression_engine_sub_scores() -> None:
    player = Player(
        mastery_rank=15,
        completed_quests=["The Second Dream", "The War Within", "The Sacrifice", "Chains of Harrow", "The New War", "Angels of the Zariman"],
        owned_mods=["Serration", "Split Chamber", "Galvanized Chamber"],
        owned_arcanes=["Primary Merciless"],
        owned_weapons=["Phenmor"],
        steel_path_unlocked=True,
        arbitrations_unlocked=True,
        helminth_unlocked=True
    )
    
    pe = ProgressionEngine()
    assert pe.get_story_score(player) == 100.0
    assert pe.get_unlock_score(player) == 100.0
    assert pe.get_mastery_score(player) == 50.0
    
    readiness = pe.get_readiness_score(player)
    assert 0.0 < readiness <= 100.0
