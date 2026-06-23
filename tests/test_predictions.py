from unittest.mock import MagicMock
from src.models.player import Player
from src.core.prediction_engine import PredictionEngine

def test_prediction_engine_milestones() -> None:
    pe = PredictionEngine()
    
    # Mock snapshots to simulate a 2.0% daily readiness growth rate
    pe.se.get_snapshots = MagicMock(return_value=[
        {"timestamp": 1000, "readiness": 50.0, "date": "2026-06-21"},
        {"timestamp": 1000 + 86400, "readiness": 52.0, "date": "2026-06-22"}
    ])
    
    player = Player(
        mastery_rank=10,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False
    )
    
    res = pe.predict_milestones(player)
    assert res["daily_growth_rate"] == 2.0
    assert "days_to_steel_path" in res
    assert "days_to_archons" in res
    assert "days_to_endgame" in res
