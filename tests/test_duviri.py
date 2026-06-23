from pathlib import Path
from src.core.duviri_engine import DuviriEngine

def test_duviri_engine(tmp_path: Path) -> None:
    state_file = tmp_path / "duviri_state.json"
    engine = DuviriEngine(state_path=state_file)

    # Test load defaults
    state = engine.load_duviri_state()
    assert state["intrinsics"]["Combat"] == 1
    assert state["pathos_clamps_owned"] == 0

    # Test percentage calculation
    pct = engine.get_progress_percentage(state)
    assert pct == 10.0 # (1+1+1+1) / 40 = 10%

    # Save custom state
    state["intrinsics"]["Combat"] = 10
    state["intrinsics"]["Opportunity"] = 4
    engine.save_duviri_state(state)

    reloaded = engine.load_duviri_state()
    assert reloaded["intrinsics"]["Combat"] == 10

    # Test recommendations
    recs = engine.get_recommendations(reloaded)
    assert len(recs) > 0
