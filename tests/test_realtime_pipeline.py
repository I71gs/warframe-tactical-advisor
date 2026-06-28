from __future__ import annotations
import unittest.mock
from PySide6.QtWidgets import QApplication
from src.core.app_context import AppContext
from src.services.world_state_service import WorldStateService
from src.core.profiler import Profiler
from src.gui.performance_dashboard import PerformanceDashboard


def test_world_state_online_reconnect() -> None:
    """Verifies that the world state service handles API connection status and returns valid data."""
    ctx = AppContext()
    wss = WorldStateService(ctx)
    state = wss.get_world_state()
    # Should gracefully return a dictionary (even if empty or mock fallback when offline)
    assert isinstance(state, dict)
    assert "fissures" in state or "alerts" in state


def test_telemetry_profiler_performance() -> None:
    """Validates that real-time profiling metrics (DB latency, memory usage) are within safe parameters."""
    profiler = Profiler()
    report = profiler.run_profiling()
    
    assert "database_latency_ms" in report
    assert "memory_usage_mb" in report
    assert "cache_hit_rate_pct" in report
    
    # Latency check: Local SQLite query latency should be extremely low (< 50ms)
    assert report["database_latency_ms"] < 50.0
    # Memory check: Current Python process memory usage should be within a safe envelope (< 500 MB)
    assert report["memory_usage_mb"] < 500.0


def test_performance_dashboard_widgets() -> None:
    """Verifies that the PerformanceDashboard telemetries bind correctly and update without error."""
    # Ensure a QApplication instance is initialized
    app = QApplication.instance() or QApplication([])
    
    dashboard = PerformanceDashboard()
    
    # Run a single telemetry cycle update
    dashboard.update_telemetry()
    
    # Verify that the telemetry labels display non-empty readings
    assert "%" in dashboard.cpu_lbl.text()
    assert "MB" in dashboard.mem_lbl.text()
    assert "ms" in dashboard.db_lbl.text()
    assert "ms" in dashboard.refresh_lbl.text()
    
    # Ensure progress bars have valid ranges
    assert dashboard.cpu_bar.minimum() == 0
    assert dashboard.mem_bar.maximum() == 1024
    
    dashboard.close()


def test_world_state_mock_offline_fallback() -> None:
    """Simulates connection failure to ensure graceful fallback to offline cached modes."""
    ctx = AppContext()
    wss = WorldStateService(ctx)
    
    # Mocking urlopen to raise an exception connection error
    with unittest.mock.patch("urllib.request.urlopen", side_effect=Exception("Connection timed out")):
        state = wss.get_world_state()
        # Fallback should deliver structured elements to avoid UI layout disruption
        assert isinstance(state, dict)
        assert "fissures" in state
        assert "alerts" in state
