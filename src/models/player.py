from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Player:
    """Represents a Warframe player's full profile, inventory, and progression state."""

    # Core identity
    mastery_rank: int
    steel_path_unlocked: bool = False
    arbitrations_unlocked: bool = False
    helminth_unlocked: bool = False

    # Legacy flat lists (kept for backward compatibility)
    completed_quests: list[str] = field(default_factory=list)
    owned_mods: list[str] = field(default_factory=list)
    owned_arcanes: list[str] = field(default_factory=list)
    owned_weapons: list[str] = field(default_factory=list)

    # v2 Collection — dicts keyed by item name, value is inventory detail dict
    # Each dict: {name, owned, rank, forma_count, has_reactor, polarities, notes, acquisition}
    warframe_inventory: list[dict] = field(default_factory=list)
    companion_inventory: list[dict] = field(default_factory=list)
    archwing_inventory: list[dict] = field(default_factory=list)
    necramech_inventory: list[dict] = field(default_factory=list)
    amp_inventory: list[dict] = field(default_factory=list)

    # Focus & operator
    focus_schools: list[dict] = field(default_factory=list)  # [{school, active, focus_spent}]
    active_focus_school: str = ""

    # Railjack
    intrinsics: dict[str, int] = field(default_factory=dict)   # {category: rank}
    railjack_upgrades: list[dict] = field(default_factory=list) # [{component, tier, notes}]

    # Convenience helpers
    @property
    def owned_warframes(self) -> list[str]:
        """Return names of owned Warframes from the v2 inventory."""
        return [e["name"] for e in self.warframe_inventory if e.get("owned")]

    @property
    def owned_companions(self) -> list[str]:
        """Return names of owned companions from the v2 inventory."""
        return [e["name"] for e in self.companion_inventory if e.get("owned")]

    @property
    def total_intrinsic_rank(self) -> int:
        """Sum of all Railjack intrinsic ranks."""
        return sum(self.intrinsics.values())
