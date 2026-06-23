from __future__ import annotations
from src.core.theme_manager import ThemeManager

def test_theme_manager_basic() -> None:
    tm = ThemeManager()
    themes = tm.get_themes()
    assert len(themes) > 0
    assert "Dark" in themes
    assert "Light" in themes
    assert "Custom Theme" in themes

    colors = tm.get_theme_colors("Dark")
    assert colors["PRIMARY"] == "#0b1220"

    active_theme = tm.get_active_theme_name()
    assert isinstance(active_theme, str)

def test_theme_manager_save_active() -> None:
    tm = ThemeManager()
    tm.save_active_theme("Light")
    assert tm.get_active_theme_name() == "Light"
    # Restore Dark for other tests
    tm.save_active_theme("Dark")
    assert tm.get_active_theme_name() == "Dark"

def test_theme_manager_fallback_flow() -> None:
    tm = ThemeManager()
    colors = tm.get_theme_colors("NonExistentThemeName123")
    # Should fallback to Dark
    assert colors["PRIMARY"] == "#0b1220"

def test_theme_manager_colors_check() -> None:
    tm = ThemeManager()
    for tname in ["Dark", "Light", "Lotus", "Corpus", "Orokin", "Zariman"]:
        colors = tm.get_theme_colors(tname)
        assert "PRIMARY" in colors
        assert "SECONDARY" in colors
        assert "ACCENT" in colors
        assert "TEXT" in colors
        assert "CARD" in colors

def test_theme_manager_custom_theme_load() -> None:
    tm = ThemeManager()
    colors = tm.get_theme_colors("Custom Theme")
    assert colors is not None
    assert "PRIMARY" in colors
