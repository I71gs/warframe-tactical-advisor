from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from src.core.settings_manager import SettingsManager

ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = ROOT / "themes"
THEMES_DIR.mkdir(parents=True, exist_ok=True)
CUSTOM_THEME_FILE = THEMES_DIR / "custom_theme.json"

BUILT_IN_THEMES = {
    "Dark": {
        "PRIMARY": "#0b1220",
        "SECONDARY": "#0f1724",
        "ACCENT": "#00a3cc",
        "TEXT": "#e6eef6",
        "MUTED": "#9fb6c8",
        "CARD": "#0f1a24"
    },
    "Light": {
        "PRIMARY": "#f1f5f9",
        "SECONDARY": "#e2e8f0",
        "ACCENT": "#007ea7",
        "TEXT": "#0f172a",
        "MUTED": "#64748b",
        "CARD": "#ffffff"
    },
    "Lotus": {
        "PRIMARY": "#1c1124",
        "SECONDARY": "#2b1a37",
        "ACCENT": "#e056fd",
        "TEXT": "#f9f5ff",
        "MUTED": "#a29bfe",
        "CARD": "#382547"
    },
    "Corpus": {
        "PRIMARY": "#0d1f2d",
        "SECONDARY": "#1d2d44",
        "ACCENT": "#f2a65a",
        "TEXT": "#f0ebd8",
        "MUTED": "#748cab",
        "CARD": "#1d3557"
    },
    "Orokin": {
        "PRIMARY": "#fdfbf7",
        "SECONDARY": "#f4efe6",
        "ACCENT": "#cfad64",
        "TEXT": "#1c1917",
        "MUTED": "#78716c",
        "CARD": "#ffffff"
    },
    "Zariman": {
        "PRIMARY": "#071a17",
        "SECONDARY": "#0f2d29",
        "ACCENT": "#20b2aa",
        "TEXT": "#e0f2f1",
        "MUTED": "#4db6ac",
        "CARD": "#123e38"
    }
}

class ThemeManager:
    """Manages active theme selectors, built-in themes, and custom theme.json loaders."""

    def __init__(self) -> None:
        self.settings = SettingsManager()
        self._ensure_sample_custom_theme()

    def _ensure_sample_custom_theme(self) -> None:
        if not CUSTOM_THEME_FILE.exists():
            sample = {
                "name": "Custom Zariman Blue",
                "PRIMARY": "#05111a",
                "SECONDARY": "#0c1e2d",
                "ACCENT": "#33ffaa",
                "TEXT": "#dcfce7",
                "MUTED": "#86efac",
                "CARD": "#0f273c"
            }
            try:
                with open(CUSTOM_THEME_FILE, 'w', encoding='utf-8') as f:
                    json.dump(sample, f, indent=4)
            except Exception:
                pass

    def get_themes(self) -> list[str]:
        """Returns list of all available theme names."""
        themes = list(BUILT_IN_THEMES.keys())
        themes.append("Custom Theme")
        return themes

    def get_theme_colors(self, name: str) -> dict[str, str]:
        """Returns color maps for a given theme name."""
        if name in BUILT_IN_THEMES:
            return BUILT_IN_THEMES[name]
            
        if name == "Custom Theme" and CUSTOM_THEME_FILE.exists():
            try:
                with open(CUSTOM_THEME_FILE, 'r', encoding='utf-8') as f:
                    custom_data = json.load(f)
                    if isinstance(custom_data, dict):
                        return custom_data
            except Exception:
                pass
                
        return BUILT_IN_THEMES["Dark"]

    def get_active_theme_name(self) -> str:
        """Fetch saved active theme or default to Dark."""
        self.settings.load()
        return self.settings.get("active_theme", "Dark")

    def save_active_theme(self, name: str) -> None:
        """Saves selected theme selection to settings."""
        self.settings.update(active_theme=name)
        self.settings.save()
