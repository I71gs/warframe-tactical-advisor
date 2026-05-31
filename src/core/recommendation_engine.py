from src.models.recommendation import Recommendation
from src.core.knowledge_base import KnowledgeBase


class RecommendationEngine:

    def __init__(self):
        self.kb = KnowledgeBase()

    def generate_recommendations(self, player):

        recommendations = []

        # Recommendations from mods.json
        for mod in self.kb.mods:

            if mod["name"] in player.owned_mods:
                continue

            recommendations.append(
                Recommendation(
                    action=f"Acquire {mod['name']}",
                    reason=f"Important mod from {mod['source']}",
                    power_gain=mod['importance'],
                    account_progress=80,
                    time_efficiency=70
                )
            )


        for quest in self.kb.quests:
            if quest["name"] in player.completed_quests:
                continue

            recommendations.append(
                Recommendation(
                    action=f"Complete {quest['name']}",
                    reason="Important story progression.",
                    power_gain=quest["importance"],
                    account_progress=100,
                    time_efficiency=60
                )
            )
        # Steel Path recommendation
        if not player.steel_path_unlocked:

            recommendations.append(
                Recommendation(
                    action="Unlock Steel Path",
                    reason="Access endgame content.",
                    power_gain=95,
                    account_progress=100,
                    time_efficiency=70
                )
            )

        # Arbitration recommendation
        recommendations.append(
            Recommendation(
                action="Farm Arbitrations",
                reason="Unlock Galvanized Mods.",
                power_gain=90,
                account_progress=85,
                time_efficiency=80
            )
        )

        # Arcane recommendation
        recommendations.append(
            Recommendation(
                action="Get Primary Merciless",
                reason="Huge weapon damage increase.",
                power_gain=85,
                account_progress=75,
                time_efficiency=90
            )
        )

        # Remove duplicates automatically
        unique_recommendations = {}

        for rec in recommendations:
            unique_recommendations[rec.action] = rec

        return list(unique_recommendations.values())