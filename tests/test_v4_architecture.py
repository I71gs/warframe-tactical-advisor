import sys
from pathlib import Path
from src.core.app_context import AppContext
from src.utils.event_bus import EventBus
from src.utils.error_handler import handle_exception, CRASH_LOG_PATH
from src.core.workers.plugin_worker import PluginWorker
from src.core.workers.backup_worker import BackupWorker
from src.core.workers.snapshot_worker import SnapshotWorker

def test_app_context() -> None:
    context1 = AppContext()
    context2 = AppContext()
    assert context1 is context2
    assert context1.player_service is not None
    assert context1.progression_service is not None
    assert context1.build_service is not None
    assert context1.resource_service is not None
    assert context1.report_service is not None

def test_event_bus() -> None:
    bus = EventBus()
    events = []
    
    def callback(data: dict) -> None:
        events.append(data.get("val"))
        
    bus.subscribe("TEST_EVENT", callback)
    bus.publish("TEST_EVENT", {"val": 42})
    
    assert len(events) == 1
    assert events[0] == 42

def test_background_workers() -> None:
    # Run synchronously to check they don't throw errors
    PluginWorker().run()
    BackupWorker().run()
    SnapshotWorker().run()

def test_error_handler() -> None:
    if CRASH_LOG_PATH.exists():
        try:
            CRASH_LOG_PATH.unlink()
        except Exception:
            pass
        
    try:
        raise ValueError("Simulated Architecture Test Exception")
    except ValueError:
        exc_type, exc_val, exc_tb = sys.exc_info()
        handle_exception(exc_type, exc_val, exc_tb)
        
    assert CRASH_LOG_PATH.exists()
    content = CRASH_LOG_PATH.read_text(encoding='utf-8')
    assert "Simulated Architecture Test Exception" in content
