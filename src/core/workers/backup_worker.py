from PySide6.QtCore import QRunnable
from src.core.app_context import AppContext
from src.utils.logger import logger

class BackupWorker(QRunnable):
    """Background worker for database backup."""

    def run(self) -> None:
        try:
            context = AppContext()
            logger.info("Starting background backup...")
            backup_path = context.player_service.backup_profile()
            logger.info("Background backup successful: %s", backup_path)
            context.event_bus.publish("NOTIFICATION", {"message": f"Backup successful: {backup_path}"})
        except Exception as exc:
            logger.error("Background backup failed: %s", exc)
