import sqlite3
from pathlib import Path


class DatabaseManager:

    def __init__(self):

        # Always use the same database file
        db_path = Path(__file__).parent.parent.parent / "player.db"

        self.connection = sqlite3.connect(str(db_path))
        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            mastery_rank INTEGER,
            steel_path_unlocked INTEGER
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS completed_quests (
            id INTEGER PRIMARY KEY,
            quest_name TEXT UNIQUE
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS owned_mods (
            id INTEGER PRIMARY KEY,
            mod_name TEXT UNIQUE
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS owned_arcanes (
            id INTEGER PRIMARY KEY,
            arcane_name TEXT UNIQUE
        )
        """)

        self.connection.commit()

    # -------------------------
    # QUESTS
    # -------------------------

    def add_completed_quest(self, quest_name):

        quest_name = quest_name.strip()

        if not quest_name:
            return

        try:

            self.cursor.execute(
                """
                INSERT INTO completed_quests (
                    quest_name
                )
                VALUES (?)
                """,
                (quest_name,)
            )

            self.connection.commit()

        except sqlite3.IntegrityError:
            pass

    def get_completed_quests(self):

        self.cursor.execute(
            """
            SELECT quest_name
            FROM completed_quests
            ORDER BY quest_name
            """
        )

        return [
            row[0]
            for row in self.cursor.fetchall()
        ]

    # -------------------------
    # MODS
    # -------------------------

    def add_owned_mod(self, mod_name):

        mod_name = mod_name.strip()

        if not mod_name:
            return

        try:

            self.cursor.execute(
                """
                INSERT INTO owned_mods (
                    mod_name
                )
                VALUES (?)
                """,
                (mod_name,)
            )

            self.connection.commit()

        except sqlite3.IntegrityError:
            pass

    def get_owned_mods(self):

        self.cursor.execute(
            """
            SELECT mod_name
            FROM owned_mods
            ORDER BY mod_name
            """
        )

        return [
            row[0]
            for row in self.cursor.fetchall()
        ]
    # -------------------------
    # ARCANE
    # -------------------------
    
    def add_owned_arcane(self, arcane_name):

        arcane_name = arcane_name.strip().lower()

        existing = self.get_owned_arcanes()

        if arcane_name in [
            a.lower()
            for a in existing
        ]:
            return

        self.cursor.execute(
            """
            INSERT INTO owned_arcanes (
                arcane_name
            )
            VALUES (?)
            """,
            (arcane_name,)
        )

        self.connection.commit()

    def get_owned_arcanes(self):

        self.cursor.execute(
            """
            SELECT arcane_name
            FROM owned_arcanes
            """
        )

        return [
            row[0]
            for row in self.cursor.fetchall()
        ]

    # -------------------------
    # PLAYER
    # -------------------------

    def save_player(
        self,
        mastery_rank,
        steel_path_unlocked
    ):

        self.cursor.execute(
            "DELETE FROM players"
        )

        self.cursor.execute(
            """
            INSERT INTO players (
                mastery_rank,
                steel_path_unlocked
            )
            VALUES (?, ?)
            """,
            (
                mastery_rank,
                steel_path_unlocked
            )
        )

        self.connection.commit()

    def get_player(self):

        self.cursor.execute(
            """
            SELECT
                mastery_rank,
                steel_path_unlocked
            FROM players
            LIMIT 1
            """
        )

        return self.cursor.fetchone()