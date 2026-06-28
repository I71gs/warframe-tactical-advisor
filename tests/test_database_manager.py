from pathlib import Path

from src.database.database import DatabaseManager


def test_database_manager_temporary_database(tmp_path: Path) -> None:
    db_path = tmp_path / 'test_player.db'
    db = DatabaseManager(db_path=db_path)

    assert db.get_schema_version() == '2'
    assert db.get_players() == []

    db.save_player(12, True, False, False)
    assert db.get_player() == (12, 1, 0, 0)
    assert db.get_players() == [(12, 1, 0, 0)]

    db.add_completed_quest('The New War')
    assert db.get_completed_quests() == ['The New War']

    db.add_owned_mod('Galvanized Chamber')
    assert db.get_owned_mods() == ['Galvanized Chamber']

    backup_path = db.backup_database(destination=tmp_path / 'player_backup.sqlite')
    assert backup_path.exists()
    db.connection.close()

def test_database_manager_detailed_inventory(tmp_path: Path) -> None:
    db_path = tmp_path / 'test_detailed_player.db'
    db = DatabaseManager(db_path=db_path)

    # Initially empty
    assert db.get_weapon_inventory() == []
    assert db.get_mod_inventory() == []

    # Insert weapons
    db.add_weapon_detailed("Phenmor", 30, 2, True)
    db.add_weapon_detailed("Laetum", 10, 0, False)
    weapons = db.get_weapon_inventory()
    assert len(weapons) == 2
    
    phenmor = next(w for w in weapons if w["weapon_name"] == "Phenmor")
    assert phenmor["rank"] == 30
    assert phenmor["forma_count"] == 2
    assert phenmor["has_catalyst"] is True

    # Check compatibility with old owned_weapons
    assert "Phenmor" in db.get_owned_weapons()

    # Delete weapon
    db.remove_weapon_detailed("Laetum")
    assert len(db.get_weapon_inventory()) == 1
    assert "Laetum" not in db.get_owned_weapons()

    # Insert mods
    db.add_mod_detailed("Serration", 8, 10)
    mods = db.get_mod_inventory()
    assert len(mods) == 1
    serration = mods[0]
    assert serration["mod_name"] == "Serration"
    assert serration["rank"] == 8
    assert serration["max_rank"] == 10

    # Check compatibility with old owned_mods
    assert "Serration" in db.get_owned_mods()

    # Delete mod
    db.remove_mod_detailed("Serration")
    assert db.get_mod_inventory() == []
    assert "Serration" not in db.get_owned_mods()

    db.connection.close()


def test_database_manager_v2_collections(tmp_path) -> None:
    """Test schema v2 collection tables: warframe_inventory, focus, intrinsics, railjack, search history."""
    from src.database.database import DatabaseManager as DM
    db = DM(db_path=tmp_path / "v2_test.db")

    # warframe_inventory CRUD
    db.upsert_collection_item("warframe_inventory", "Wisp", owned=True, rank=30, forma_count=3, has_reactor=True, notes="main")
    rows = db.get_collection_table("warframe_inventory")
    assert len(rows) == 1
    wisp = rows[0]
    assert wisp["name"] == "Wisp"
    assert wisp["owned"] == 1
    assert wisp["rank"] == 30
    assert wisp["forma_count"] == 3
    assert wisp["has_reactor"] == 1
    assert wisp["notes"] == "main"

    # update forma
    db.upsert_collection_item("warframe_inventory", "Wisp", owned=True, rank=30, forma_count=4)
    rows = db.get_collection_table("warframe_inventory")
    assert rows[0]["forma_count"] == 4

    # remove
    db.remove_collection_item("warframe_inventory", "Wisp")
    assert db.get_collection_table("warframe_inventory") == []

    # focus schools (seeded on create — should already have Zenurik etc)
    db.set_focus_school("Zenurik", active=True, focus_spent=50000)
    schools = db.get_focus_schools()
    zenurik = next(s for s in schools if s["school"] == "Zenurik")
    assert zenurik["active"] == 1
    assert zenurik["focus_spent"] == 50000

    # intrinsics (seeded on create)
    db.set_intrinsic("Piloting", 7)
    assert db.get_intrinsics()["Piloting"] == 7
    db.set_intrinsic("Piloting", 15)  # clamps to 10
    assert db.get_intrinsics()["Piloting"] == 10

    # railjack
    db.set_railjack_upgrade("Carcinnox", tier=5, notes="Void Proxima")
    upgrades = db.get_railjack_upgrades()
    assert any(u["component"] == "Carcinnox" and u["tier"] == 5 for u in upgrades)

    # search history
    db.add_search_history("Wisp")
    db.add_search_history("Saryn")
    history = db.get_search_history()
    assert "Saryn" in history
    assert "Wisp" in history
    db.clear_search_history()
    assert db.get_search_history() == []

    db.connection.close()
