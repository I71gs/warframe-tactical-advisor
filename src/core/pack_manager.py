from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from src.utils.logger import logger

ROOT = Path(__file__).resolve().parents[2]
PACKS_DIR = ROOT / "packs"

class PackManager:
    """Manages enabling/disabling data packs, version requirements, dependencies, and merges."""

    def __init__(self, packs_dir: Path | str | None = None) -> None:
        self.packs_dir = Path(packs_dir) if packs_dir else PACKS_DIR
        self.packs_dir.mkdir(parents=True, exist_ok=True)

    def load_pack_file(self, filepath: Path) -> dict[str, Any] | None:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Failed to load pack file %s: %s", filepath.name, e)
            return None

    def save_pack_file(self, filepath: Path, data: dict[str, Any]) -> None:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error("Failed to save pack file %s: %s", filepath.name, e)

    def get_all_packs(self) -> list[dict[str, Any]]:
        packs = []
        for path in self.packs_dir.glob("*.json"):
            pack = self.load_pack_file(path)
            if pack and "id" in pack:
                pack["filepath"] = str(path)
                packs.append(pack)
        return packs

    def set_pack_enabled(self, pack_id: str, enabled: bool) -> bool:
        """Enables/disables a pack and saves to its json file."""
        for path in self.packs_dir.glob("*.json"):
            pack = self.load_pack_file(path)
            if pack and pack.get("id") == pack_id:
                pack["enabled"] = enabled
                self.save_pack_file(path, pack)
                return True
        return False

    def validate_dependencies(self) -> dict[str, list[str]]:
        """Returns a dict of pack_id to list of unmet/disabled dependency ids."""
        packs = self.get_all_packs()
        pack_map = {p["id"]: p for p in packs}
        unmet = {}

        for p in packs:
            if not p.get("enabled", False):
                continue
            unmet_deps = []
            for dep in p.get("dependencies", []):
                if dep not in pack_map:
                    unmet_deps.append(f"{dep} (Missing)")
                elif not pack_map[dep].get("enabled", False):
                    unmet_deps.append(f"{dep} (Disabled)")
            if unmet_deps:
                unmet[p["id"]] = unmet_deps
        return unmet

    def merge_packs(self, base_weapons: list[dict[str, Any]], base_mods: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]:
        """Merges all enabled, valid packs into base datasets."""
        unmet = self.validate_dependencies()
        packs = self.get_all_packs()
        
        merged_weapons = list(base_weapons)
        merged_mods = list(base_mods)

        # Track keys to avoid duplicates
        weapon_names = {w["name"].lower() for w in merged_weapons}
        mod_names = {m["name"].lower() for m in merged_mods}

        for p in packs:
            if not p.get("enabled", False):
                continue
            # Skip packs with unmet dependencies
            if p["id"] in unmet:
                logger.warning("Skipping pack %s due to unmet dependencies", p["id"])
                continue

            # Merge weapons
            for w in p.get("weapons", []):
                if w["name"].lower() not in weapon_names:
                    merged_weapons.append(w)
                    weapon_names.add(w["name"].lower())

            # Merge mods
            for m in p.get("mods", []):
                if m["name"].lower() not in mod_names:
                    merged_mods.append(m)
                    mod_names.add(m["name"].lower())

        return merged_weapons, merged_mods
