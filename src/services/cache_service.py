from __future__ import annotations
import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any
from src.utils.logger import logger

if TYPE_CHECKING:
    from src.core.app_context import AppContext

ROOT = Path(__file__).resolve().parents[2]
CACHE_FILE = ROOT / 'cache' / 'app_cache.json'
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

class CacheService:
    """Manages memory and JSON disk caching for calculations, recommendations, and wiki searches."""

    def __init__(self, context: AppContext, cache_file: Path | str | None = None) -> None:
        self.context = context
        self.cache_file = Path(cache_file) if cache_file else CACHE_FILE
        self.memory_cache: dict[str, dict[str, Any]] = {}
        self.load_disk_cache()

        # Invalidate cache on any profile modifications
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.clear_volatile_cache())

    def load_disk_cache(self) -> None:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.memory_cache = json.load(f)
            except Exception as exc:
                logger.error("Failed to load cache from disk: %s", exc)
                self.memory_cache = {}

    def save_disk_cache(self) -> None:
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory_cache, f, indent=4)
        except Exception as exc:
            logger.error("Failed to save cache to disk: %s", exc)

    def get(self, key: str) -> Any | None:
        entry = self.memory_cache.get(key)
        if entry:
            expiry = entry.get("expiry", 0)
            if expiry == 0 or expiry > time.time():
                return entry.get("value")
            else:
                self.invalidate(key)
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 0) -> None:
        expiry = (time.time() + ttl_seconds) if ttl_seconds > 0 else 0
        self.memory_cache[key] = {
            "value": value,
            "expiry": expiry
        }
        self.save_disk_cache()

    def invalidate(self, key: str) -> None:
        if key in self.memory_cache:
            del self.memory_cache[key]
            self.save_disk_cache()

    def clear(self) -> None:
        self.memory_cache.clear()
        self.save_disk_cache()

    def clear_volatile_cache(self) -> None:
        """Clear scores and recommendations, keeping wiki and general search caches intact."""
        keys_to_remove = [k for k in self.memory_cache if not k.startswith("wiki_") and not k.startswith("search_")]
        for k in keys_to_remove:
            del self.memory_cache[k]
        self.save_disk_cache()
        logger.info("Volatile memory cache invalidated on profile update.")
