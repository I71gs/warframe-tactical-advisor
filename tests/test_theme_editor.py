from __future__ import annotations
import json
import pytest
import unittest.mock
from src.core.theme_manager import ThemeManager

def test_theme_manager_custom_dirs(tmp_path) -> None:
    themes_dir = tmp_path
    custom_dir = themes_dir / "custom"
    custom_dir.mkdir(parents=True, exist_ok=True)
    custom_theme_file = custom_dir / "my_custom.json"
    with open(custom_theme_file, "w", encoding="utf-8") as f:
        json.dump({
            "name": "My Custom Test",
            "PRIMARY": "#111111",
            "SECONDARY": "#222222",
            "ACCENT": "#333333",
            "TEXT": "#444444",
            "MUTED": "#555555",
            "CARD": "#666666"
        }, f)
        
    with unittest.mock.patch("src.core.theme_manager.THEMES_DIR", themes_dir):
        with unittest.mock.patch("src.core.theme_manager.CUSTOM_THEME_FILE", themes_dir / "custom_theme.json"):
            tm = ThemeManager()
            assert "My Custom Test" in tm.get_themes()

def test_theme_manager_default_themes(tmp_path) -> None:
    themes_dir = tmp_path
    with unittest.mock.patch("src.core.theme_manager.THEMES_DIR", themes_dir):
        with unittest.mock.patch("src.core.theme_manager.CUSTOM_THEME_FILE", themes_dir / "custom_theme.json"):
            tm = ThemeManager()
            assert "Dark" in tm.get_themes()
            assert "Light" in tm.get_themes()

def test_theme_manager_save_active(tmp_path) -> None:
    themes_dir = tmp_path
    with unittest.mock.patch("src.core.theme_manager.THEMES_DIR", themes_dir):
        with unittest.mock.patch("src.core.theme_manager.CUSTOM_THEME_FILE", themes_dir / "custom_theme.json"):
            tm = ThemeManager()
            tm.save_active_theme("Light")
            assert tm.get_active_theme_name() == "Light"
