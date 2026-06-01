from src.database.database import DatabaseManager
from src.models.player import Player


class PlayerLoader:

    def load_player(self):

        db = DatabaseManager()

        player_row = db.get_player()

        mastery_rank = 0
        steel_path_unlocked = False

        if player_row:

            mastery_rank = player_row[0]
            steel_path_unlocked = bool(player_row[1])

        return Player(
            mastery_rank=mastery_rank,
            steel_path_unlocked=steel_path_unlocked,
            completed_quests=db.get_completed_quests(),
            owned_mods=db.get_owned_mods(),
            owned_arcanes=db.get_owned_arcanes()
        )