from __future__ import annotations
import tempfile
import os
from pathlib import Path
from src.core.session_analytics import SessionAnalytics

def test_session_analytics_logging() -> None:
    fd, temp_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        analytics = SessionAnalytics(logs_filepath=temp_path)
        
        # Test Log session
        record = analytics.log_session(
            duration_minutes=30,
            tasks_completed=2,
            tasks_total=3,
            resources={"Credits": 250000, "Endo": 1500}
        )
        assert record["duration"] == 30
        assert record["efficiency"] == 66.7
        
        # Test load
        logs = analytics.load_logs()
        assert len(logs) == 1
        
        # Test daily productivity
        prod = analytics.get_daily_productivity()
        assert prod["sessions_count"] == 1
        assert prod["total_duration_minutes"] == 30
        assert prod["resources_collected"]["Credits"] == 250000
        
        # Test historical efficiency
        history = analytics.get_historical_efficiency()
        assert len(history) == 1
        assert history[0]["average_efficiency"] == 66.7
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_session_analytics_empty_file() -> None:
    analytics = SessionAnalytics(logs_filepath="/non/existent/file.json")
    logs = analytics.load_logs()
    assert logs == []
    prod = analytics.get_daily_productivity()
    assert prod["sessions_count"] == 0
    assert prod["total_duration_minutes"] == 0
    assert prod["average_efficiency"] == 0.0
