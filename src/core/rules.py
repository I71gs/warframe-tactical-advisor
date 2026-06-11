from typing import Any

class ProgressionRules:
    """Class ProgressionRules documentation."""

    @staticmethod
    def can_access_steel_path(player: Any) -> Any:
        """Method can_access_steel_path."""
        return 'The New War' in player.completed_quests

    @staticmethod
    def can_access_arbitrations(player: Any) -> Any:
        """Method can_access_arbitrations."""
        return 'The New War' in player.completed_quests