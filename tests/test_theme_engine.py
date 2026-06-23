from __future__ import annotations
from src.core.theme_engine import ThemeEngine

def test_theme_engine_compilation() -> None:
    te = ThemeEngine()
    colors = {
        "PRIMARY": "#111111",
        "SECONDARY": "#222222",
        "ACCENT": "#333333",
        "TEXT": "#444444",
        "MUTED": "#555555",
        "CARD": "#666666"
    }
    stylesheet = te.compile_stylesheet(colors)
    assert "#111111" in stylesheet
    assert "#222222" in stylesheet
    assert "#333333" in stylesheet
    assert "#444444" in stylesheet
    assert "#666666" in stylesheet

def test_theme_engine_fallback() -> None:
    te = ThemeEngine()
    stylesheet = te.compile_stylesheet({})
    assert "#0b1220" in stylesheet  # default primary fallback
