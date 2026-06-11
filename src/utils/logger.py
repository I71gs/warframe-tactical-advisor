from typing import Any
import logging
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'app.log'

def setup_app_logger() -> Any:
    """Method setup_app_logger."""
    logger = logging.getLogger('warframe_tactical_advisor')
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
logger = setup_app_logger()