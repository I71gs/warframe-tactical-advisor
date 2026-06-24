from __future__ import annotations
import sqlite3
import sys
from pathlib import Path

def inspect(db_path: Path) -> None:
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    print(f"Inspecting SQLite Database at {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Tables found: {', '.join(tables)}")
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cursor.fetchone()[0]
            print(f"  - {t}: {cnt} rows")
        conn.close()
    except Exception as e:
        print(f"Error inspecting database: {e}")

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    default_db = root / "profiles" / "default" / "player.db"
    inspect(default_db)
