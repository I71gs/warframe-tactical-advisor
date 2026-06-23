from pathlib import Path
from src.core.resource_engine import ResourceEngine

def test_resource_planner_deficits(tmp_path: Path) -> None:
    state_file = tmp_path / "resource_state.json"
    re = ResourceEngine(state_path=state_file)
    
    # Save dummy inventory counts
    owned = {
        "Voidplumes": 5,
        "Entrati Lanthorn": 1,
        "Thrax Plasm": 0,
        "Credits": 50000,
        "Endo": 10000,
        "Forma": 0
    }
    re.save_owned_resources(owned)
    
    # Check plan for "Phenmor"
    # Recipe Phenmor: Voidplumes: 15, Entrati Lanthorn: 5, Thrax Plasm: 100
    plan = re.get_plan("Phenmor")
    
    voidplumes_plan = next(p for p in plan if p["resource"] == "Voidplumes")
    assert voidplumes_plan["required"] == 15
    assert voidplumes_plan["owned"] == 5
    assert voidplumes_plan["missing"] == 10
    
    lanthorn_plan = next(p for p in plan if p["resource"] == "Entrati Lanthorn")
    assert lanthorn_plan["missing"] == 4
    
    credits_plan = next(p for p in plan if p["resource"] == "Credits")
    assert credits_plan["missing"] == 0 # we have 50000, required is 30000
