from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from src.gui.widgets.circle_progress import CircleProgress
from src.core.theme_manager import ThemeManager

def test_circle_progress_painting() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Initialize widget
    widget = CircleProgress(size=100, width=5.0, label="Readiness")
    widget.setValue(45.0)
    assert widget.value == 45.0
    
    # Test painting mock with all registered themes
    tm = ThemeManager()
    themes = ["Dark", "Light", "Orokin", "Lotus", "Corpus", "Zariman", "Grineer"]
    
    for theme in themes:
        tm.save_active_theme(theme)
        # Call paintEvent indirectly via repaint/render checks
        widget.update()
        # Verify cached color state updates
        active_name, colors = widget.get_cached_theme_colors()
        assert active_name == theme
        assert "ACCENT" in colors
        assert "TEXT" in colors
        assert "MUTED" in colors
        
    # Reset to default
    tm.save_active_theme("Dark")
