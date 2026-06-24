from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

class ChildWindow(QMainWindow):
    """Container window for displaying specific tabs in detached frames."""

    def __init__(self, title: str, widget_class: type, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)
        
        # Instantiate a fresh widget copy to display in this window
        self.widget = widget_class()
        self.setCentralWidget(self.widget)
        self.setWindowFlags(Qt.Window)

    def closeEvent(self, event: Any) -> None:
        if self.parent() and hasattr(self.parent(), "window_manager"):
            self.parent().window_manager.on_window_closed(self.windowTitle())
        super().closeEvent(event)

class WindowManager:
    """Manages sub-windows to guarantee zero-duplicate instances for each title."""

    def __init__(self, parent_window: QMainWindow) -> None:
        self.parent_window = parent_window
        self.parent_window.window_manager = self
        self.active_windows: dict[str, ChildWindow] = {}

    def open_window(self, title: str, widget_class: type) -> None:
        """Opens a separate window or focuses the existing one if already open."""
        if title in self.active_windows:
            win = self.active_windows[title]
            win.show()
            win.raise_()
            win.activateWindow()
        else:
            win = ChildWindow(title, widget_class, self.parent_window)
            self.active_windows[title] = win
            win.show()

    def on_window_closed(self, title: str) -> None:
        if title in self.active_windows:
            del self.active_windows[title]
