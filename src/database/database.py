from __future__ import annotations
from pathlib import Path
import shutil
import sqlite3
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / 'player.db'
BACKUP_DIR = ROOT / 'backups'
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
SCHEMA_VERSION = '2'

class DatabaseManager:
    """Manages local SQLite persistence for player profiles and progress."""

    def __init__(self, db_path: Path | str | None = None, timeout: int = 5) -> None:
        """Open or create the SQLite database file."""
        if db_path is not None:
            self.db_path = Path(db_path)
        else:
            from src.core.settings_manager import SettingsManager
            profile = SettingsManager().get('current_profile', 'default')
            from src.core.save_manager import SaveManager
            sm = SaveManager()
            sm.create_profile(profile)
            self.db_path = sm.get_profile_db_path(profile)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
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
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS weapon_inventory (
            weapon_name TEXT PRIMARY KEY,
            rank INTEGER DEFAULT 0,
            forma_count INTEGER DEFAULT 0,
            has_catalyst INTEGER DEFAULT 0
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS mod_inventory (
            mod_name TEXT PRIMARY KEY,
            rank INTEGER DEFAULT 0,
            max_rank INTEGER DEFAULT 10
        )
        ''')
        
        # Migrate existing owned_weapons to weapon_inventory if empty
        self.cursor.execute("SELECT COUNT(*) FROM weapon_inventory")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("SELECT weapon_name FROM owned_weapons")
            weapons = self.cursor.fetchall()
            for (w,) in weapons:
                self.cursor.execute("INSERT OR IGNORE INTO weapon_inventory (weapon_name, rank, forma_count, has_catalyst) VALUES (?, 30, 0, 0)", (w,))
                
        # Migrate existing owned_mods to mod_inventory if empty
        self.cursor.execute("SELECT COUNT(*) FROM mod_inventory")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("SELECT mod_name FROM owned_mods")
            mods = self.cursor.fetchall()
            for (m,) in mods:
                self.cursor.execute("INSERT OR IGNORE INTO mod_inventory (mod_name, rank, max_rank) VALUES (?, 10, 10)", (m,))

        # ── Schema v2 collection tables ────────────────────────────────────
        collection_table_sql = '''
            CREATE TABLE IF NOT EXISTS {table} (
                name        TEXT PRIMARY KEY,
                owned       INTEGER DEFAULT 0,
                rank        INTEGER DEFAULT 0,
                forma_count INTEGER DEFAULT 0,
                has_reactor INTEGER DEFAULT 0,
                polarities  TEXT    DEFAULT '',
                notes       TEXT    DEFAULT '',
                acquisition TEXT    DEFAULT ''
            )
        '''
        for tbl in (
            'warframe_inventory',
            'companion_inventory',
            'archwing_inventory',
            'necramech_inventory',
            'amp_inventory',
        ):
            self.cursor.execute(collection_table_sql.format(table=tbl))

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS focus_schools (
                school      TEXT PRIMARY KEY,
                active      INTEGER DEFAULT 0,
                focus_spent INTEGER DEFAULT 0,
                notes       TEXT DEFAULT ''
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS intrinsics (
                category TEXT PRIMARY KEY,
                rank     INTEGER DEFAULT 0
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS railjack_upgrades (
                component TEXT PRIMARY KEY,
                tier      INTEGER DEFAULT 0,
                notes     TEXT DEFAULT ''
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS operator_config (
                key   TEXT PRIMARY KEY,
                value TEXT DEFAULT ''
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                query     TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')

        # ── Seed default intrinsic categories if empty ─────────────────────
        self.cursor.execute('SELECT COUNT(*) FROM intrinsics')
        if self.cursor.fetchone()[0] == 0:
            for cat in ('Piloting', 'Gunnery', 'Tactical', 'Engineering', 'Command'):
                self.cursor.execute(
                    'INSERT OR IGNORE INTO intrinsics (category, rank) VALUES (?, 0)', (cat,)
                )

        # ── Seed default focus schools if empty ────────────────────────────
        self.cursor.execute('SELECT COUNT(*) FROM focus_schools')
        if self.cursor.fetchone()[0] == 0:
            for school in ('Zenurik', 'Naramon', 'Unairu', 'Madurai', 'Vazarin'):
                self.cursor.execute(
                    'INSERT OR IGNORE INTO focus_schools (school) VALUES (?)', (school,)
                )

        # ── Schema migration v1 → v2 ───────────────────────────────────────
        current = self.get_schema_version()
        if current == '1':
            self.set_schema_version('2')

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

    def add_weapon_detailed(self, name: str, rank: int, forma_count: int, has_catalyst: bool) -> None:
        name = name.strip()
        if not name:
            return
        self.cursor.execute('''
            INSERT OR REPLACE INTO weapon_inventory (weapon_name, rank, forma_count, has_catalyst)
            VALUES (?, ?, ?, ?)
        ''', (name, rank, forma_count, int(has_catalyst)))
        try:
            self.cursor.execute('INSERT OR IGNORE INTO owned_weapons (weapon_name) VALUES (?)', (name,))
        except Exception:
            pass
        self.connection.commit()

    def get_weapon_inventory(self) -> list[dict]:
        self.cursor.execute('SELECT weapon_name, rank, forma_count, has_catalyst FROM weapon_inventory')
        rows = self.cursor.fetchall()
        self.connection.commit()
        return [
            {
                "weapon_name": r[0],
                "rank": r[1],
                "forma_count": r[2],
                "has_catalyst": bool(r[3])
            } for r in rows
        ]

    def remove_weapon_detailed(self, name: str) -> None:
        self.cursor.execute('DELETE FROM weapon_inventory WHERE LOWER(weapon_name) = LOWER(?)', (name,))
        self.cursor.execute('DELETE FROM owned_weapons WHERE LOWER(weapon_name) = LOWER(?)', (name,))
        self.connection.commit()

    def add_mod_detailed(self, name: str, rank: int, max_rank: int) -> None:
        name = name.strip()
        if not name:
            return
        self.cursor.execute('''
            INSERT OR REPLACE INTO mod_inventory (mod_name, rank, max_rank)
            VALUES (?, ?, ?)
        ''', (name, rank, max_rank))
        try:
            self.cursor.execute('INSERT OR IGNORE INTO owned_mods (mod_name) VALUES (?)', (name,))
        except Exception:
            pass
        self.connection.commit()

    def get_mod_inventory(self) -> list[dict]:
        self.cursor.execute('SELECT mod_name, rank, max_rank FROM mod_inventory')
        rows = self.cursor.fetchall()
        self.connection.commit()
        return [
            {
                "mod_name": r[0],
                "rank": r[1],
                "max_rank": r[2]
            } for r in rows
        ]

    def remove_mod_detailed(self, name: str) -> None:
        self.cursor.execute('DELETE FROM mod_inventory WHERE LOWER(mod_name) = LOWER(?)', (name,))
        self.cursor.execute('DELETE FROM owned_mods WHERE LOWER(mod_name) = LOWER(?)', (name,))
        self.connection.commit()

    # ── Generic collection table CRUD ──────────────────────────────────────

    def upsert_collection_item(
        self,
        table: str,
        name: str,
        owned: bool = True,
        rank: int = 0,
        forma_count: int = 0,
        has_reactor: bool = False,
        polarities: str = '',
        notes: str = '',
        acquisition: str = '',
    ) -> None:
        """Insert or update a row in any collection inventory table."""
        ALLOWED = {
            'warframe_inventory', 'companion_inventory', 'archwing_inventory',
            'necramech_inventory', 'amp_inventory',
        }
        if table not in ALLOWED:
            raise ValueError(f'Unknown collection table: {table}')
        self.cursor.execute(f'''
            INSERT OR REPLACE INTO {table}
                (name, owned, rank, forma_count, has_reactor, polarities, notes, acquisition)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name.strip(), int(owned), rank, forma_count, int(has_reactor),
              polarities, notes, acquisition))
        self.connection.commit()

    def get_collection_table(self, table: str) -> list[dict]:
        """Return all rows from a collection inventory table as list of dicts."""
        ALLOWED = {
            'warframe_inventory', 'companion_inventory', 'archwing_inventory',
            'necramech_inventory', 'amp_inventory',
        }
        if table not in ALLOWED:
            raise ValueError(f'Unknown collection table: {table}')
        self.cursor.execute(
            f'SELECT name, owned, rank, forma_count, has_reactor, polarities, notes, acquisition FROM {table}'
        )
        cols = ('name', 'owned', 'rank', 'forma_count', 'has_reactor', 'polarities', 'notes', 'acquisition')
        rows = self.cursor.fetchall()
        self.connection.commit()
        return [dict(zip(cols, r)) for r in rows]

    def remove_collection_item(self, table: str, name: str) -> None:
        """Delete a single row from a collection inventory table."""
        ALLOWED = {
            'warframe_inventory', 'companion_inventory', 'archwing_inventory',
            'necramech_inventory', 'amp_inventory',
        }
        if table not in ALLOWED:
            raise ValueError(f'Unknown collection table: {table}')
        self.cursor.execute(f'DELETE FROM {table} WHERE LOWER(name) = LOWER(?)', (name,))
        self.connection.commit()

    # ── Focus Schools ───────────────────────────────────────────────────────

    def get_focus_schools(self) -> list[dict]:
        """Return all focus school rows."""
        self.cursor.execute('SELECT school, active, focus_spent, notes FROM focus_schools')
        cols = ('school', 'active', 'focus_spent', 'notes')
        rows = self.cursor.fetchall()
        self.connection.commit()
        return [dict(zip(cols, r)) for r in rows]

    def set_focus_school(self, school: str, active: bool, focus_spent: int = 0, notes: str = '') -> None:
        """Update a focus school row."""
        self.cursor.execute(
            'INSERT OR REPLACE INTO focus_schools (school, active, focus_spent, notes) VALUES (?, ?, ?, ?)',
            (school, int(active), focus_spent, notes)
        )
        self.connection.commit()

    # ── Intrinsics ──────────────────────────────────────────────────────────

    def get_intrinsics(self) -> dict[str, int]:
        """Return {category: rank} for all intrinsic categories."""
        self.cursor.execute('SELECT category, rank FROM intrinsics')
        rows = self.cursor.fetchall()
        self.connection.commit()
        return {r[0]: r[1] for r in rows}

    def set_intrinsic(self, category: str, rank: int) -> None:
        """Set the rank for an intrinsic category (0–10)."""
        rank = max(0, min(10, rank))
        self.cursor.execute(
            'INSERT OR REPLACE INTO intrinsics (category, rank) VALUES (?, ?)', (category, rank)
        )
        self.connection.commit()

    # ── Railjack ─────────────────────────────────────────────────────────────

    def get_railjack_upgrades(self) -> list[dict]:
        """Return all railjack upgrade rows."""
        self.cursor.execute('SELECT component, tier, notes FROM railjack_upgrades')
        cols = ('component', 'tier', 'notes')
        rows = self.cursor.fetchall()
        self.connection.commit()
        return [dict(zip(cols, r)) for r in rows]

    def set_railjack_upgrade(self, component: str, tier: int, notes: str = '') -> None:
        """Insert or update a Railjack component tier."""
        self.cursor.execute(
            'INSERT OR REPLACE INTO railjack_upgrades (component, tier, notes) VALUES (?, ?, ?)',
            (component, tier, notes)
        )
        self.connection.commit()

    # ── Search History ────────────────────────────────────────────────────────

    def add_search_history(self, query: str) -> None:
        """Record a search query with current timestamp."""
        from datetime import datetime as dt
        self.cursor.execute(
            'INSERT INTO search_history (query, timestamp) VALUES (?, ?)',
            (query.strip(), dt.now().isoformat())
        )
        # Keep only last 200 entries
        self.cursor.execute(
            'DELETE FROM search_history WHERE id NOT IN (SELECT id FROM search_history ORDER BY id DESC LIMIT 200)'
        )
        self.connection.commit()

    def get_search_history(self, limit: int = 20) -> list[str]:
        """Return the most recent search queries."""
        self.cursor.execute(
            'SELECT query FROM search_history ORDER BY id DESC LIMIT ?', (limit,)
        )
        rows = self.cursor.fetchall()
        self.connection.commit()
        return [r[0] for r in rows]

    def clear_search_history(self) -> None:
        """Wipe all search history records."""
        self.cursor.execute('DELETE FROM search_history')
        self.connection.commit()

    # ── Config helpers ───────────────────────────────────────────────────────

    def get_config(self, key: str) -> str | None:
        """Get config value for given key."""
        self.cursor.execute('SELECT value FROM operator_config WHERE key = ?', (key,))
        row = self.cursor.fetchone()
        self.connection.commit()
        return row[0] if row else None

    def set_config(self, key: str, value: str) -> None:
        """Set config value for given key."""
        self.cursor.execute(
            'INSERT OR REPLACE INTO operator_config (key, value) VALUES (?, ?)',
            (key, str(value))
        )
        self.connection.commit()

