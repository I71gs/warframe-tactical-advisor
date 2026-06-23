from __future__ import annotations
from src.core.session_optimizer import SessionOptimizer
from src.models.player import Player

def test_session_optimizer() -> None:
    player = Player(
        mastery_rank=12,
        steel_path_unlocked=False,
        completed_quests=["The Second Dream", "The War Within"],
        owned_mods=["Serration"],
        owned_arcanes=[],
        owned_weapons=["Laetum"]
    )
    optimizer = SessionOptimizer()
    session = optimizer.optimize_session(player, duration_minutes=120)

    assert "sequence" in session
    assert len(session["sequence"]) > 0
    assert "power_gain_per_hour" in session
