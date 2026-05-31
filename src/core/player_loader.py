from src.models.player import Player
from src.database.database import DatabaseManager


class PlayerLoader:

    def load_player(self):

        db = DatabaseManager()

        completed_quests = (
            db.get_completed_quests()
        )

        owned_mods = (
            db.get_owned_mods()
        )

        return Player(
            mastery_rank=10,
            completed_quests=completed_quests,
            owned_mods=owned_mods,
            steel_path_unlocked=False
        )