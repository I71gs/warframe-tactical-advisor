from src.core.data_loader import load_json


class KnowledgeBase:

    def __init__(self):

        self.quests = load_json(
            "data/quests.json"
        )

        self.mods = load_json(
            "data/mods.json"
        )

        self.arcanes = load_json(
            "data/arcanes.json"
        )