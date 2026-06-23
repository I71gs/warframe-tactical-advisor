from __future__ import annotations
from pathlib import Path
import shutil
import sqlite3
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / 'player.db'
BACKUP_DIR = ROOT / 'backups'
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
SCHEMA_VERSION = '1'

class DatabaseManager:
    """Manages local SQLite persistence for player profiles and progress."""

    def __init__(self, db_path: Path | str | None = None, timeout: int = 5) -> None:
        """Open or create the SQLite database file."""
        if db_path is not None:
            self.db_path = Path(db_path)
        else:
            from src.core.settings_manager import SettingsManager
            profile = SettingsManager().get('current_profile', 'default')
            if profile == 'default':
                self.db_path = DB_PATH
            else:
                self.db_path = ROOT / f'player_{profile}.db'
        self.connection = sqlite3.connect(str(self.db_path), timeout=timeout)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self) -> None:
        """Create the required database tables if they do not already exist."""
        self.cursor.execute('\n        CREATE TABLE IF NOT EXISTS players (\n            id INTEGER PRIMARY KEY,\n            mastery_rank INTEGER,\n            steel_path_unlocked INTEGER,\n            arbitrations_unlocked INTEGER DEFAULT 0,\n            helminth_unlocked INTEGER DEFAULT 0\n        )\n        ')
        self.cursor.execute("PRAGMA table_info(players)")
        columns = [row[1] for row in self.cursor.fetchall()]
        if 'arbitrations_unlocked' not in columns:
            self.cursor.execute("ALTER TABLE players ADD COLUMN arbitrations_unlocked INTEGER DEFAULT 0")
        if 'helminth_unlocked' not in columns:
            self.cursor.execute("ALTER TABLE players ADD COLUMN helminth_unlocked INTEGER DEFAULT 0")
        self.cursor.execute('\n        CREATE TABLE IF NOT EXISTS metadata (\n            key TEXT PRIMARY KEY,\n            value TEXT\n        )\n        ')
        if self.get_schema_version() is None:
            self.set_schema_version(SCHEMA_VERSION)
        self.cursor.execute('\n        CREATE TABLE IF NOT EXISTS completed_quests (\n            id INTEGER PRIMARY KEY,\n            quest_name TEXT UNIQUE\n        )\n        ')
        self.cursor.execute('\n        CREATE TABLE IF NOT EXISTS owned_mods (\n            id INTEGER PRIMARY KEY,\n            mod_name TEXT UNIQUE\n        )\n        ')
        self.cursor.execute('\n        CREATE TABLE IF NOT EXISTS owned_arcanes (\n            id INTEGER PRIMARY KEY,\n            arcane_name TEXT UNIQUE\n        )\n        ')
        self.cursor.execute('\n        CREATE TABLE IF NOT EXISTS owned_weapons (\n            id INTEGER PRIMARY KEY,\n            weapon_name TEXT UNIQUE\n        )\n        ')
        self.connection.commit()

    def get_schema_version(self) -> str | None:
        """Return the schema version stored in the database metadata."""
        self.cursor.execute("SELECT value FROM metadata WHERE key = 'schema_version'")
        row = self.cursor.fetchone()
        self.connection.commit()
        return row[0] if row else None

    def set_schema_version(self, version: str) -> None:
        """Store or update the current database schema version."""
        self.cursor.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('schema_version', ?)", (version,))
        self.connection.commit()

    def backup_database(self, destination: Path | str | None = None) -> Path:
        """Create a file backup of the current database and return its path."""
        if destination is None:
            destination = BACKUP_DIR / f'player_backup_{datetime.now():%Y%m%d_%H%M%S}.sqlite'
        else:
            destination = Path(destination)
            if not destination.is_absolute():
                destination = BACKUP_DIR / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.db_path, destination)
        return destination

    def add_completed_quest(self, quest_name: str) -> None:
        """Insert a completed quest name into the database."""
        quest_name = quest_name.strip()
        if not quest_name:
            return
        try:
            self.cursor.execute('\n                INSERT INTO completed_quests (\n                    quest_name\n                )\n                VALUES (?)\n                ', (quest_name,))
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    def get_completed_quests(self) -> list[str]:
        """Return a sorted list of completed quest names."""
        self.cursor.execute('\n            SELECT quest_name\n            FROM completed_quests\n            ORDER BY quest_name\n            ')
        results = [row[0] for row in self.cursor.fetchall()]
        self.connection.commit()
        return results

    def remove_completed_quest(self, quest_name: str) -> None:
        """Remove a completed quest from the database."""
        self.cursor.execute('\n            DELETE FROM completed_quests\n            WHERE LOWER(\n                quest_name\n            ) = LOWER(?)\n            ', (quest_name,))
        self.connection.commit()

    def add_owned_mod(self, mod_name: str) -> None:
        """Record an owned mod in the database."""
        mod_name = mod_name.strip()
        if not mod_name:
            return
        try:
            self.cursor.execute('\n                INSERT INTO owned_mods (\n                    mod_name\n                )\n                VALUES (?)\n                ', (mod_name,))
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    def get_owned_mods(self) -> list[str]:
        """Return a sorted list of owned mod names."""
        self.cursor.execute('\n            SELECT mod_name\n            FROM owned_mods\n            ORDER BY mod_name\n            ')
        results = [row[0] for row in self.cursor.fetchall()]
        self.connection.commit()
        return results

    def remove_owned_mod(self, mod_name: str) -> None:
        """Remove an owned mod from the database."""
        self.cursor.execute('\n            DELETE FROM owned_mods\n            WHERE LOWER(\n                mod_name\n            ) = LOWER(?)\n            ', (mod_name,))
        self.connection.commit()

    def add_owned_arcane(self, arcane_name: str) -> None:
        """Record an owned arcane in the database."""
        arcane_name = arcane_name.strip()
        if not arcane_name:
            return
        try:
            self.cursor.execute('\n                INSERT INTO owned_arcanes (\n                    arcane_name\n                )\n                VALUES (?)\n                ', (arcane_name,))
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    def get_owned_arcanes(self) -> list[str]:
        """Return a sorted list of owned arcane names."""
        self.cursor.execute('\n            SELECT arcane_name\n            FROM owned_arcanes\n            ORDER BY arcane_name\n            ')
        results = [row[0] for row in self.cursor.fetchall()]
        self.connection.commit()
        return results

    def remove_owned_arcane(self, arcane_name: str) -> None:
        """Remove an owned arcane from the database."""
        self.cursor.execute('\n            DELETE FROM owned_arcanes\n            WHERE LOWER(\n                arcane_name\n            ) = LOWER(?)\n            ', (arcane_name,))
        self.connection.commit()

    def add_owned_weapon(self, weapon_name: str) -> None:
        """Record an owned weapon in the database."""
        weapon_name = weapon_name.strip()
        if not weapon_name:
            return
        try:
            self.cursor.execute('\n                INSERT INTO owned_weapons (\n                    weapon_name\n                )\n                VALUES (?)\n                ', (weapon_name,))
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    def get_owned_weapons(self) -> list[str]:
        """Return a sorted list of owned weapon names."""
        self.cursor.execute('\n            SELECT weapon_name\n            FROM owned_weapons\n            ORDER BY weapon_name\n            ')
        results = [row[0] for row in self.cursor.fetchall()]
        self.connection.commit()
        return results

    def remove_owned_weapon(self, weapon_name: str) -> None:
        """Remove an owned weapon from the database."""
        self.cursor.execute('\n            DELETE FROM owned_weapons\n            WHERE LOWER(\n                weapon_name\n            ) = LOWER(?)\n            ', (weapon_name,))
        self.connection.commit()

    def save_player(self, mastery_rank: int, steel_path_unlocked: bool, arbitrations_unlocked: bool = False, helminth_unlocked: bool = False) -> None:
        """Save the player's mastery and status flags."""
        self.cursor.execute('DELETE FROM players')
        self.cursor.execute('\n            INSERT INTO players (\n                mastery_rank,\n                steel_path_unlocked,\n                arbitrations_unlocked,\n                helminth_unlocked\n            )\n            VALUES (?, ?, ?, ?)\n            ', (mastery_rank, int(steel_path_unlocked), int(arbitrations_unlocked), int(helminth_unlocked)))
        self.connection.commit()

    def get_player(self) -> tuple[int, int, int, int] | None:
        """Return the saved player row or None if no player exists."""
        self.cursor.execute("""
            SELECT
                mastery_rank,
                steel_path_unlocked,
                arbitrations_unlocked,
                helminth_unlocked
            FROM players
            LIMIT 1
            """)
        player = self.cursor.fetchone()
        self.connection.commit()
        return player

    def get_players(self) -> list[tuple[int, int, int, int]]:
        """Return all saved player rows."""
        self.cursor.execute("""
            SELECT
                mastery_rank,
                steel_path_unlocked,
                arbitrations_unlocked,
                helminth_unlocked
            FROM players
            """)
        players = self.cursor.fetchall()
        self.connection.commit()
        return players
