from src.models.recommendation import Recommendation


class RecommendationEngine:

    def generate_recommendations(self, player):

        recommendations = []

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

        return recommendations