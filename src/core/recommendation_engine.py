from operator import mod
from src.models.recommendation import Recommendation
from src.core.knowledge_base import KnowledgeBase 

kb = KnowledgeBase()

class RecommendationEngine:

    def generate_recommendations(self, player):

        recommendations = []

        for mod in kb.mods:

            recommendations.append(
                Recommendation(
                    action=f"Acquire {mod['name']}",
                    reason=f"Important mod from {mod['source']}",
                    power_gain=mod['importance'],
                    account_progress=80,
                    time_efficiency=70
        )
    )

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

        recommendations.append(
            Recommendation(
                action="Farm Arbitrations",
                reason="Unlock Galvanized Mods.",
                power_gain=90,
                account_progress=85,
                time_efficiency=80
            )
        )

        recommendations.append(
            Recommendation(
                action="Get Primary Merciless",
                reason="Huge weapon damage increase.",
                power_gain=85,
                account_progress=75,
                time_efficiency=90
            )
        )

        if not player.steel_path_unlocked:

            recommendations.append(
                Recommendation(
                    action="Unlock Steel Path",
                    reason="Unlock endgame progression.",
                    power_gain=95,
                    account_progress=100,
                    time_efficiency=70
                )
            )
    

        return recommendations