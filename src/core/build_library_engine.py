from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from src.utils.logger import logger

ROOT = Path(__file__).resolve().parents[2]
LIBRARY_DIR = ROOT / "build_library"

class BuildLibraryEngine:
    """Manages the player's custom builds library, favorites, notes, and rankings."""

    def __init__(self, library_dir: Path | str | None = None) -> None:
        self.library_dir = Path(library_dir) if library_dir else LIBRARY_DIR
        self.library_dir.mkdir(parents=True, exist_ok=True)
        self.library_file = self.library_dir / "custom_builds.json"

    def load_library(self) -> list[dict[str, Any]]:
        """Loads custom builds from the JSON library file."""
        if not self.library_file.exists():
            return []
        try:
            with open(self.library_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            logger.error("Failed to load build library: %s", e)
        return []

    def save_library(self, builds: list[dict[str, Any]]) -> None:
        """Saves custom builds to the JSON library file."""
        try:
            with open(self.library_file, "w", encoding="utf-8") as f:
                json.dump(builds, f, indent=4)
        except Exception as e:
            logger.error("Failed to save build library: %s", e)

    def add_or_update_build(
        self,
        weapon: str,
        mods: list[str],
        arcane: str,
        element: str,
        rating: int = 5,
        notes: str = "",
        is_favorite: bool = False
    ) -> None:
        """Adds a new build or updates an existing one for a weapon."""
        builds = self.load_library()
        found = False
        for b in builds:
            if b["weapon"].lower() == weapon.strip().lower():
                b["mods"] = mods
                b["arcane"] = arcane
                b["element"] = element
                b["rating"] = rating
                b["notes"] = notes
                b["is_favorite"] = is_favorite
                found = True
                break
        if not found:
            builds.append({
                "weapon": weapon.strip(),
                "mods": mods,
                "arcane": arcane,
                "element": element,
                "rating": rating,
                "notes": notes,
                "is_favorite": is_favorite
            })
        self.save_library(builds)

    def delete_build(self, weapon: str) -> None:
        """Deletes a custom build by weapon name."""
        builds = self.load_library()
        builds = [b for b in builds if b["weapon"].lower() != weapon.strip().lower()]
        self.save_library(builds)

    def toggle_favorite(self, weapon: str) -> None:
        """Toggles the favorite status of a build."""
        builds = self.load_library()
        for b in builds:
            if b["weapon"].lower() == weapon.strip().lower():
                b["is_favorite"] = not b.get("is_favorite", False)
                break
        self.save_library(builds)
