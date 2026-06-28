import sys
import traceback
import json
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QMessageBox, QApplication
from src.utils.logger import logger

ROOT = Path(__file__).resolve().parents[2]
CRASH_LOG_PATH = ROOT / 'crash.log'

def handle_exception(exc_type, exc_value, exc_traceback) -> None:
    """Global unhandled exception interception hook."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Generate log entry
    timestamp = datetime.now().isoformat()
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = "".join(tb_lines)

    crash_data = {
        "timestamp": timestamp,
        "exception_type": exc_type.__name__,
        "exception_value": str(exc_value),
        "traceback": tb_text,
        "python_version": sys.version,
        "platform": sys.platform
    }

    try:
        # Append structured JSON lines
        with open(CRASH_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(crash_data) + "\n")
    except Exception as exc:
        logger.error("Failed to write to crash.log: %s", exc)

    logger.error("Unhandled Exception: %s: %s\n%s", exc_type.__name__, exc_value, tb_text)

    # Check if a QApplication is running to show graphical crash dialog (skip during tests)
    app = QApplication.instance()
    if app and 'pytest' not in sys.modules:
        try:
            QMessageBox.critical(
                None,
                "Application Crash",
                f"An unexpected error has occurred.\n\n"
                f"Error: {exc_type.__name__}: {exc_value}\n\n"
                f"Details have been written to crash.log in structured JSON format.",
                QMessageBox.Ok
            )
        except Exception:
            pass

def install_error_handler() -> None:
    """Register custom exception hook wrapper."""
    sys.excepthook = handle_exception
