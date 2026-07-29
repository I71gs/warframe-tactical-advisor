from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from src.core.settings_manager import SettingsManager

ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = ROOT / "src" / "resources" / "themes"
THEMES_DIR.mkdir(parents=True, exist_ok=True)
CUSTOM_THEME_FILE = THEMES_DIR / "custom_theme.json"

class ThemeManager:
    """Manages active theme selectors, base Dark/Light themes, and Warframe accent packs."""

    def __init__(self) -> None:
        self.settings = SettingsManager()
        self.themes: dict[str, dict[str, str]] = {}
        self._setup_themes()
        self.load_themes_from_files()

    def _setup_themes(self) -> None:
        # Base Themes
        self.base_themes = {
            "Dark": {
                "PRIMARY": "#0b1220",
                "SECONDARY": "#0f1724",
                "ACCENT": "#00a3cc",
                "TEXT": "#e6eef6",
                "MUTED": "#9fb6c8",
                "CARD": "#0f1a24"
            },
            "Light": {
                "PRIMARY": "#f8fafc",
                "SECONDARY": "#e2e8f0",
                "ACCENT": "#0284c7",
                "TEXT": "#0f172a",
                "MUTED": "#64748b",
                "CARD": "#ffffff"
            },
            "Custom Theme": {
                "PRIMARY": "#05111a",
                "SECONDARY": "#0c1e2d",
                "ACCENT": "#33ffaa",
                "TEXT": "#dcfce7",
                "MUTED": "#86efac",
                "CARD": "#0f273c"
            }
        }

        # Accent Packs
        self.accent_packs = {
            "None": {},
            "Lotus": {
                "ACCENT": "#caa3ff",
                "SECONDARY": "#18112d",
                "CARD": "#1f1832"
            },
            "Corpus": {
                "ACCENT": "#00d4ff",
                "SECONDARY": "#0f1d2c",
                "CARD": "#122334"
            },
            "Orokin": {
                "ACCENT": "#cfad64",
                "SECONDARY": "#1c1810",
                "CARD": "#221d15"
            },
            "Zariman": {
                "ACCENT": "#6fffe8",
                "SECONDARY": "#122421",
                "CARD": "#162b28"
            },
            "Grineer": {
                "ACCENT": "#a35d3d",
                "SECONDARY": "#1d1814",
                "CARD": "#231f1c"
            },
            "Cosmic Twilight": {
                "ACCENT": "#bb86fc",
                "SECONDARY": "#170b2c",
                "CARD": "#1c1134"
            }
        }

    def load_themes_from_files(self) -> None:
        """Scan THEMES_DIR and themes/custom/ for base JSON theme config files, ignoring legacy ones."""
        self.themes.clear()
        
        # Load pre-defined bases first
        self.themes.update(self.base_themes)
        
        paths = list(THEMES_DIR.glob("*.json"))
        custom_dir = THEMES_DIR / "custom"
        if custom_dir.exists():
            paths.extend(custom_dir.glob("*.json"))

        for p in paths:
            # Skip legacy full Warframe themes to avoid cluttering options
            if p.stem in ["corpus", "grineer", "lotus", "orokin", "zariman", "cosmic_twilight"]:
                continue
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "PRIMARY" in data:
                        name = data.get("name") or p.stem.capitalize()
                        if p.name == "custom_theme.json":
                            name = "Custom Theme"
                        self.themes[name] = data
            except Exception:
                pass

    def get_themes(self) -> list[str]:
        """Returns list of all available theme combinations (Base Theme + Accent Pack)."""
        self.load_themes_from_files()
        list_themes = []
        for base in self.themes.keys():
            list_themes.append(base)
            for pack in self.accent_packs.keys():
                if pack != "None":
                    list_themes.append(f"{base} ({pack})")
        return list_themes

    def get_theme_colors(self, name: str) -> dict[str, str]:
        """Returns color maps for a given base theme + accent pack name."""
        self.load_themes_from_files()
        base_name = "Dark"
        accent_name = "None"
        
        if " (" in name and name.endswith(")"):
            try:
                base_name, rest = name.split(" (", 1)
                accent_name = rest[:-1]
            except Exception:
                base_name = "Dark"
                accent_name = "None"
        elif name in self.themes:
            base_name = name
            accent_name = "None"
            
        # Retrieve base palette
        colors = dict(self.themes.get(base_name, self.themes.get("Dark", self.base_themes["Dark"])))
        
        # Apply accent pack overrides
        pack_overrides = self.accent_packs.get(accent_name, {})
        for key, val in pack_overrides.items():
            colors[key] = val
            
        return colors

    def get_active_theme_name(self) -> str:
        """Fetch saved active theme, default to 'Dark (Cosmic Twilight)'."""
        self.settings.load()
        return self.settings.get("active_theme", "Dark (Cosmic Twilight)")

    def save_active_theme(self, name: str) -> None:
        """Saves selected theme selection to settings."""
        self.settings.update(active_theme=name)
        self.settings.save()
