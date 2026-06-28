from __future__ import annotations
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QFont

class CircleProgress(QWidget):
    """Rich Circular Progress indicator widget using QPainter."""

    def __init__(
        self,
        parent: QWidget | None = None,
        size: int = 80,
        width: float = 4.0,
        color: str = "#bb86fc",
        track_color: str = "rgba(255, 255, 255, 0.05)",
        label: str = ""
    ) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.pen_width = width
        self.color = QColor(color)
        self.track_color = QColor(track_color)
        self.value = 0.0
        self.max_value = 100.0
        self.label = label

    def setValue(self, val: float) -> None:
        self.value = float(val)
        self.update()

    def setRange(self, min_val: float, max_val: float) -> None:
        self.max_value = float(max_val) if max_val > 0 else 100.0
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        r = min(w, h) - self.pen_width * 2.0

        # Define bounds
        rect = QRectF(self.pen_width, self.pen_width, r, r)

        # Draw track
        track_pen = QPen(self.track_color)
        track_pen.setWidthF(self.pen_width)
        track_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Calculate span angle
        pct = max(0.0, min(1.0, self.value / self.max_value))
        span_angle = int(-pct * 360 * 16)

        # Draw progress arc (start at top: 90 degrees)
        prog_pen = QPen(self.color)
        prog_pen.setWidthF(self.pen_width)
        prog_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(prog_pen)
        painter.drawArc(rect, 90 * 16, span_angle)

        # Draw center text (large bold value)
        val_rect = self.rect()
        if self.label:
            val_rect.adjust(0, 0, 0, -12)

        font = QFont("Segoe UI", 11)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("#f0f6fc"))
        txt = f"{int(self.value)}%"
        painter.drawText(val_rect, Qt.AlignCenter, txt)

        # Draw uppercase diagnostic sub-label
        if self.label:
            lbl_rect = self.rect()
            lbl_rect.adjust(0, 16, 0, 0)
            lbl_font = QFont("Segoe UI", 7)
            lbl_font.setBold(True)
            painter.setFont(lbl_font)
            painter.setPen(QColor("#8e85a6"))
            painter.drawText(lbl_rect, Qt.AlignCenter, self.label.upper())

        painter.end()
