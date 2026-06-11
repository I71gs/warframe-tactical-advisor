from __future__ import annotations

class Player:
    """Represents a Warframe player's profile, inventory, and progression state."""

    def __init__(
        self,
        mastery_rank: int,
        completed_quests: list[str] | None = None,
        owned_mods: list[str] | None = None,
        owned_arcanes: list[str] | None = None,
        owned_weapons: list[str] | None = None,
        steel_path_unlocked: bool = False,
        arbitrations_unlocked: bool = False,
        helminth_unlocked: bool = False,
    ) -> None:
        """Initialize a new player profile."""
        self.mastery_rank = mastery_rank
        self.completed_quests = completed_quests or []
        self.owned_mods = owned_mods or []
        self.owned_arcanes = owned_arcanes or []
        self.owned_weapons = owned_weapons or []
        self.steel_path_unlocked = steel_path_unlocked
        self.arbitrations_unlocked = arbitrations_unlocked
        self.helminth_unlocked = helminth_unlocked
