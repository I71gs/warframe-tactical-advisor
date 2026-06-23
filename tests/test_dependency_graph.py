from src.models.player import Player
from src.core.dependency_graph_engine import DependencyGraphEngine

def test_dependency_graph_building() -> None:
    # Player with no MR and no quests completed
    player = Player(
        mastery_rank=2,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False
    )
    
    dge = DependencyGraphEngine()
    
    # Resolve tree for "Phenmor"
    graph = dge.get_graph("Phenmor", player)
    assert graph["name"] == "Phenmor"
    assert graph["status"] == "locked"
    
    # Children should include Mastery Rank 14 and quest Angels of the Zariman
    child_names = {c["name"] for c in graph["children"]}
    assert "Mastery Rank 14" in child_names
    assert "Angels of the Zariman" in child_names
    
    # Since player is MR 2, the MR 14 node should be locked
    mr_node = next(c for c in graph["children"] if c["name"] == "Mastery Rank 14")
    assert mr_node["status"] == "locked"
