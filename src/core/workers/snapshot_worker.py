from PySide6.QtCore import QRunnable
from src.core.app_context import AppContext
from src.utils.logger import logger

class SnapshotWorker(QRunnable):
    """Background worker to record progression snapshot."""

    def run(self) -> None:
        try:
            context = AppContext()
            logger.info("Recording progression snapshot...")
            player = context.player_service.get_player()
            context.progression_service.pe.record_progress_snapshot(player)
            logger.info("Progression snapshot recorded successfully.")
            context.event_bus.publish("SNAPSHOT_CREATED")
            context.event_bus.publish("NOTIFICATION", {"message": "Progression snapshot created."})
        except Exception as exc:
            logger.error("Background snapshot recording failed: %s", exc)
