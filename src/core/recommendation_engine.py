from src.models.recommendation import Recommendation
from src.core.knowledge_base import KnowledgeBase
from src.core.quest_graph import QuestGraph
from src.core.progression_engine import ProgressionEngine

kb = KnowledgeBase()
graph = QuestGraph()
progression = ProgressionEngine()


class RecommendationEngine:

    def generate_recommendations(self, player):

        recommendations = []

        completed = set(player.completed_quests)

        # ---------------------------------
        # PROGRESSION ANALYSIS
        # ---------------------------------

        stage = progression.determine_stage(player)

        primary_goal = progression.get_primary_goal(player)

        next_quest = progression.get_next_story_quest(player)

        # ---------------------------------
        # PRIMARY OBJECTIVE
        # ---------------------------------

        if next_quest:

            recommendations.append(
                Recommendation(
                    action=f"Complete {next_quest}",
                    reason=f"Primary progression objective ({stage})",
                    power_gain=100,
                    account_progress=100,
                    time_efficiency=90
                )
            )

        # ---------------------------------
        # STAGE SPECIFIC OBJECTIVES
        # ---------------------------------

        if stage == "early_game":

            recommendations.append(
                Recommendation(
                    action="Clear Star Chart",
                    reason="Unlock core progression",
                    power_gain=80,
                    account_progress=95,
                    time_efficiency=85
                )
            )

        elif stage == "mid_game":

            recommendations.append(
                Recommendation(
                    action="Prepare For The New War",
                    reason="Major story milestone",
                    power_gain=90,
                    account_progress=95,
                    time_efficiency=80
                )
            )

        elif stage == "late_game":

            recommendations.append(
                Recommendation(
                    action="Farm Arbitrations",
                    reason="Unlock Galvanized Mods",
                    power_gain=95,
                    account_progress=90,
                    time_efficiency=80
                )
            )

            if not player.steel_path_unlocked:

                recommendations.append(
                    Recommendation(
                        action="Unlock Steel Path",
                        reason="Access endgame content",
                        power_gain=100,
                        account_progress=100,
                        time_efficiency=60
                    )
                )

        elif stage == "end_game":

            recommendations.append(
                Recommendation(
                    action="Optimize Builds",
                    reason="Focus on endgame efficiency",
                    power_gain=90,
                    account_progress=70,
                    time_efficiency=95
                )
            )

        # ---------------------------------
        # MOD RECOMMENDATIONS
        # ---------------------------------

        owned_mods = {
            mod.lower()
            for mod in player.owned_mods
        }

        for mod in kb.mods:

            if mod["name"].lower() not in owned_mods:

                recommendations.append(
                    Recommendation(
                        action=f"Acquire {mod['name']}",
                        reason=f"Important mod from {mod['source']}",
                        power_gain=mod["importance"],
                        account_progress=80,
                        time_efficiency=70
                    )
                )
        
        # ---------------------------------
        # ARCANE RECOMMENDATIONS
        # ---------------------------------

        owned_arcanes = {
            arcane.lower()
            for arcane in player.owned_arcanes
        }

        if "primary merciless" not in owned_arcanes:

            recommendations.append(
                Recommendation(
                    action="Get Primary Merciless",
                    reason="Top tier weapon arcane",
                    power_gain=90,
                    account_progress=80,
                    time_efficiency=85
                )
            )

        # ---------------------------------
        # SORT BY SCORE
        # ---------------------------------

        recommendations.sort(
            key=lambda r: r.calculate_score(),
            reverse=True
        )

        return recommendations
    

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