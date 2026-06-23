from pathlib import Path
from src.core.incarnon_engine import IncarnonEngine
from src.models.player import Player

def test_incarnon_engine(tmp_path: Path) -> None:
    state_file = tmp_path / "incarnon_state.json"
    engine = IncarnonEngine(state_path=state_file)

    # Initial state should be loaded with defaults
    state = engine.load_incarnon_state()
    assert "Phenmor" in state
    assert len(state["Phenmor"]) == 5
    assert not any(state["Phenmor"])

    # Update state
    state["Phenmor"][0] = True
    engine.save_incarnon_state(state)

    # Reload state
    reloaded = engine.load_incarnon_state()
    assert reloaded["Phenmor"][0] is True

    # Test weapon status
    player = Player(mastery_rank=15, owned_weapons=["Phenmor"])
    status = engine.get_weapon_status(player, "Phenmor")
    assert status["owned"] is True
    assert status["mr_requirement_met"] is True
    assert status["evolutions"][0]["completed"] is True
    assert status["evolutions"][1]["completed"] is False
