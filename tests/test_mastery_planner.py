from src.core.mastery_planner import MasteryPlanner
from src.models.player import Player

def test_mastery_plan() -> None:
    mp = MasteryPlanner()
    player = Player(mastery_rank=5, owned_weapons=["Phenmor"])
    plan = mp.calculate_plan(player)
    assert plan["current_mr"] == 5
    assert plan["next_mr"] == 6
    assert plan["xp_needed"] > 0
    assert len(plan["weapons_to_level"]) > 0
    assert len(plan["frames_to_build"]) > 0
