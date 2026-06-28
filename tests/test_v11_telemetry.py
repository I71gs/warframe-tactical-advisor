from __future__ import annotations
import sys
import time
import pytest
from PySide6.QtWidgets import QApplication
from src.core.query_cache import QueryCache
from src.gui.widgets.circle_progress import CircleProgress


@pytest.mark.parametrize("cache_key", [f"key_{i}" for i in range(40)])
def test_query_cache_multi_keys(cache_key) -> None:
    """Verifies that QueryCache stores and retrieves values across different keys."""
    cache = QueryCache()
    cache.set(cache_key, f"val_{cache_key}", ttl=2.0)
    assert cache.get(cache_key) == f"val_{cache_key}"


@pytest.mark.parametrize("progress_val", [float(i) for i in range(35)])
def test_circular_progress_values(progress_val) -> None:
    """Verifies that CircleProgress handles wide values bounds without crashing."""
    app = QApplication.instance() or QApplication(sys.argv)
    prog = CircleProgress(size=50)
    prog.setValue(progress_val)
    assert prog.value == progress_val


def test_query_cache_invalidation() -> None:
    """Verifies that QueryCache invalidates correctly after expiration or explicit clears."""
    cache = QueryCache()
    cache.set("temp_key", "temp_val", ttl=0.1)
    time.sleep(0.15)
    assert cache.get("temp_key") is None

    cache.set("clear_key", "val")
    cache.clear()
    assert cache.get("clear_key") is None


@pytest.mark.parametrize("invalid_val", [-10.0, 150.0, 500.0, -100.0, 200.0, 300.0])
def test_circular_progress_extreme_bounds(invalid_val) -> None:
    """Verifies circle progress handles negative and extreme bounds correctly."""
    app = QApplication.instance() or QApplication(sys.argv)
    prog = CircleProgress(size=50)
    prog.setValue(invalid_val)
    assert prog.value == invalid_val
