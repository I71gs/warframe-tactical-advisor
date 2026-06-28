from src.core.mastery_planner import MasteryPlanner
from src.models.player import Player


def test_mastery_plan_basic() -> None:
    """calculate_plan returns expected keys and non-zero suggestions."""
    mp = MasteryPlanner()
    player = Player(mastery_rank=5, owned_weapons=["Phenmor"])
    plan = mp.calculate_plan(player)

    assert plan["current_mr"] == 5
    assert plan["next_mr"] == 6
    assert plan["xp_needed"] > 0
    assert "xp_to_mr30" in plan
    assert len(plan["weapons_to_level"]) > 0
    # v2: frames_to_build comes from the full WARFRAME_ROSTER — should be non-empty
    assert len(plan["frames_to_build"]) > 0


def test_mastery_plan_excludes_owned() -> None:
    """Owned weapons and warframes are excluded from suggestions."""
    mp = MasteryPlanner()
    owned_weapons = ["Phenmor", "Laetum", "Torid"]
    player = Player(mastery_rank=10, owned_weapons=owned_weapons)
    plan = mp.calculate_plan(player)

    weapon_names = [w["name"] for w in plan["weapons_to_level"]]
    for ow in owned_weapons:
        assert ow not in weapon_names


def test_fastest_mr_path() -> None:
    """get_fastest_mr_path returns sorted items favouring easy acquisition."""
    mp = MasteryPlanner()
    player = Player(mastery_rank=8)
    path = mp.get_fastest_mr_path(player, limit=10)
    assert len(path) > 0
    for item in path:
        assert "name" in item
        assert "xp" in item
        assert item["xp"] > 0


def test_mr_forecast() -> None:
    """get_mr_forecast returns milestone projections."""
    mp = MasteryPlanner()
    player = Player(mastery_rank=10)
    forecast = mp.get_mr_forecast(player, items_per_day=3)
    assert forecast["current_mr"] == 10
    assert "days_to_mr30" in forecast
    assert "mr_milestones" in forecast
    milestones = forecast["mr_milestones"]
    assert any("MR" in k for k in milestones)


def test_category_breakdown() -> None:
    """get_category_breakdown returns per-category XP potential."""
    mp = MasteryPlanner()
    player = Player(mastery_rank=5)
    breakdown = mp.get_category_breakdown(player)
    assert isinstance(breakdown, dict)
    # Should at least have Warframe and Primary Weapon categories
    assert any("Warframe" in k or "Primary" in k for k in breakdown)
    for cat, data in breakdown.items():
        assert data["count"] >= 0
        assert data["xp_potential"] >= 0
