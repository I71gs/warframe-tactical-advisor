import json
from pathlib import Path
from src.core.plugin_manager import PluginManager
from src.core.weapon_database import WEAPONS
from src.core.build_database import BUILDS
from src.core.farming_database import FARMING_DATA

def test_plugin_manager(tmp_path: Path) -> None:
    # Set up temp plugin
    plugin_data = {
        "weapons": [
            {
                "name": "Test Weapon Plugin",
                "type": "Primary",
                "acquisition": "Test Source",
                "meta_rating": 99,
                "category": "Rifle"
            }
        ],
        "builds": [
            {
                "weapon": "Test Weapon Plugin",
                "mods": ["Serration"],
                "arcane": "None",
                "element": "None",
                "rating": 100
            }
        ],
        "farming": {
            "test weapon plugin": {
                "source": "Test Mission",
                "estimated_time": "1 hour"
            }
        }
    }
    
    # Write custom JSON plugin file
    plugin_file = tmp_path / "custom_test_plugin.json"
    with open(plugin_file, "w", encoding="utf-8") as f:
        json.dump(plugin_data, f, indent=4)
        
    pm = PluginManager(plugins_dir=tmp_path)
    pm.load_plugins()

    # Assert load occurred successfully
    assert any(w["name"] == "Test Weapon Plugin" for w in WEAPONS)
    assert any(b["weapon"] == "Test Weapon Plugin" for b in BUILDS)
    assert "test weapon plugin" in FARMING_DATA
    assert FARMING_DATA["test weapon plugin"]["source"] == "Test Mission"
