from src.core.team_synergy_engine import TeamSynergyEngine

def test_team_synergy_calculations() -> None:
    tse = TeamSynergyEngine()
    
    # Check Wisp + Phenmor loadout
    res = tse.evaluate_composition(
        warframe="Wisp",
        primary="Phenmor",
        secondary="Laetum",
        melee="Praedos"
    )
    
    assert res["score"] >= 80
    assert res["rating"] == "Good"
    assert any("haste" in r.lower() or "fire rate" in r.lower() for r in [res["primary_rationale"], res["secondary_rationale"]])
    assert len(res["strengths"]) > 0
    assert len(res["weaknesses"]) > 0

def test_team_synergy_average() -> None:
    tse = TeamSynergyEngine()
    
    # Generic loadout
    res = tse.evaluate_composition(
        warframe="Excalibur",
        primary="Nataruk",
        secondary="Lex Prime",
        melee="Skana"
    )
    
    # Score should be significantly lower than the Wisp synergized meta loadout
    assert res["score"] < 75
    assert res["rating"] == "Average"
