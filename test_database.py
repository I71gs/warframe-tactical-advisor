from src.database.database import DatabaseManager

db = DatabaseManager()

players = db.get_players()

print(players)