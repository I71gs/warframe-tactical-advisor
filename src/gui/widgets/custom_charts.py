from __future__ import annotations
import math
import sys
from typing import Any
from PySide6.QtWidgets import QWidget, QToolTip, QGraphicsEffect, QPushButton, QGroupBox
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient, QBrush, QPolygonF
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, Property, QEasingCurve, QPropertyAnimation, QParallelAnimationGroup, QSequentialAnimationGroup

class FadeTranslateScaleEffect(QGraphicsEffect):
    """Custom QGraphicsEffect supporting combined opacity, layout-safe vertical translation, and scaling from widget center."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._opacity = 1.0
        self._y_offset = 0.0
        self._scale = 1.0

    def get_opacity(self) -> float:
        return self._opacity

    def set_opacity(self, val: float) -> None:
        self._opacity = float(val)
        self.update()

    opacity = Property(float, get_opacity, set_opacity)

    def get_y_offset(self) -> float:
        return self._y_offset

    def set_y_offset(self, val: float) -> None:
        self._y_offset = float(val)
        self.update()

    yOffset = Property(float, get_y_offset, set_y_offset)

    def get_scale(self) -> float:
        return self._scale

    def set_scale(self, val: float) -> None:
        self._scale = float(val)
        self.update()

    scale = Property(float, get_scale, set_scale)

    def draw(self, painter: Any) -> None:
        if self._opacity <= 0.0:
            return
        painter.save()
        if self._opacity < 1.0:
            painter.setOpacity(self._opacity)

        w = self.sourceBoundingRect().width()
        h = self.sourceBoundingRect().height()
        cx = w / 2.0
        cy = h / 2.0

        painter.translate(cx, cy)
        if self._scale != 1.0:
            painter.scale(self._scale, self._scale)
        painter.translate(-cx, -cy)

        if self._y_offset != 0.0:
            painter.translate(0, self._y_offset)

        self.drawSource(painter)
        painter.restore()


class AnimatedButton(QPushButton):
    """Subclass of QPushButton providing smooth interactive press/release scaling (97% size)."""

    def __init__(self, text: str = "", parent: Any = None) -> None:
        super().__init__(text, parent)
        self.effect = FadeTranslateScaleEffect(self)
        self.setGraphicsEffect(self.effect)
        
        self.press_anim = QPropertyAnimation(self.effect, b"scale")
        self.press_anim.setDuration(120)
        self.press_anim.setEasingCurve(QEasingCurve.OutQuad)
        
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event: Any) -> None:
        if "pytest" not in sys.modules:
            self.press_anim.stop()
            self.press_anim.setStartValue(self.effect.get_scale())
            self.press_anim.setEndValue(0.97)
            self.press_anim.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:
        if "pytest" not in sys.modules:
            self.press_anim.stop()
            self.press_anim.setStartValue(self.effect.get_scale())
            self.press_anim.setEndValue(1.0)
            self.press_anim.start()
        super().mouseReleaseEvent(event)


# ── Circular Progress Ring ──────────────────────────────────────────────────
class CircularProgress(QWidget):
    def __init__(self, parent: Any = None, color: str = "#00a3cc", thickness: int = 8, min_size: int = 100, label: str = "", subtitle: str = "") -> None:
        super().__init__(parent)
        self.color_hex = color
        self.thickness = thickness
        self.value = 0.0
        self.target_value = 0.0
        self.label = label
        self.subtitle = subtitle
        self.setMinimumSize(min_size, min_size)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate_step)
        
    def set_value(self, val: float) -> None:
        self.target_value = float(val)
        if not self.timer.isActive():
            self.timer.start(16)
            
    def _animate_step(self) -> None:
        diff = self.target_value - self.value
        if abs(diff) < 0.5:
            self.value = self.target_value
            self.timer.stop()
        else:
            self.value += diff * 0.1
        self.update()
        
    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        from src.core.theme_manager import ThemeManager
        colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
        accent = QColor(self.color_hex)
        text_color = QColor(colors.get("TEXT", "#eae6f8"))
        muted_color = QColor(colors.get("MUTED", "#8e85a6"))
        
        width = self.width()
        height = self.height()
        size = min(width, height) - self.thickness * 2
        
        rect = QRectF(
            self.width() / 2 - size / 2,
            self.height() / 2 - size / 2,
            size,
            size
        )
        
        # Draw background track
        pen_track = QPen()
        pen_track.setColor(QColor(255, 255, 255, 12))
        pen_track.setWidth(self.thickness)
        pen_track.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_track)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Draw progress stroke
        pen_progress = QPen()
        pen_progress.setWidth(self.thickness)
        pen_progress.setCapStyle(Qt.RoundCap)
        
        angle = int(-self.value * 3.6 * 16)
        
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0, accent)
        grad.setColorAt(1, accent.lighter(135))
        
        pen_progress.setBrush(QBrush(grad))
        painter.setPen(pen_progress)
        painter.drawArc(rect, 90 * 16, angle)
        
        # Central value text
        painter.setPen(text_color)
        font = QFont("Inter", int(size * 0.18), QFont.Bold)
        painter.setFont(font)
        
        text_val = f"{int(self.value)}%" if not self.label else self.label
        painter.drawText(rect, Qt.AlignCenter, text_val)
        
        # Subtitle
        if self.subtitle:
            painter.setPen(muted_color)
            sub_font = QFont("Inter", int(size * 0.08))
            painter.setFont(sub_font)
            sub_rect = rect.translated(0, size * 0.22)
            painter.drawText(sub_rect, Qt.AlignCenter, self.subtitle)


# ── Radar Chart Widget ──────────────────────────────────────────────────────
class RadarChartWidget(QWidget):
    def __init__(self, parent: Any = None, categories: list[str] | None = None, series: list[dict[str, Any]] | None = None) -> None:
        super().__init__(parent)
        self.categories = categories or []
        self.series = series or []
        self.setMouseTracking(True)
        self.hovered_series_idx = -1
        self.hovered_point_idx = -1
        self._scale_factor = 0.0
        
        self.load_anim = QPropertyAnimation(self, b"scaleFactor")
        self.load_anim.setDuration(450)
        self.load_anim.setEasingCurve(QEasingCurve.OutQuad)
        
    def get_scale_factor(self) -> float:
        return self._scale_factor
        
    def set_scale_factor(self, val: float) -> None:
        self._scale_factor = val
        self.update()
        
    scaleFactor = Property(float, get_scale_factor, set_scale_factor)
        
    def set_data(self, categories: list[str], series: list[dict[str, Any]]) -> None:
        self.categories = categories
        self.series = series
        if "pytest" in sys.modules:
            self._scale_factor = 1.0
            self.update()
        else:
            self._scale_factor = 0.0
            self.load_anim.stop()
            self.load_anim.setStartValue(0.0)
            self.load_anim.setEndValue(1.0)
            self.load_anim.start()
        
    def mouseMoveEvent(self, event: Any) -> None:
        pos = event.position()
        center_x = self.width() / 2
        center_y = self.height() / 2
        max_radius = min(self.width(), self.height()) / 2 - 40
        N = len(self.categories)
        if N == 0 or not self.series:
            return
            
        found = False
        for s_idx, s in enumerate(self.series):
            vals = s["values"]
            for i in range(min(N, len(vals))):
                angle = -math.pi / 2 + i * (2 * math.pi / N)
                val = vals[i]
                r = max_radius * (val / 100.0) * self._scale_factor
                px = center_x + r * math.cos(angle)
                py = center_y + r * math.sin(angle)
                
                # Check distance to mouse
                dist = math.hypot(pos.x() - px, pos.y() - py)
                if dist < 8:
                    if self.hovered_series_idx != s_idx or self.hovered_point_idx != i:
                        self.hovered_series_idx = s_idx
                        self.hovered_point_idx = i
                        self.update()
                        
                        series_name = s.get("name", "Account")
                        QToolTip.showText(
                            event.globalPosition().toPoint(),
                            f"Series: {series_name}\nCategory: {self.categories[i]}\nValue: {val}%",
                            self
                        )
                    found = True
                    break
            if found:
                break
                
        if not found and self.hovered_series_idx != -1:
            self.hovered_series_idx = -1
            self.hovered_point_idx = -1
            self.update()
            QToolTip.hideText()
            
    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        from src.core.theme_manager import ThemeManager
        colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
        text_color = QColor(colors.get("TEXT", "#eae6f8"))
        muted_color = QColor(colors.get("MUTED", "#8e85a6"))
        grid_color = QColor(colors.get("SECONDARY", "#130f26")).lighter(140)
        
        N = len(self.categories)
        if N == 0:
            return
            
        center_x = self.width() / 2
        center_y = self.height() / 2
        max_radius = min(self.width(), self.height()) / 2 - 40
        
        # 1. Grid Rings
        pen_grid = QPen(grid_color)
        pen_grid.setStyle(Qt.DotLine)
        pen_grid.setWidth(1)
        painter.setPen(pen_grid)
        
        for r_val in [20, 40, 60, 80, 100]:
            r = max_radius * (r_val / 100.0)
            poly = QPolygonF()
            for i in range(N):
                angle = -math.pi / 2 + i * (2 * math.pi / N)
                x = center_x + r * math.cos(angle)
                y = center_y + r * math.sin(angle)
                poly.append(QPointF(x, y))
            painter.drawPolygon(poly)
            
            # draw grid value labels (e.g. 20, 40)
            painter.setPen(muted_color)
            painter.setFont(QFont("Inter", 8))
            painter.drawText(int(center_x - 14), int(center_y - r + 3), f"{r_val}")
            painter.setPen(pen_grid)
            
        # 2. Spokes and Outer Category Labels
        for i in range(N):
            angle = -math.pi / 2 + i * (2 * math.pi / N)
            x_outer = center_x + max_radius * math.cos(angle)
            y_outer = center_y + max_radius * math.sin(angle)
            painter.setPen(pen_grid)
            painter.drawLine(QPointF(center_x, center_y), QPointF(x_outer, y_outer))
            
            # Labels alignment
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            x_label = center_x + (max_radius + 18) * cos_a
            y_label = center_y + (max_radius + 18) * sin_a
            
            align = Qt.AlignCenter
            if cos_a > 0.1:
                align = Qt.AlignLeft | Qt.AlignVCenter
            elif cos_a < -0.1:
                align = Qt.AlignRight | Qt.AlignVCenter
            else:
                align = Qt.AlignHCenter | (Qt.AlignTop if sin_a > 0 else Qt.AlignBottom)
                
            painter.setPen(text_color)
            painter.setFont(QFont("Inter", 9, QFont.Bold))
            
            # Bounds rect
            rect_lbl = QRectF(x_label - 50, y_label - 10, 100, 20)
            painter.drawText(rect_lbl, align, self.categories[i])
            
        # 3. Series Polygons
        for s_idx, s in enumerate(self.series):
            vals = s["values"]
            color = QColor(s.get("color", "#00a3cc"))
            
            poly = QPolygonF()
            for i in range(N):
                angle = -math.pi / 2 + i * (2 * math.pi / N)
                val = vals[i] if i < len(vals) else 0.0
                r = max_radius * (val / 100.0) * self._scale_factor
                x = center_x + r * math.cos(angle)
                y = center_y + r * math.sin(angle)
                poly.append(QPointF(x, y))
                
            # Draw fill polygon
            brush_color = QColor(color)
            brush_color.setAlpha(40)
            painter.setBrush(QBrush(brush_color))
            painter.setPen(Qt.NoPen)
            painter.drawPolygon(poly)
            
            # Draw line loop
            painter.setBrush(Qt.NoBrush)
            pen_line = QPen(color)
            pen_line.setWidth(2)
            painter.setPen(pen_line)
            painter.drawPolygon(poly)
            
            # Draw vertices
            for i in range(N):
                angle = -math.pi / 2 + i * (2 * math.pi / N)
                val = vals[i] if i < len(vals) else 0.0
                r = max_radius * (val / 100.0) * self._scale_factor
                px = center_x + r * math.cos(angle)
                py = center_y + r * math.sin(angle)
                
                # Check if hovered
                if self.hovered_series_idx == s_idx and self.hovered_point_idx == i:
                    painter.setBrush(QBrush(QColor("#ffffff")))
                    painter.setPen(QPen(color, 2))
                    painter.drawEllipse(QPointF(px, py), 6, 6)
                else:
                    painter.setBrush(QBrush(color))
                    painter.setPen(QPen(QColor(255, 255, 255, 180), 1))
                    painter.drawEllipse(QPointF(px, py), 4, 4)


# ── Line Chart Widget ───────────────────────────────────────────────────────
class LineChartWidget(QWidget):
    def __init__(self, parent: Any = None, x_labels: list[str] | None = None, series: list[dict[str, Any]] | None = None) -> None:
        super().__init__(parent)
        self.x_labels = x_labels or []
        self.series = series or []
        self.setMouseTracking(True)
        self.hovered_series_idx = -1
        self.hovered_point_idx = -1
        self._scale_factor = 0.0
        
        self.load_anim = QPropertyAnimation(self, b"scaleFactor")
        self.load_anim.setDuration(450)
        self.load_anim.setEasingCurve(QEasingCurve.OutQuad)
        
    def get_scale_factor(self) -> float:
        return self._scale_factor
        
    def set_scale_factor(self, val: float) -> None:
        self._scale_factor = val
        self.update()
        
    scaleFactor = Property(float, get_scale_factor, set_scale_factor)
        
    def set_data(self, x_labels: list[str], series: list[dict[str, Any]]) -> None:
        self.x_labels = x_labels
        self.series = series
        if "pytest" in sys.modules:
            self._scale_factor = 1.0
            self.update()
        else:
            self._scale_factor = 0.0
            self.load_anim.stop()
            self.load_anim.setStartValue(0.0)
            self.load_anim.setEndValue(1.0)
            self.load_anim.start()
        
    def mouseMoveEvent(self, event: Any) -> None:
        pos = event.position()
        width = self.width() - 80
        height = self.height() - 80
        N = len(self.x_labels)
        if N == 0 or not self.series:
            return
            
        found = False
        for s_idx, s in enumerate(self.series):
            vals = s["values"]
            for i in range(min(N, len(vals))):
                val = vals[i]
                if val is None:
                    continue
                x = 50 + i * (width / (N - 1)) if N > 1 else 50 + width / 2
                y = height + 40 - (val / 100.0) * height * self._scale_factor
                
                dist = math.hypot(pos.x() - x, pos.y() - y)
                if dist < 8:
                    if self.hovered_series_idx != s_idx or self.hovered_point_idx != i:
                        self.hovered_series_idx = s_idx
                        self.hovered_point_idx = i
                        self.update()
                        
                        series_name = s.get("name", "Account")
                        QToolTip.showText(
                            event.globalPosition().toPoint(),
                            f"Series: {series_name}\nDate: {self.x_labels[i]}\nValue: {val}%",
                            self
                        )
                    found = True
                    break
            if found:
                break
                
        if not found and self.hovered_series_idx != -1:
            self.hovered_series_idx = -1
            self.hovered_point_idx = -1
            self.update()
            QToolTip.hideText()

    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        from src.core.theme_manager import ThemeManager
        colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
        text_color = QColor(colors.get("TEXT", "#eae6f8"))
        muted_color = QColor(colors.get("MUTED", "#8e85a6"))
        grid_color = QColor(colors.get("SECONDARY", "#130f26")).lighter(140)
        
        width = self.width() - 80
        height = self.height() - 80
        N = len(self.x_labels)
        if N == 0:
            return
            
        # Draw grid axes and background lines
        pen_grid = QPen(grid_color)
        pen_grid.setStyle(Qt.DotLine)
        painter.setPen(pen_grid)
        
        for val in [0, 25, 50, 75, 100]:
            y = height + 40 - (val / 100.0) * height
            painter.drawLine(QPointF(50, y), QPointF(width + 50, y))
            # Left Y labels
            painter.setPen(muted_color)
            painter.setFont(QFont("Inter", 8))
            painter.drawText(QRectF(15, y - 8, 30, 16), Qt.AlignRight | Qt.AlignVCenter, f"{val}")
            painter.setPen(pen_grid)
            
        # Draw X labels and ticks
        for i in range(N):
            x = 50 + i * (width / (N - 1)) if N > 1 else 50 + width / 2
            painter.drawLine(QPointF(x, 40), QPointF(x, height + 40))
            
            painter.setPen(muted_color)
            painter.setFont(QFont("Inter", 7))
            rect_lbl = QRectF(x - 30, height + 45, 60, 30)
            painter.drawText(rect_lbl, Qt.AlignHCenter | Qt.AlignTop, self.x_labels[i])
            painter.setPen(pen_grid)
            
        # Draw series lines and points
        for s_idx, s in enumerate(self.series):
            vals = s["values"]
            color = QColor(s.get("color", "#00a3cc"))
            
            pen_line = QPen(color)
            pen_line.setWidth(2.5)
            # Check projection style
            if s.get("projection"):
                pen_line.setStyle(Qt.DashLine)
            painter.setPen(pen_line)
            
            points = []
            for i in range(min(N, len(vals))):
                x = 50 + i * (width / (N - 1)) if N > 1 else 50 + width / 2
                val = vals[i]
                if val is None:
                    points.append(None)
                else:
                    y = height + 40 - (val / 100.0) * height * self._scale_factor
                    points.append(QPointF(x, y))
                
            # Draw segments
            for j in range(len(points) - 1):
                p1 = points[j]
                p2 = points[j+1]
                if p1 is not None and p2 is not None:
                    painter.drawLine(p1, p2)
                
            # Draw markers
            painter.setPen(Qt.NoPen)
            for i, p in enumerate(points):
                if p is None:
                    continue
                if self.hovered_series_idx == s_idx and self.hovered_point_idx == i:
                    painter.setBrush(QBrush(QColor("#ffffff")))
                    painter.setPen(QPen(color, 2))
                    painter.drawEllipse(p, 6, 6)
                else:
                    painter.setBrush(QBrush(color))
                    painter.setPen(QPen(QColor(255, 255, 255, 180), 1))
                    painter.drawEllipse(p, 4.5, 4.5)
                painter.setPen(Qt.NoPen)


# ── Pie Chart (Donut Chart) Widget ─────────────────────────────────────────
class PieChartWidget(QWidget):
    def __init__(self, parent: Any = None, labels: list[str] | None = None, values: list[float] | None = None, colors: list[str] | None = None) -> None:
        super().__init__(parent)
        self.labels = labels or []
        self.values = values or []
        self.color_hexes = colors or ["#22c55e", "#ef4444"]
        self.setMouseTracking(True)
        self.hover_slice_idx = -1
        self._scale_factor = 0.0
        
        self.load_anim = QPropertyAnimation(self, b"scaleFactor")
        self.load_anim.setDuration(450)
        self.load_anim.setEasingCurve(QEasingCurve.OutQuad)
        
    def get_scale_factor(self) -> float:
        return self._scale_factor
        
    def set_scale_factor(self, val: float) -> None:
        self._scale_factor = val
        self.update()
        
    scaleFactor = Property(float, get_scale_factor, set_scale_factor)
        
    def set_data(self, labels: list[str], values: list[float]) -> None:
        self.labels = labels
        self.values = values
        if "pytest" in sys.modules:
            self._scale_factor = 1.0
            self.update()
        else:
            self._scale_factor = 0.0
            self.load_anim.stop()
            self.load_anim.setStartValue(0.0)
            self.load_anim.setEndValue(1.0)
            self.load_anim.start()
        
    def mouseMoveEvent(self, event: Any) -> None:
        pos = event.position()
        center_x = self.width() / 2
        center_y = self.height() / 2
        size = min(self.width(), self.height()) - 50
        
        dx = pos.x() - center_x
        dy = pos.y() - center_y
        dist = math.hypot(dx, dy)
        
        # Donut active hover range
        inner_r = size / 4
        outer_r = size / 2
        
        if inner_r <= dist <= outer_r:
            angle = math.degrees(math.atan2(-dy, dx))
            if angle < 0:
                angle += 360
                
            total = sum(self.values)
            if total > 0:
                target_deg = (90 - angle) % 360
                curr_deg = 0.0
                matched_idx = -1
                for idx, val in enumerate(self.values):
                    span = (val / total) * 360 * self._scale_factor
                    if curr_deg <= target_deg <= curr_deg + span:
                        matched_idx = idx
                        break
                    curr_deg += span
                    
                if self.hover_slice_idx != matched_idx:
                    self.hover_slice_idx = matched_idx
                    self.update()
                    if matched_idx != -1:
                        QToolTip.showText(
                            event.globalPosition().toPoint(),
                            f"Category: {self.labels[matched_idx]}\nValue: {self.values[matched_idx]} items ({self.values[matched_idx]/total:.1%})",
                            self
                        )
                return
                
        if self.hover_slice_idx != -1:
            self.hover_slice_idx = -1
            self.update()
            QToolTip.hideText()
            
    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        from src.core.theme_manager import ThemeManager
        theme_colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
        text_color = QColor(theme_colors.get("TEXT", "#eae6f8"))
        muted_color = QColor(theme_colors.get("MUTED", "#8e85a6"))
        bg_color = QColor(theme_colors.get("PRIMARY", "#0b1220"))
        
        width = self.width()
        height = self.height()
        size = min(width, height) - 60
        
        rect = QRectF(width / 2 - size / 2, height / 2 - size / 2, size, size)
        
        total = sum(self.values)
        if total == 0:
            painter.setPen(muted_color)
            painter.setFont(QFont("Inter", 10))
            painter.drawText(self.rect(), Qt.AlignCenter, "No collection data available")
            return
            
        start_angle = 90 * 16 # Top position
        for idx, val in enumerate(self.values):
            color = QColor(self.color_hexes[idx % len(self.color_hexes)])
            span = int(-(val / total) * 360 * 16 * self._scale_factor) # clockwise
            
            # Hover explosion effect: translate slightly outward
            if idx == self.hover_slice_idx:
                painter.save()
                # calculate middle angle of slice
                mid_angle = math.radians(90 - (idx * (val/total) * 180 + (val/total)*180)) # rough approximation
                # translate slightly
                # painter.translate(5 * math.cos(mid_angle), -5 * math.sin(mid_angle)) # standard translation
                
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(bg_color, 1.5))
            painter.drawPie(rect, start_angle, span)
            
            if idx == self.hover_slice_idx:
                painter.restore()
                
            start_angle += span
            
        # Draw central circle to create a beautiful Donut Chart
        hole_size = size / 2.2
        hole_rect = QRectF(width / 2 - hole_size / 2, height / 2 - hole_size / 2, hole_size, hole_size)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(255, 255, 255, 10), 1))
        painter.drawEllipse(hole_rect)
        
        # Legend drawing
        painter.setPen(text_color)
        painter.setFont(QFont("Inter", 8, QFont.Bold))
        legend_y = int(height / 2 - (len(self.values) * 15) / 2)
        for idx, lbl in enumerate(self.labels):
            color = QColor(self.color_hexes[idx % len(self.color_hexes)])
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(width / 2 + size / 2 - 10), legend_y + idx * 18 + 2, 8, 8)
            
            painter.setPen(text_color)
            painter.setFont(QFont("Inter", 8))
            pct = self.values[idx] / total if total else 0
            painter.drawText(int(width / 2 + size / 2 + 5), legend_y + idx * 18 + 10, f"{lbl}: {self.values[idx]:.0f} ({pct:.0%})")


# ── Bar Chart Widget ────────────────────────────────────────────────────────
class BarChartWidget(QWidget):
    def __init__(self, parent: Any = None, x_labels: list[str] | None = None, values: list[float] | None = None, color: str = "#caa3ff") -> None:
        super().__init__(parent)
        self.x_labels = x_labels or []
        self.values = values or []
        self.color_hex = color
        self.setMouseTracking(True)
        self.hover_bar_idx = -1
        self._scale_factor = 0.0
        
        self.load_anim = QPropertyAnimation(self, b"scaleFactor")
        self.load_anim.setDuration(450)
        self.load_anim.setEasingCurve(QEasingCurve.OutQuad)
        
    def get_scale_factor(self) -> float:
        return self._scale_factor
        
    def set_scale_factor(self, val: float) -> None:
        self._scale_factor = val
        self.update()
        
    scaleFactor = Property(float, get_scale_factor, set_scale_factor)
        
    def set_data(self, x_labels: list[str], values: list[float]) -> None:
        self.x_labels = x_labels
        self.values = values
        if "pytest" in sys.modules:
            self._scale_factor = 1.0
            self.update()
        else:
            self._scale_factor = 0.0
            self.load_anim.stop()
            self.load_anim.setStartValue(0.0)
            self.load_anim.setEndValue(1.0)
            self.load_anim.start()
        
    def mouseMoveEvent(self, event: Any) -> None:
        pos = event.position()
        width = self.width() - 80
        height = self.height() - 80
        N = len(self.x_labels)
        if N == 0 or not self.values:
            return
            
        bar_w = (width / N) * 0.7
        spacing = (width / N) * 0.3
        max_val = max(self.values) if self.values else 100.0
        if max_val == 0:
            max_val = 100.0
            
        matched_idx = -1
        for i in range(N):
            x = 50 + i * (width / N) + spacing / 2
            val = self.values[i]
            bar_h = (val / max_val) * height * self._scale_factor
            y = height + 40 - bar_h
            
            rect = QRectF(x, y, bar_w, bar_h)
            if rect.contains(pos.x(), pos.y()):
                matched_idx = i
                break
                
        if self.hover_bar_idx != matched_idx:
            self.hover_bar_idx = matched_idx
            self.update()
            if matched_idx != -1:
                QToolTip.showText(
                    event.globalPosition().toPoint(),
                    f"Date: {self.x_labels[matched_idx]}\nValue: {self.values[matched_idx]:.0f} completions",
                    self
                )
        if matched_idx == -1 and self.hover_bar_idx != -1:
            self.hover_bar_idx = -1
            self.update()
            QToolTip.hideText()
            
    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        from src.core.theme_manager import ThemeManager
        colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
        text_color = QColor(colors.get("TEXT", "#eae6f8"))
        muted_color = QColor(colors.get("MUTED", "#8e85a6"))
        grid_color = QColor(colors.get("SECONDARY", "#130f26")).lighter(140)
        accent = QColor(self.color_hex)
        
        width = self.width() - 80
        height = self.height() - 80
        N = len(self.x_labels)
        if N == 0:
            return
            
        max_val = max(self.values) if self.values else 1.0
        if max_val == 0:
            max_val = 1.0
            
        # Draw background grid ticks
        pen_grid = QPen(grid_color)
        pen_grid.setStyle(Qt.DotLine)
        painter.setPen(pen_grid)
        
        # 4 grid lines
        grid_divisions = 4
        for step in range(grid_divisions + 1):
            val = (max_val / grid_divisions) * step
            y = height + 40 - (val / max_val) * height
            painter.drawLine(QPointF(50, y), QPointF(width + 50, y))
            
            # Label
            painter.setPen(muted_color)
            painter.setFont(QFont("Inter", 8))
            painter.drawText(QRectF(15, y - 8, 30, 16), Qt.AlignRight | Qt.AlignVCenter, f"{val:.0f}")
            painter.setPen(pen_grid)
            
        # Draw bars
        bar_w = (width / N) * 0.7
        spacing = (width / N) * 0.3
        
        for i in range(N):
            x = 50 + i * (width / N) + spacing / 2
            val = self.values[i]
            bar_h = (val / max_val) * height * self._scale_factor
            y = height + 40 - bar_h
            
            rect = QRectF(x, y, bar_w, bar_h)
            
            # Gradient color
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            if i == self.hover_bar_idx:
                grad.setColorAt(0, accent.lighter(130))
                grad.setColorAt(1, accent)
            else:
                grad.setColorAt(0, accent)
                grad.setColorAt(1, accent.darker(130))
                
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(rect, 4, 4)
            
            # Label on X axis
            painter.setPen(muted_color)
            painter.setFont(QFont("Inter", 7))
            rect_lbl = QRectF(x - 10, height + 45, bar_w + 20, 30)
            painter.drawText(rect_lbl, Qt.AlignHCenter | Qt.AlignTop, self.x_labels[i])


class HoverAnimatedCard(QGroupBox):
    """Custom QGroupBox card wrapper with layout-safe hover translate lifting and opacity animations."""

    def __init__(self, title: str = "", parent: Any = None) -> None:
        super().__init__(title, parent)
        self.effect = FadeTranslateScaleEffect(self)
        self.setGraphicsEffect(self.effect)
        
        self.hover_anim = QPropertyAnimation(self.effect, b"yOffset")
        self.hover_anim.setDuration(150)
        self.hover_anim.setEasingCurve(QEasingCurve.OutQuad)

    def enterEvent(self, event: Any) -> None:
        if "pytest" not in sys.modules:
            self.hover_anim.stop()
            self.hover_anim.setStartValue(self.effect.get_y_offset())
            self.hover_anim.setEndValue(-4.0)
            self.hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event: Any) -> None:
        if "pytest" not in sys.modules:
            self.hover_anim.stop()
            self.hover_anim.setStartValue(self.effect.get_y_offset())
            self.hover_anim.setEndValue(0.0)
            self.hover_anim.start()
        super().leaveEvent(event)
