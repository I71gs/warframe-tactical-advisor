from src.core.economy_engine import EconomyEngine

def test_economy_plan() -> None:
    ee = EconomyEngine()
    plan = ee.get_economy_plan()
    assert len(plan) > 0
    assert any(p["currency"] == "Credits" for p in plan)
    assert any(p["currency"] == "Endo" for p in plan)
    for p in plan:
        assert "required" in p
        assert "owned" in p
        assert "missing" in p
        assert "farm_hours" in p
