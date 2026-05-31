from src.database.database import DatabaseManager

db = DatabaseManager()

db.create_tables()

db.add_completed_quest(
    "The New War"
)

db.add_owned_mod(
    "Galvanized Chamber"
)

print(
    db.get_completed_quests()
)

print(
    db.get_owned_mods()
)
