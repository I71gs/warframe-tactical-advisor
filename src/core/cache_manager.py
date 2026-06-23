from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class CacheManager:
    """Manages file-based JSON caching with lazy verification and expiration metrics."""

    def __init__(self, cache_dir: Path | str | None = None) -> None:
        self.cache_dir = Path(cache_dir) if cache_dir else CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, cache_name: str) -> Path:
        if not cache_name.endswith('.json'):
            cache_name += '.json'
        return self.cache_dir / cache_name

    def load_cache(self, cache_name: str) -> dict[str, Any]:
        """Load JSON data from cache, returns empty dict if missing/invalid."""
        path = self._get_path(cache_name)
        if not path.exists():
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
        return {}

    def save_cache(self, cache_name: str, data: dict[str, Any]) -> None:
        """Save JSON data to cache alongside a timestamp."""
        path = self._get_path(cache_name)
        payload = {
            "_timestamp": time.time(),
            "data": data
        }
        try:
            with open(path, 'w', encoding='utf-8') as fh:
                json.dump(payload, fh, indent=4)
        except Exception:
            pass

    def is_expired(self, cache_name: str, days: int = 7) -> bool:
        """Check if cached file timestamp exceeds the specified days."""
        path = self._get_path(cache_name)
        if not path.exists():
            return True
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                payload = json.load(fh)
                ts = payload.get("_timestamp", 0)
                elapsed = time.time() - ts
                return elapsed > (days * 86400)
        except Exception:
            return True

    def clear_cache(self, cache_name: str) -> None:
        """Delete specific cache file."""
        path = self._get_path(cache_name)
        if path.exists():
            try:
                path.unlink()
            except Exception:
                pass
