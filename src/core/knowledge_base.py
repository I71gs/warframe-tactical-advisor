from __future__ import annotations
from typing import Any
from src.core.data_loader import load_json

class KnowledgeBase:
    """Loads offline knowledge assets for quests, mods, and arcanes."""

    def __init__(self) -> None:
        """Initialize the knowledge base from JSON assets."""
        self.quests: list[dict[str, Any]] = load_json('data/quests.json')
        self.mods: list[dict[str, Any]] = load_json('data/mods.json')
        self.arcanes: list[dict[str, Any]] = load_json('data/arcanes.json')
