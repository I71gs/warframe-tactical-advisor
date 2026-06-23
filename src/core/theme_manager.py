from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from src.core.settings_manager import SettingsManager

ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = ROOT / "themes"
THEMES_DIR.mkdir(parents=True, exist_ok=True)
CUSTOM_THEME_FILE = THEMES_DIR / "custom_theme.json"

class ThemeManager:
    """Manages active theme selectors, built-in themes, and custom theme.json loaders from files."""

    def __init__(self) -> None:
        self.settings = SettingsManager()
        self.themes: dict[str, dict[str, str]] = {}
        self._ensure_default_themes()
        self.load_themes_from_files()

    def _ensure_default_themes(self) -> None:
        # Fallback dictionary if disk files are empty or unreadable
        self.fallback_themes = {
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
            }
        }
        if not CUSTOM_THEME_FILE.exists():
            sample = {
                "name": "Custom Theme",
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

    def load_themes_from_files(self) -> None:
        """Scan THEMES_DIR for any json theme configuration files."""
        self.themes.clear()
        
        # Load any json files in themes/
        for p in THEMES_DIR.glob("*.json"):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "PRIMARY" in data:
                        name = data.get("name") or p.stem.capitalize()
                        # If it is custom_theme.json, name it "Custom Theme" to match GUI
                        if p.name == "custom_theme.json":
                            name = "Custom Theme"
                        self.themes[name] = data
            except Exception:
                pass
                
        # Fill in fallbacks if dark/light are missing
        for name, colors in self.fallback_themes.items():
            if name not in self.themes:
                self.themes[name] = colors

        # Register themes from PluginRegistry
        try:
            from src.core.plugin_registry import PluginRegistry
            for name, colors in PluginRegistry().themes.items():
                self.themes[name] = colors
        except Exception:
            pass

    def get_themes(self) -> list[str]:
        """Returns list of all available theme names."""
        self.load_themes_from_files()
        return sorted(list(self.themes.keys()))

    def get_theme_colors(self, name: str) -> dict[str, str]:
        """Returns color maps for a given theme name."""
        self.load_themes_from_files()
        if name in self.themes:
            return self.themes[name]
        return self.themes.get("Dark", self.fallback_themes["Dark"])

    def get_active_theme_name(self) -> str:
        """Fetch saved active theme or default to Dark."""
        self.settings.load()
        return self.settings.get("active_theme", "Dark")

    def save_active_theme(self, name: str) -> None:
        """Saves selected theme selection to settings."""
        self.settings.update(active_theme=name)
        self.settings.save()
