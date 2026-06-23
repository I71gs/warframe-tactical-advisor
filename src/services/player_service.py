from __future__ import annotations
from typing import TYPE_CHECKING
from src.core.player_loader import PlayerLoader
from src.core.profile_manager import ProfileManager
from src.database.database import DatabaseManager
from src.models.player import Player

if TYPE_CHECKING:
    from src.core.app_context import AppContext

class PlayerService:
    """Interacts with DatabaseManager, PlayerLoader, and ProfileManager to manage player identity."""

    def __init__(self, context: AppContext) -> None:
        self.context = context

    def get_player(self) -> Player:
        return PlayerLoader().load_player()

    def add_completed_quest(self, quest_name: str) -> None:
        DatabaseManager().add_completed_quest(quest_name)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def remove_completed_quest(self, quest_name: str) -> None:
        DatabaseManager().remove_completed_quest(quest_name)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def add_owned_mod(self, mod_name: str) -> None:
        DatabaseManager().add_owned_mod(mod_name)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def remove_owned_mod(self, mod_name: str) -> None:
        DatabaseManager().remove_owned_mod(mod_name)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def add_owned_arcane(self, arcane_name: str) -> None:
        DatabaseManager().add_owned_arcane(arcane_name)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def remove_owned_arcane(self, arcane_name: str) -> None:
        DatabaseManager().remove_owned_arcane(arcane_name)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def add_owned_weapon(self, weapon_name: str) -> None:
        DatabaseManager().add_owned_weapon(weapon_name)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def remove_owned_weapon(self, weapon_name: str) -> None:
        DatabaseManager().remove_owned_weapon(weapon_name)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def save_player(self, mastery_rank: int, steel_path_unlocked: bool, arbitrations_unlocked: bool = False, helminth_unlocked: bool = False) -> None:
        DatabaseManager().save_player(mastery_rank, steel_path_unlocked, arbitrations_unlocked, helminth_unlocked)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def backup_profile(self) -> str:
        # In TA, ProfileManager().backup_profile() or DatabaseManager().backup_database() creates the backup.
        # Let's import ProfileManager directly to execute the backup.
        from src.core.profile_manager import ProfileManager
        dest = ProfileManager().backup_profile()
        return str(dest)

    def switch_profile(self, profile_name: str) -> None:
        from src.core.settings_manager import SettingsManager
        sm = SettingsManager()
        sm.update(current_profile=profile_name)
        sm.save()
        self.context.event_bus.publish("ACCOUNT_SWITCHED", {"profile": profile_name})
