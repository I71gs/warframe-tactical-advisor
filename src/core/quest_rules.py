from typing import Any

class QuestRules:
    """Class QuestRules documentation."""

    @staticmethod
    def can_start_quest(quest: Any, completed_quests: Any) -> Any:
        """Method can_start_quest."""
        for requirement in quest['requires']:
            if requirement not in completed_quests:
                return False
        return True