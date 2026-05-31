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

        self.connection.commit()

    def save_player(self,mastery_rank,steel_path_unlocked):
        
        self.cursor.execute("""
                            INSERT INTO players (
                            mastery_rank,
                            steel_path_unlocked
                            )
                            VALUES (?, ?)
                            """,
                        (
                            mastery_rank,
                            int(steel_path_unlocked)
                            ))
        
        self.connection.commit()

    def get_players(self):
        
        self.cursor.execute(
        "SELECT * FROM players"
        )
        
        return self.cursor.fetchall()