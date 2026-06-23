from src.core.circuit_engine import CircuitEngine
from src.models.player import Player

def test_circuit_recommendation() -> None:
    ce = CircuitEngine()
    player = Player(mastery_rank=10, steel_path_unlocked=False)
    rec = ce.get_circuit_recommendation(player)
    assert "week" in rec
    assert len(rec["rotation_items"]) > 0
    assert rec["recommended_pick"] is not None
    assert rec["readiness_status"].startswith("Locked")

    player_sp = Player(mastery_rank=15, steel_path_unlocked=True)
    rec_sp = ce.get_circuit_recommendation(player_sp)
    assert rec_sp["readiness_score"] >= 0.0
