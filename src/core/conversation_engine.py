from __future__ import annotations
from typing import Any

class ConversationEngine:
    """Manages natural language conversation state and query logs."""

    def __init__(self) -> None:
        self.history: list[dict[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        """Log a message exchange in the conversation history."""
        self.history.append({"role": role, "content": content})

    def get_history(self) -> list[dict[str, str]]:
        """Retrieve full conversation log."""
        return self.history

    def clear(self) -> None:
        """Clear conversation history."""
        self.history.clear()
