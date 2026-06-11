from src.core.player_loader import PlayerLoader
from src.core.progression_engine import ProgressionEngine

player = PlayerLoader().load_player()

engine = ProgressionEngine()

print("Stage:")
print(engine.determine_stage(player))

print()

print("Primary Goal:")
print(engine.get_primary_goal(player))

print()
print("Next Quest:")
print(
    engine.get_next_story_quest(player)
)