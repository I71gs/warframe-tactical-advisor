from PySide6.QtCore import QRunnable
from src.core.app_context import AppContext
from src.utils.logger import logger

class PluginWorker(QRunnable):
    """Background worker to load custom plugins."""

    def run(self) -> None:
        try:
            context = AppContext()
            logger.info("Scanning and loading custom plugins in background...")
            from src.core.plugin_manager import PluginManager
            PluginManager().load_plugins()
            logger.info("Plugins loaded successfully.")
            context.event_bus.publish("PLUGINS_LOADED")
            context.event_bus.publish("NOTIFICATION", {"message": "Custom plugins loaded successfully."})
        except Exception as exc:
            logger.error("Background plugin loading failed: %s", exc)
