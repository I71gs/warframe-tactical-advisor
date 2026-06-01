# debug_player.py

from src.core.player_loader import PlayerLoader

player = PlayerLoader().load_player()

print("QUESTS:")
print(player.completed_quests)

print("\nMODS:")
print(player.owned_mods)