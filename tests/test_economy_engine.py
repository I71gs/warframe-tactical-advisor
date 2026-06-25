from __future__ import annotations
from src.core.economy_engine import EconomyEngine

def test_economy_engine_plan() -> None:
    ee = EconomyEngine()
    plan = ee.get_economy_plan()
    
    assert len(plan) > 0
    currencies = {p["currency"] for p in plan}
    assert "Credits" in currencies
    assert "Endo" in currencies
    assert "Kuva" in currencies
    
    # Check that required values and best sources are present
    credits_info = next(p for p in plan if p["currency"] == "Credits")
    assert credits_info["required"] == 2500000
    assert "Index" in credits_info["source"]

def test_economy_engine_keys_mapping() -> None:
    ee = EconomyEngine()
    plan = ee.get_economy_plan()
    
    # Check that Vitus Essence and Voidplumes exist
    vitus = next(p for p in plan if p["currency"] == "Vitus Essence")
    assert vitus["required"] == 80
    plumes = next(p for p in plan if p["currency"] == "Voidplumes")
    assert plumes["required"] == 50
