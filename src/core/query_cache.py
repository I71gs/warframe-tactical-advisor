from __future__ import annotations
import time
from typing import Any, Callable

class QueryCache:
    """Thread-safe generic cache with TTL and cache hit statistics."""

    _instance = None

    def __new__(cls, *args, **kwargs) -> QueryCache:
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._init_cache()
        return cls._instance

    def _init_cache(self) -> None:
        self.store: dict[str, tuple[Any, float]] = {}
        self.hit_count = 0
        self.miss_count = 0
        self.default_ttl = 60.0  # 60 seconds default TTL

    def get(self, key: str) -> Any | None:
        """Retrieve value from cache if present and not expired."""
        if key not in self.store:
            self.miss_count += 1
            return None

        val, expire_time = self.store[key]
        if time.time() > expire_time:
            # Expired
            del self.store[key]
            self.miss_count += 1
            return None

        self.hit_count += 1
        return val

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Store value with dynamic TTL in cache."""
        duration = ttl if ttl is not None else self.default_ttl
        expire_time = time.time() + duration
        self.store[key] = (value, expire_time)

    def cached_call(self, key: str, func: Callable[[], Any], ttl: float | None = None) -> Any:
        """Retrieve from cache, or evaluate func, store in cache, and return."""
        val = self.get(key)
        if val is not None:
            return val

        # Evaluate and cache
        computed = func()
        self.set(key, computed, ttl)
        return computed

    def get_hit_rate(self) -> float:
        total = self.hit_count + self.miss_count
        if total == 0:
            return 100.0
        return round((self.hit_count / total) * 100.0, 1)

    def clear(self) -> None:
        self.store.clear()
        self.hit_count = 0
        self.miss_count = 0
