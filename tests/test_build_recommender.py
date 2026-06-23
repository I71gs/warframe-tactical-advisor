from src.models.player import Player
from src.core.build_recommender import BuildRecommender

def test_build_recommender_scoring() -> None:
    # Player has only partial mods for Phenmor
    player = Player(
        mastery_rank=14,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False,
        owned_mods=["Serration", "Split Chamber"],
        owned_arcanes=[],
        owned_weapons=[]
    )
    
    br = BuildRecommender()
    rec = br.recommend_build(player, "Phenmor")
    
    assert rec is not None
    assert rec["weapon"] == "Phenmor"
    assert "Mod: Galvanized Chamber" in rec["missing"]
    assert "Arcane: Primary Merciless" in rec["missing"]
    
    # Check that current score is lower than potential
    assert rec["current_score"] < rec["potential_score"]
    assert rec["current_score"] > 0
    assert "+" in rec["gain"]
