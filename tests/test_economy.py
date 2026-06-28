from src.core.economy_engine import EconomyEngine


def test_economy_plan() -> None:
    ee = EconomyEngine()
    plan = ee.get_economy_plan()
    assert len(plan) > 0
    # Key renamed from 'currency' to 'resource' in v2
    assert any(p["resource"] == "Credits" for p in plan)
    assert any(p["resource"] == "Endo" for p in plan)
    for p in plan:
        assert "required" in p
        assert "owned" in p
        assert "missing" in p
        assert "farm_hours" in p
        assert "best_node" in p
        assert "resource" in p
