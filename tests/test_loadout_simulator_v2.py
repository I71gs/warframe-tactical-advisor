from src.core.build_simulator import BuildSimulator
from src.models.player import Player

def test_build_simulator_v2() -> None:
    sim = BuildSimulator()
    player = Player(
        mastery_rank=10,
        steel_path_unlocked=True,
        arbitrations_unlocked=True,
        owned_mods=["Galvanized Chamber", "Galvanized Aptitude"],
        owned_arcanes=["Primary Merciless"]
    )
    res = sim.simulate_build(player, "Phenmor")
    assert res is not None
    assert res["weapon"] == "Phenmor"
    assert res["health"] > 0
    assert res["armor"] > 0
    assert res["shield"] > 0
    assert res["ehp"] > 0
    assert res["dps_score"] > 0
    assert res["crit_score"] > 0
    assert res["status_score"] > 0
    assert res["survivability_score"] > 0
    assert res["overall_rating"] > 0
