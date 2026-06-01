from src.core.quest_graph import QuestGraph
from src.models import player

graph = QuestGraph()


class ProgressionEngine:

    def determine_stage(self, player):

        completed = set(player.completed_quests)

        if "The Second Dream" not in completed:
            return "early_game"

        if "The New War" not in completed:
            return "mid_game"

        if not player.steel_path_unlocked:
            return "late_game"

        return "end_game"

    def get_primary_goal(self, player):

        stage = self.determine_stage(player)

        goals = {
            "early_game": "Complete Main Story Quests",
            "mid_game": "Reach The New War",
            "late_game": "Unlock Steel Path",
            "end_game": "Optimize Builds"
        }

        return goals[stage]

    def get_next_story_quest(self, player):

        completed = set(player.completed_quests)

        for quest in graph.dependencies:

            if (
                quest not in completed
                and graph.is_unlocked(
                    quest,
                    completed
                )
            ):
                return quest

        return "Story Complete"

    def get_story_completion_percentage(self, player):

        total = len(graph.dependencies)

        completed = len([
            q
            for q in player.completed_quests
            if q in graph.dependencies
        ])

        return round(
            (completed / total) * 100,
            1
        )

    def get_readiness_score(self, player):

        story = self.get_story_completion_percentage(
            player
        )

        mods = min(
            len(player.owned_mods) * 10,
            100
        )

        return round(
            (story * 0.7) + (mods * 0.3),
            1
        )
    
    def get_mod_completion_percentage(self, player):

        important_mods = [
            "galvanized chamber",
            "galvanized aptitude",
            "serration",
            "split chamber"
        ]

        owned = {
            mod.lower()
            for mod in player.owned_mods
        }

        count = 0

        for mod in important_mods:

            if mod in owned:
                count += 1

        return round(
            (count / len(important_mods)) * 100,
            1
        )
    
    def get_arcane_completion_percentage(
        self,
        player
    ):

        important_arcanes = [
            "primary merciless"
        ]

        owned = {
            arcane.lower()
            for arcane in player.owned_arcanes
        }

        count = 0

        for arcane in important_arcanes:

            if arcane in owned:
                count += 1

        return round(
            (count / len(important_arcanes)) * 100,
            1
        )