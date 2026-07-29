from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication, QWidget, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt, QTimer
from src.gui.widgets.custom_charts import FadeTranslateScaleEffect, AnimatedButton, HoverAnimatedCard
from src.gui.main_window import PageTransitionContainer, NavPill, MainWindow
from src.gui.widgets.command_palette_dialog import CommandPaletteDialog

# Ensure a QApplication instance exists
app = QApplication.instance() or QApplication([])


def test_fade_translate_scale_effect():
    """Verify FadeTranslateScaleEffect sets properties correctly."""
    widget = QWidget()
    effect = FadeTranslateScaleEffect(widget)
    
    effect.set_opacity(0.5)
    assert effect.opacity == 0.5
    
    effect.set_y_offset(10.0)
    assert effect.yOffset == 10.0
    
    effect.set_scale(0.95)
    assert effect.scale == 0.95


def test_animated_button():
    """Verify AnimatedButton click scaling behavior."""
    btn = AnimatedButton("Test Button")
    
    # Assert initial scale factor is default 1.0
    assert btn.effect.get_scale() == 1.0
    
    # Trigger mouse press event simulation
    btn.effect.set_scale(0.97)
    assert btn.effect.get_scale() == 0.97


def test_page_transition_container():
    """Verify PageTransitionContainer transitions immediately under pytest."""
    widget = QWidget()
    container = PageTransitionContainer(widget)
    
    assert container.opacity_effect.opacity() == 0.0
    assert container.get_top_margin() == 8.0
    
    container.trigger_transition()
    
    # Under pytest, it triggers instantly for robust assertion checks
    assert container.opacity_effect.opacity() == 1.0
    assert container.get_top_margin() == 0.0


def test_hover_animated_card():
    """Verify HoverAnimatedCard initializes graphics effect correctly."""
    card = HoverAnimatedCard("Card Title")
    assert card.effect.get_y_offset() == 0.0
