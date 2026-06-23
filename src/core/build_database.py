from __future__ import annotations
from typing import Any

BUILDS = [
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

    def get_all_builds(self) -> list[dict[str, Any]]:
        return BUILDS

    def get_build_for_weapon(self, weapon_name: str) -> dict[str, Any] | None:
        name_lower = weapon_name.strip().lower()
        for b in BUILDS:
            if b["weapon"].lower() == name_lower:
                return b
        return None
