# debug_db.py

from src.database.database import DatabaseManager

db = DatabaseManager()

print("QUESTS:")
print(db.get_completed_quests())

print("\nMODS:")
print(db.get_owned_mods())