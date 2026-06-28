from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from src.gui.overlay import OverlayWindow

def test_overlay_initialization() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    parent = QMainWindow()
    
    overlay = OverlayWindow(parent)
    assert overlay.main_window is parent
    assert overlay.active_tab == 0
    
    # Test tab switching
    overlay.switch_tab(1)
    assert overlay.active_tab == 1
    
    overlay.switch_tab(2)
    assert overlay.active_tab == 2

def test_overlay_close_and_restore() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    parent = QMainWindow()
    parent.show()
    
    overlay = OverlayWindow(parent)
    overlay.show()
    assert overlay.isVisible()
    
    # Click restore button
    overlay.restore_main_window()
    assert overlay.isHidden()
    assert parent.isVisible()
