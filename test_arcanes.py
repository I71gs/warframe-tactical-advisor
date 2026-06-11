from src.database.database import DatabaseManager

db = DatabaseManager()

db.create_tables()

db.add_owned_arcane(
    "Primary Merciless"
)

print(
    db.get_owned_arcanes()
)