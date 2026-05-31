from src.models.player import Player
from src.core.rules import ProgressionRules

player = Player(
    mastery_rank=10,
    completed_quests=["The New War"],
    owned_mods=[],
    steel_path_unlocked=False
)

print(
    "Steel Path:",
    ProgressionRules.can_access_steel_path(player)
)

print(
    "Arbitrations:",
    ProgressionRules.can_access_arbitrations(player)
)