class ScoringEngine:

    def calculate_score(self, recommendation):

        score = (
            recommendation.power_gain * 0.5
            + recommendation.account_progress * 0.3
            + recommendation.time_efficiency * 0.2
        )

        return round(score, 2)