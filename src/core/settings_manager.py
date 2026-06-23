from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from src.utils.logger import logger

ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = ROOT / 'settings.json'
BACKUP_DIR = ROOT / 'backups'
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_SETTINGS = {
    'version': '1.0',
    'dark_mode': True,
    'auto_refresh': True,
    'remember_size': True,
    'remember_tab': True,
    'last_tab_index': 0,
    'window_size': {'width': 1000, 'height': 700},
    'current_profile': 'default',
}

class SettingsManager:
    """Handles persistent settings for the application."""

    def __init__(self, path: Path | str | None = None) -> None:
        """Load settings from file or use defaults."""
        self.path = Path(path) if path else SETTINGS_PATH
        self.values = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self) -> None:
        """Read settings from disk into memory."""
        if not self.path.exists():
            return
        try:
            with open(self.path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                raise ValueError('Settings file is not a JSON object')
            self.values.update({k: v for k, v in data.items() if k in self.values})
        except Exception as exc:
            logger.warning('Failed to load settings: %s', exc)

    def save(self) -> bool:
        """Persist settings to the JSON settings file."""
        try:
            with open(self.path, 'w', encoding='utf-8') as fh:
                json.dump(self.values, fh, indent=2)
            logger.info('Settings saved')
            return True
        except Exception as exc:
            logger.exception('Failed to save settings')
            return False

    def update(self, **kwargs: Any) -> None:
        """Update the in-memory settings dictionary."""
        for key, value in kwargs.items():
            if key in self.values:
                self.values[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Return a registered setting value or a fallback default."""
        return self.values.get(key, default)

    def get_backup_path(self) -> Path:
        """Return the backup directory used by the application."""
        return BACKUP_DIR
