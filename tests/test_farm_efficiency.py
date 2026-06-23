from src.models.player import Player
from src.core.farm_efficiency_engine import FarmEfficiencyEngine

def test_farm_efficiency_routes() -> None:
    player = Player(
        mastery_rank=8,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False
    )
    
    fee = FarmEfficiencyEngine()
    routes = fee.get_routes(player)
    
    assert len(routes) >= 3
    # First route should be Steel Path Readiness since arbitrations is not unlocked (CRITICAL priority)
    assert routes[0]["name"] == "Steel Path Readiness Route (Galvanized Mods)"
    assert routes[0]["active"] is True
    assert routes[0]["priority"] == "CRITICAL"
