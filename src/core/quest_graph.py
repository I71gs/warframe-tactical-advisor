from __future__ import annotations
from typing import Iterable

class QuestGraph:
    """Represents story quest dependencies and unlock requirements."""

    def __init__(self) -> None:
        """Initialize story quest dependency graph."""
        self.dependencies = {
            'The Second Dream': [],
            'The War Within': ['The Second Dream'],
            'Chains of Harrow': ['The War Within'],
            'The Sacrifice': ['The War Within'],
            'The New War': ['The Sacrifice', 'Chains of Harrow'],
            'Angels of the Zariman': ['The New War'],
        }

    def get_prerequisites(self, quest: str) -> list[str]:
        """Return prerequisite quests for a given quest."""
        return self.dependencies.get(quest, [])

    def is_unlocked(self, quest: str, completed_quests: Iterable[str]) -> bool:
        """Return whether a quest is unlocked by completed prerequisites."""
        for req in self.get_prerequisites(quest):
            if req not in completed_quests:
                return False
        return True
