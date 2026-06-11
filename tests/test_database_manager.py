from pathlib import Path

from src.database.database import DatabaseManager


def test_database_manager_temporary_database(tmp_path: Path) -> None:
    db_path = tmp_path / 'test_player.db'
    db = DatabaseManager(db_path=db_path)

    assert db.get_schema_version() == '1'
    assert db.get_players() == []

    db.save_player(12, 1)
    assert db.get_player() == (12, 1)
    assert db.get_players() == [(12, 1)]

    db.add_completed_quest('The New War')
    assert db.get_completed_quests() == ['The New War']

    db.add_owned_mod('Galvanized Chamber')
    assert db.get_owned_mods() == ['Galvanized Chamber']

    backup_path = db.backup_database(destination=tmp_path / 'player_backup.sqlite')
    assert backup_path.exists()
    db.connection.close()
