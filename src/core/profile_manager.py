from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from src.core.player_loader import PlayerLoader
from src.database.database import DatabaseManager

class ProfileManager:
    """Handles profile export, import, and database restore operations."""

    def export_profile(self, filename: str = 'profile.json') -> None:
        """Export the current saved player profile to JSON."""
        player = PlayerLoader().load_player()
        data = {
            'version': '1.0',
            'profile': {
                'mastery_rank': player.mastery_rank,
                'steel_path_unlocked': player.steel_path_unlocked,
                'arbitrations_unlocked': player.arbitrations_unlocked,
                'helminth_unlocked': player.helminth_unlocked,
                'completed_quests': player.completed_quests,
                'owned_mods': player.owned_mods,
                'owned_arcanes': player.owned_arcanes,
                'owned_weapons': player.owned_weapons,
            },
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def import_profile(self, filename: str = 'profile.json') -> None:
        """Import a profile JSON file into the local database."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict) and 'version' in data:
            version = data.get('version')
            if version != '1.0':
                raise ValueError(f'Unsupported profile version: {version}')
            profile = data.get('profile', {})
        else:
            profile = data
        db = DatabaseManager()
        db.cursor.execute('DELETE FROM players')
        db.cursor.execute('DELETE FROM completed_quests')
        db.cursor.execute('DELETE FROM owned_mods')
        db.cursor.execute('DELETE FROM owned_arcanes')
        db.cursor.execute('DELETE FROM owned_weapons')
        db.connection.commit()
        db.save_player(
            profile.get('mastery_rank', 0),
            profile.get('steel_path_unlocked', False),
            profile.get('arbitrations_unlocked', False),
            profile.get('helminth_unlocked', False)
        )
        for quest in profile.get('completed_quests', []):
            db.add_completed_quest(quest)
        for mod in profile.get('owned_mods', []):
            db.add_owned_mod(mod)
        for arcane in profile.get('owned_arcanes', []):
            db.add_owned_arcane(arcane)
        for weapon in profile.get('owned_weapons', []):
            db.add_owned_weapon(weapon)
