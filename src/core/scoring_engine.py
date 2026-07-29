from typing import Any

class ScoringEngine:
    """Class ScoringEngine documentation."""

    def calculate_score(self, recommendation: Any) -> Any:
        """Method calculate_score."""
        try:
            from src.core.settings_manager import SettingsManager
            settings = SettingsManager()
            priority = settings.get('priority_level', 'balanced')
        except Exception:
            priority = 'balanced'

        if priority == 'power':
            w_power, w_progress, w_eff = 0.7, 0.15, 0.15
        elif priority == 'progress':
            w_power, w_progress, w_eff = 0.15, 0.7, 0.15
        elif priority == 'efficiency':
            w_power, w_progress, w_eff = 0.15, 0.15, 0.7
        else:  # balanced
            w_power, w_progress, w_eff = 0.5, 0.3, 0.2

        score = (
            recommendation.power_gain * w_power +
            recommendation.account_progress * w_progress +
            recommendation.time_efficiency * w_eff
        )
        return round(score, 2)