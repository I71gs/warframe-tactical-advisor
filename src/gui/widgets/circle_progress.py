import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QPointF
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

    _theme_cache = None
    _colors_cache = None

    @classmethod
    def get_cached_theme_colors(cls) -> tuple[str, dict[str, str]]:
        from src.core.theme_manager import ThemeManager
        try:
            tm = ThemeManager()
            active = tm.get_active_theme_name()
            # To avoid reloading on every paint, cache colors
            if cls._theme_cache != active or cls._colors_cache is None:
                cls._theme_cache = active
                cls._colors_cache = tm.get_theme_colors(active)
            return active, cls._colors_cache
        except Exception:
            return "Dark", {
                "PRIMARY": "#0b1220",
                "SECONDARY": "#0f1724",
                "ACCENT": "#00a3cc",
                "TEXT": "#e6eef6",
                "MUTED": "#9fb6c8",
                "CARD": "#0f1a24"
            }

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        theme_name, colors = self.get_cached_theme_colors()
        
        # Pull styling overrides from theme details
        accent_color = QColor(colors.get("ACCENT", "#bb86fc"))
        muted_color = QColor(colors.get("MUTED", "#8e85a6"))
        text_color = QColor(colors.get("TEXT", "#eae6f8"))
        font_family = colors.get("FONT_FAMILY", '"Segoe UI", -apple-system, sans-serif')
        # Clean up font family string for QFont instantiation
        font_family_clean = font_family.split(",")[0].replace('"', '').replace("'", "").strip()

        w = float(self.width())
        h = float(self.height())
        cx = w / 2.0
        cy = h / 2.0
        r = min(w, h) - self.pen_width * 2.0
        rect = QRectF(self.pen_width, self.pen_width, r, r)

        pct = max(0.0, min(1.0, self.value / self.max_value))

        if theme_name == "Corpus":
            # Holographic digital tick segmented scanner
            num_ticks = 16
            tick_length = 6.0
            outer_radius = r / 2.0
            
            # Draw ticks
            for i in range(num_ticks):
                # Start at top (i=0 -> -90 deg)
                angle = (i * (360.0 / num_ticks)) - 90.0
                rad = math.radians(angle)
                
                # Active tick or track tick color
                tick_pct = i / num_ticks
                if tick_pct <= pct and pct > 0:
                    pen = QPen(accent_color, 2.0)
                else:
                    pen = QPen(self.track_color, 1.5)
                painter.setPen(pen)
                
                x1 = cx + (outer_radius - tick_length) * math.cos(rad)
                y1 = cy + (outer_radius - tick_length) * math.sin(rad)
                x2 = cx + outer_radius * math.cos(rad)
                y2 = cy + outer_radius * math.sin(rad)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
                
            # Draw outer crosshair ticks at 0, 90, 180, 270 deg
            cross_pen = QPen(accent_color, 1.0)
            painter.setPen(cross_pen)
            cross_r = outer_radius + 4.0
            for angle in [0, 90, 180, 270]:
                rad = math.radians(angle)
                x1 = cx + (cross_r - 2.0) * math.cos(rad)
                y1 = cy + (cross_r - 2.0) * math.sin(rad)
                x2 = cx + cross_r * math.cos(rad)
                y2 = cy + cross_r * math.sin(rad)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        elif theme_name == "Orokin":
            # Gold Concentric Octagons & sharp geometric sectors
            # Draw background octagon track
            oct_pen_track = QPen(self.track_color, 1.0)
            painter.setPen(oct_pen_track)
            
            # Compute octagon points
            num_sides = 8
            oct_radius = r / 2.0
            points = []
            for i in range(num_sides + 1):
                angle = (i * (360.0 / num_sides)) - 90.0
                rad = math.radians(angle)
                points.append(QPointF(cx + oct_radius * math.cos(rad), cy + oct_radius * math.sin(rad)))
            
            for i in range(num_sides):
                painter.drawLine(points[i], points[i+1])
                
            # Draw progress segments
            if pct > 0:
                oct_pen_prog = QPen(accent_color, 2.5)
                painter.setPen(oct_pen_prog)
                active_sides = int(pct * num_sides)
                remainder = (pct * num_sides) - active_sides
                
                # Draw full active sides
                for i in range(active_sides):
                    painter.drawLine(points[i], points[i+1])
                # Draw partial side
                if remainder > 0 and active_sides < num_sides:
                    p_start = points[active_sides]
                    p_end = points[active_sides + 1]
                    p_mid = p_start + (p_end - p_start) * remainder
                    painter.drawLine(p_start, p_mid)

            # Draw concentric double outer circle thin border
            gold_pen = QPen(accent_color, 0.5)
            painter.setPen(gold_pen)
            painter.drawEllipse(QRectF(cx - oct_radius - 3, cy - oct_radius - 3, r + 6, r + 6))

        elif theme_name == "Lotus":
            # Soft organic curves with glowing shadow behind it
            # Glow track
            glow_pen = QPen(QColor(accent_color.red(), accent_color.green(), accent_color.blue(), 30))
            glow_pen.setWidthF(self.pen_width + 4.0)
            glow_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(glow_pen)
            painter.drawArc(rect, 0, 360 * 16)

            # Actual track
            track_pen = QPen(self.track_color)
            track_pen.setWidthF(self.pen_width)
            track_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(track_pen)
            painter.drawArc(rect, 0, 360 * 16)

            # Progress
            if pct > 0:
                span_angle = int(-pct * 360 * 16)
                prog_pen = QPen(accent_color)
                prog_pen.setWidthF(self.pen_width)
                prog_pen.setCapStyle(Qt.RoundCap)
                painter.setPen(prog_pen)
                painter.drawArc(rect, 90 * 16, span_angle)

        elif theme_name == "Grineer":
            # Chunky, heavy block segmented progress
            num_blocks = 8
            block_gap = 4.0  # degrees
            block_width = (360.0 / num_blocks) - block_gap
            
            for i in range(num_blocks):
                # Start at top
                angle = (i * (360.0 / num_blocks)) - 90.0
                
                # Active or track colors
                block_pct = (i + 1) / num_blocks
                if block_pct <= pct:
                    pen = QPen(accent_color, self.pen_width + 2.0)
                else:
                    pen = QPen(self.track_color, self.pen_width)
                pen.setCapStyle(Qt.FlatCap)
                painter.setPen(pen)
                painter.drawArc(rect, int(angle * 16), int(block_width * 16))

        elif theme_name == "Zariman":
            # Ethereal dashed arc
            track_pen = QPen(self.track_color, self.pen_width - 1.0)
            track_pen.setDashPattern([4, 4])
            painter.setPen(track_pen)
            painter.drawArc(rect, 0, 360 * 16)

            if pct > 0:
                span_angle = int(-pct * 360 * 16)
                prog_pen = QPen(accent_color, self.pen_width + 1.0)
                prog_pen.setDashPattern([8, 4])
                painter.setPen(prog_pen)
                painter.drawArc(rect, 90 * 16, span_angle)

        else:
            # Cosmic Twilight and Standard defaults: smooth arc with round caps
            track_pen = QPen(self.track_color)
            track_pen.setWidthF(self.pen_width)
            track_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(track_pen)
            painter.drawArc(rect, 0, 360 * 16)

            if pct > 0:
                span_angle = int(-pct * 360 * 16)
                prog_pen = QPen(accent_color)
                prog_pen.setWidthF(self.pen_width)
                prog_pen.setCapStyle(Qt.RoundCap)
                painter.setPen(prog_pen)
                painter.drawArc(rect, 90 * 16, span_angle)

        # Draw center text (large bold value)
        val_rect = self.rect()
        if self.label:
            val_rect.adjust(0, 0, 0, -12)

        font = QFont(font_family_clean, 11)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(text_color)
        txt = f"{int(self.value)}%"
        painter.drawText(val_rect, Qt.AlignCenter, txt)

        # Draw uppercase diagnostic sub-label
        if self.label:
            lbl_rect = self.rect()
            lbl_rect.adjust(0, 16, 0, 0)
            lbl_font = QFont(font_family_clean, 7)
            lbl_font.setBold(True)
            painter.setFont(lbl_font)
            painter.setPen(muted_color)
            painter.drawText(lbl_rect, Qt.AlignCenter, self.label.upper())

        painter.end()

