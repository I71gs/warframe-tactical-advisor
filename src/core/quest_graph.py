class QuestGraph:

    def __init__(self):

        # Directed dependency map
        # key = quest
        # value = prerequisites

        self.dependencies = {
            "The Second Dream": [],
            "The War Within": ["The Second Dream"],
            "Chains of Harrow": ["The War Within"],
            "The Sacrifice": ["The War Within"],
            "The New War": ["The Sacrifice", "Chains of Harrow"],
            "Angels of the Zariman": ["The New War"],
        }

    def get_prerequisites(self, quest):

        return self.dependencies.get(quest, [])

    def is_unlocked(self, quest, completed_quests):

        for req in self.get_prerequisites(quest):
            if req not in completed_quests:
                return False
        return True