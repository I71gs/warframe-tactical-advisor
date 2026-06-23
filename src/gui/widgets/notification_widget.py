from __future__ import annotations
from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtGui import QColor

class NotificationWidget(QWidget):
    """Discord-style toast notification popup widget."""

    def __init__(self, message: str, level: str = "info", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # Style colors matching SHEET dark mode
        colors = {
            "info": ("#00a3cc", "#0d1b2a"),
            "warning": ("#ffb76b", "#2a1b0d"),
            "error": ("#ef4444", "#2a0d0d"),
            "success": ("#22c55e", "#0d2a1b")
        }
        border_color, bg_color = colors.get(level.lower(), colors["info"])

        # Layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)

        self.label = QLabel(message)
        self.label.setStyleSheet("color: #e6eef6; font-size: 12px; font-weight: bold;")
        self.layout.addWidget(self.label)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
            }}
        """)

        # Opacity effect for fading
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # Animations
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fade_out)

    def show_toast(self, duration_ms: int = 3000) -> None:
        """Position and display the toast with transition animations."""
        self.opacity_effect.setOpacity(0.0)
        self.show()
        
        # Position at bottom-right of screen or parent window
        parent = self.parentWidget()
        if parent:
            # Get bottom-right of parent window
            parent_geom = parent.geometry()
            global_pos = parent.mapToGlobal(QPoint(parent_geom.width() - self.width() - 20, parent_geom.height() - self.height() - 40))
            self.move(global_pos)
        else:
            # Default to primary screen bottom-right
            from PySide6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 60)

        # Fade in
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
        
        self.timer.start(duration_ms)

    def fade_out(self) -> None:
        """Fade out and close the widget."""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()
