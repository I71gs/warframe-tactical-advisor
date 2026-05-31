import sqlite3


class DatabaseManager:

    def __init__(self):

        self.connection = sqlite3.connect(
            "player.db"
        )

        self.cursor = self.connection.cursor()

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
            quest_name TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS owned_mods (
            id INTEGER PRIMARY KEY,
            mod_name TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS owned_arcanes (
            id INTEGER PRIMARY KEY,
            arcane_name TEXT
        )
        """)

        self.connection.commit()

    def add_completed_quest(self, quest_name):

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

    def get_completed_quests(self):

        self.cursor.execute(
            "SELECT quest_name FROM completed_quests"
        )

        return [
            row[0]
            for row in self.cursor.fetchall()
        ]

    def add_owned_mod(self, mod_name):

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

    def get_owned_mods(self):

        self.cursor.execute(
            "SELECT mod_name FROM owned_mods"
        )

        return [
            row[0]
            for row in self.cursor.fetchall()
        ]