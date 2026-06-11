from typing import Any

class ScoringEngine:
    """Class ScoringEngine documentation."""

    def calculate_score(self, recommendation: Any) -> Any:
        """Method calculate_score."""
        score = recommendation.power_gain * 0.5 + recommendation.account_progress * 0.3 + recommendation.time_efficiency * 0.2
        return round(score, 2)