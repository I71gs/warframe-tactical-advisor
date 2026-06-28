from __future__ import annotations
from src.core.economy_engine import EconomyEngine


def test_economy_engine_plan() -> None:
    """Economy plan returns items keyed by 'resource' (renamed from 'currency' in v2)."""
    ee = EconomyEngine()
    plan = ee.get_economy_plan()

    assert len(plan) > 0
    resources = {p["resource"] for p in plan}
    assert "Credits" in resources
    assert "Endo" in resources
    assert "Kuva" in resources

    # Check structural fields
    credits_info = next(p for p in plan if p["resource"] == "Credits")
    assert credits_info["required"] == 2_500_000
    assert "best_node" in credits_info
    assert "farm_hours" in credits_info


def test_economy_engine_keys_mapping() -> None:
    """Vitus Essence, Voidplumes, and new resources are all present with correct targets."""
    ee = EconomyEngine()
    plan = ee.get_economy_plan()

    vitus = next(p for p in plan if p["resource"] == "Vitus Essence")
    assert vitus["required"] == 80

    plumes = next(p for p in plan if p["resource"] == "Voidplumes")
    assert plumes["required"] == 50

    # v2 new resources
    orokin = next(p for p in plan if p["resource"] == "Orokin Cell")
    assert orokin["required"] > 0

    neural = next(p for p in plan if p["resource"] == "Neural Sensors")
    assert neural["required"] > 0


def test_economy_goal_plan() -> None:
    """get_resource_farm_plan returns a goal-based breakdown for known goals."""
    ee = EconomyEngine()
    plan = ee.get_resource_farm_plan("wisp")
    assert plan["found"] is True
    assert "resources" in plan
    assert plan["total_farm_hours"] >= 0
    assert len(plan["recommended_boosters"]) > 0
    # Should contain Credits and Hexenon (Wisp requires Hexenon)
    resource_names = {r["resource"] for r in plan["resources"]}
    assert "Hexenon" in resource_names
    assert "Credits" in resource_names


def test_economy_goal_plan_not_found() -> None:
    ee = EconomyEngine()
    plan = ee.get_resource_farm_plan("NonExistentGoalXYZ")
    assert plan["found"] is False
    assert "message" in plan


def test_economy_bottleneck_resources() -> None:
    """get_bottleneck_resources returns top N resources with non-zero missing qty."""
    ee = EconomyEngine()
    bottlenecks = ee.get_bottleneck_resources(top_n=3)
    assert isinstance(bottlenecks, list)
    assert len(bottlenecks) <= 3
    for b in bottlenecks:
        assert b["missing"] > 0
        assert "resource" in b
