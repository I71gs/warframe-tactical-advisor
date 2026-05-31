class QuestRules:

    @staticmethod
    def can_start_quest(
        quest,
        completed_quests
    ):

        for requirement in quest["requires"]:

            if requirement not in completed_quests:
                return False

        return True