from __future__ import annotations
from src.database.database import DatabaseManager
from src.models.player import Player

class PlayerLoader:
    """Loads player profile state from the local database."""

    def load_player(self) -> Player:
        """Return the current saved player profile."""
        db = DatabaseManager()
        player_row = db.get_player()
        mastery_rank = 0
        steel_path_unlocked = False
        arbitrations_unlocked = False
        helminth_unlocked = False
        if player_row is not None:
            if len(player_row) >= 4:
                mastery_rank, steel_path_unlocked_value, arbitrations_unlocked_value, helminth_unlocked_value = player_row
                steel_path_unlocked = bool(steel_path_unlocked_value)
                arbitrations_unlocked = bool(arbitrations_unlocked_value)
                helminth_unlocked = bool(helminth_unlocked_value)
            elif len(player_row) == 2:
                mastery_rank, steel_path_unlocked_value = player_row
                steel_path_unlocked = bool(steel_path_unlocked_value)
        return Player(
            mastery_rank=mastery_rank,
            steel_path_unlocked=steel_path_unlocked,
            arbitrations_unlocked=arbitrations_unlocked,
            helminth_unlocked=helminth_unlocked,
            completed_quests=db.get_completed_quests(),
            owned_mods=db.get_owned_mods(),
            owned_arcanes=db.get_owned_arcanes(),
            owned_weapons=db.get_owned_weapons(),
        )
