from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from src.utils.logger import logger

ROOT = Path(__file__).resolve().parents[2]
BUILDS_DIR = ROOT / "src" / "resources" / "data" / "builds"

STATIC_BUILDS = [
    {
        "weapon": "Phenmor",
        "mods": ["Galvanized Chamber", "Galvanized Aptitude", "Serration", "Split Chamber", "Hellfire", "Infected Clip", "Cryo Rounds", "Point Strike"],
        "arcane": "Primary Merciless",
        "element": "Viral Heat",
        "rating": 98
    },
    {
        "weapon": "Laetum",
        "mods": ["Galvanized Diffusion", "Galvanized Shot", "Hornet Strike", "Lethal Torrent", "Pathogen Rounds", "Deep Freeze", "Heated Charge", "Pistol Gambit"],
        "arcane": "Secondary Merciless",
        "element": "Viral Heat",
        "rating": 97
    },
    {
        "weapon": "Torid",
        "mods": ["Galvanized Chamber", "Serration", "Split Chamber", "Infected Clip", "Stormbringer", "Point Strike", "Vital Sense", "Hunter Munitions"],
        "arcane": "Primary Merciless",
        "element": "Corrosive",
        "rating": 95
    },
    {
        "weapon": "Felarx",
        "mods": ["Galvanized Hell", "Galvanized Savvy", "Primed Point Blank", "Hell's Chamber", "Toxic Barrage", "Frigid Blast", "Scattering Inferno", "Blaze"],
        "arcane": "Primary Merciless",
        "element": "Viral Heat",
        "rating": 96
    },
    {
        "weapon": "Kuva Bramma",
        "mods": ["Galvanized Chamber", "Serration", "Split Chamber", "Infected Clip", "Cryo Rounds", "Point Strike", "Vital Sense", "Hunter Munitions"],
        "arcane": "Primary Merciless",
        "element": "Viral",
        "rating": 92
    }
]

class BuildDatabase:
    """Provides lookup functions for high-meta weapon builds and modding targets."""

    def __init__(self) -> None:
        self.builds_dir = BUILDS_DIR
        self.builds_dir.mkdir(parents=True, exist_ok=True)

    def get_all_builds(self) -> list[dict[str, Any]]:
        """Loads and returns all builds, falling back to static builds if none exist on disk."""
        files = list(self.builds_dir.glob("*.json"))
        if not files:
            return STATIC_BUILDS
            
        builds = []
        for f in files:
            try:
                with open(f, "r", encoding="utf-8") as file_obj:
                    data = json.load(file_obj)
                    if isinstance(data, list):
                        builds.extend(data)
                    else:
                        builds.append(data)
            except Exception as e:
                logger.error("Failed to load build config %s: %s", f.name, e)

                
        # Fill missing ones from static database for robustness
        for sb in STATIC_BUILDS:
            if not any(b["weapon"].lower() == sb["weapon"].lower() for b in builds):
                builds.append(sb)
                
        return builds

    def get_build_for_weapon(self, weapon_name: str) -> dict[str, Any] | None:
        name_lower = weapon_name.strip().lower()
        builds = self.get_all_builds()
        for b in builds:
            if b["weapon"].lower() == name_lower:
                return b
        return None

# Maintain the global BUILDS list for module imports
BUILDS = BuildDatabase().get_all_builds()

