from src.core.progression_ai import ProgressionAI
from src.models.player import Player

def test_progression_ai() -> None:
    ai = ProgressionAI()
    player = Player(mastery_rank=5, completed_quests=["The War Within"])
    plan = ai.get_session_plan(player)
    assert "today" in plan
    assert "why" in plan
    assert "gain" in plan
    assert "eta" in plan
