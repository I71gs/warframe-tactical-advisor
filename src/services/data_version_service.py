from __future__ import annotations
import json
from pathlib import Path
from typing import TYPE_CHECKING
from src.utils.logger import logger

if TYPE_CHECKING:
    from src.core.app_context import AppContext

ROOT = Path(__file__).resolve().parents[2]
METADATA_PATH = ROOT / "src" / "resources" / "data" / "metadata.json"

class DataVersionService:
    """Tracks database versions, handles compatibility, and validates local datasets."""

    def __init__(self, context: AppContext) -> None:
        self.context = context

    def get_data_version(self) -> str:
        if METADATA_PATH.exists():
            try:
                with open(METADATA_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("version", "unknown")
            except Exception as e:
                logger.warning("Failed to load metadata.json: %s", e)
        return "unknown"

    def is_compatible(self, required_version: str) -> bool:
        current = self.get_data_version()
        if current == "unknown" or current == required_version:
            return True
        try:
            cur_parts = [int(p) for p in current.split(".")]
            req_parts = [int(p) for p in required_version.split(".")]
            return cur_parts >= req_parts
        except Exception:
            return True

    def validate_datasets(self) -> bool:
        """Confirms that essential data JSON files exist and are well-formed."""
        required = ["arcanes.json", "mods.json", "quests.json", "weapons.json", "warframes.json"]
        data_dir = ROOT / "src" / "resources" / "data"
        
        for name in required:
            path = data_dir / name
            if not path.exists():
                logger.error("Required dataset missing: %s", name)
                return False
            try:
                with open(path, "r", encoding="utf-8") as f:
                    json.load(f)
            except Exception as e:
                logger.error("Dataset %s is malformed: %s", name, e)
                return False
        return True
