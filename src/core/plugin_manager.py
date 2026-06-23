from __future__ import annotations
import json
from pathlib import Path
from src.utils.logger import logger
from src.core.weapon_database import WEAPONS
from src.core.build_database import BUILDS
from src.core.farming_database import FARMING_DATA

ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = ROOT / 'plugins'

class PluginManager:
    """Loads custom directories or JSON databases to extend weapons, builds, or farming routes."""

    def __init__(self, plugins_dir: Path | str | None = None) -> None:
        self.plugins_dir = Path(plugins_dir) if plugins_dir else PLUGINS_DIR

    def load_plugins(self) -> None:
        """Scan plugins directory and load extensions into global databases."""
        if not self.plugins_dir.exists():
            try:
                self.plugins_dir.mkdir(parents=True, exist_ok=True)
                # Create a sample legacy/json plugin file inside the directory
                sample_plugin = {
                    "weapons": [
                        {
                            "name": "Rubico Prime",
                            "type": "Primary",
                            "acquisition": "Relic / Prime Vault",
                            "meta_rating": 85,
                            "category": "Sniper"
                        }
                    ],
                    "builds": [
                        {
                            "weapon": "Rubico Prime",
                            "mods": ["Serration", "Split Chamber", "Point Strike", "Vital Sense", "Stormbringer", "Infected Clip", "Hellfire", "Vigilant Armaments"],
                            "arcane": "Primary Merciless",
                            "element": "Corrosive Heat",
                            "rating": 89
                        }
                    ],
                    "farming": {
                        "rubico prime": {
                            "source": "Lith / Meso Relics",
                            "estimated_time": "2-4 hours"
                        }
                    }
                }
                sample_file = self.plugins_dir / 'custom_weapons_sample.json'
                with open(sample_file, 'w', encoding='utf-8') as f:
                    json.dump(sample_plugin, f, indent=4)
            except Exception as exc:
                logger.warning("Failed to create plugins directory or sample plugin: %s", exc)
                return

        # Load all directory-based plugins (marketplace format)
        from src.core.plugin_registry import PluginRegistry
        registry = PluginRegistry()
        for folder in self.plugins_dir.iterdir():
            if folder.is_dir():
                registry.load_plugin_from_directory(folder)

        # Load all JSON plugins (legacy format)
        for path in self.plugins_dir.glob('*.json'):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load weapons
                if "weapons" in data and isinstance(data["weapons"], list):
                    for w in data["weapons"]:
                        if not any(existing["name"].lower() == w["name"].lower() for existing in WEAPONS):
                            WEAPONS.append(w)
                            
                # Load builds
                if "builds" in data and isinstance(data["builds"], list):
                    for b in data["builds"]:
                        if not any(existing["weapon"].lower() == b["weapon"].lower() for existing in BUILDS):
                            BUILDS.append(b)

                # Load farming data
                if "farming" in data and isinstance(data["farming"], dict):
                    for k, v in data["farming"].items():
                        FARMING_DATA[k.lower()] = v
                        
                logger.info("Successfully loaded legacy plugin: %s", path.name)
            except Exception as exc:
                logger.error("Failed to load legacy plugin %s: %s", path.name, exc)
