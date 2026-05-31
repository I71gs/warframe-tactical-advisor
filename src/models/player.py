class Player:

    def __init__(
        self,
        mastery_rank,
        completed_quests=None,
        owned_mods=None,
        owned_arcanes=None,
        owned_weapons=None,
        steel_path_unlocked=False,
        arbitrations_unlocked=False,
        helminth_unlocked=False
    ):

        self.mastery_rank = mastery_rank

        self.completed_quests = (
            completed_quests or []
        )

        self.owned_mods = (
            owned_mods or []
        )

        self.owned_arcanes = (
            owned_arcanes or []
        )

        self.owned_weapons = (
            owned_weapons or []
        )

        self.steel_path_unlocked = (
            steel_path_unlocked
        )

        self.arbitrations_unlocked = (
            arbitrations_unlocked
        )

        self.helminth_unlocked = (
            helminth_unlocked
        )