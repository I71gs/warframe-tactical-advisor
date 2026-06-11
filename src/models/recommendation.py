from __future__ import annotations

class Recommendation:
    """Represents a progression recommendation generated for a player."""

    def __init__(
        self,
        action: str,
        reason: str,
        power_gain: float,
        account_progress: float,
        time_efficiency: float,
        category: str = 'GENERAL',
    ) -> None:
        """Initialize a recommendation scorecard."""
        self.action = action
        self.reason = reason
        self.power_gain = power_gain
        self.account_progress = account_progress
        self.time_efficiency = time_efficiency
        self.category = category

    def calculate_score(self) -> float:
        """Calculate a weighted score for recommendation ranking."""
        return self.power_gain * 0.4 + self.account_progress * 0.4 + self.time_efficiency * 0.2
