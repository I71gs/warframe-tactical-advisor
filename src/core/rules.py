class ProgressionRules:

    @staticmethod
    def can_access_steel_path(player):

        return (
            "The New War" in player.completed_quests
        )

    @staticmethod
    def can_access_arbitrations(player):

        return (
            "The New War" in player.completed_quests
        )