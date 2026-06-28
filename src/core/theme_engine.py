from __future__ import annotations

TEMPLATE = """
/* Global Widget Styles */
QWidget {{
  background-color: {PRIMARY};
  color: {TEXT};
  font-family: {FONT_FAMILY};
  font-size: 12px;
}}

QMainWindow::separator {{
  background: {SECONDARY};
  width: 1px;
  height: 1px;
}}

/* Tooltips */
QToolTip {{
  background-color: {SECONDARY};
  color: {TEXT};
  border: 1px solid {ACCENT};
  border-radius: {BORDER_RADIUS_WIDGET};
  padding: 6px;
}}

/* Tab Bar Overhaul */
QTabWidget::pane {{
  border: {BORDER_STYLE_CARD};
  background-color: {PRIMARY};
  border-radius: {BORDER_RADIUS_CARD};
}}

QTabWidget::tab-bar {{
  alignment: left;
}}

QTabBar::tab {{
  background-color: {SECONDARY};
  color: {MUTED};
  padding: 10px 20px;
  margin-right: 6px;
  margin-bottom: 4px;
  border-top-left-radius: {BORDER_RADIUS_TAB};
  border-top-right-radius: {BORDER_RADIUS_TAB};
  border: 1px solid rgba(255, 255, 255, 0.03);
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
}}

QTabBar::tab:hover {{
  background-color: {CARD};
  color: {TEXT};
  border-color: rgba(255, 255, 255, 0.1);
}}

QTabBar::tab:selected {{
  background-color: {PRIMARY};
  color: {ACCENT};
  border-bottom: 2px solid {ACCENT};
  font-weight: bold;
}}

/* Buttons */
QPushButton {{
  background-color: {CARD};
  border: {BORDER_STYLE_BUTTON};
  padding: 8px 16px;
  border-radius: {BORDER_RADIUS_WIDGET};
  color: {TEXT};
  font-weight: bold;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}

QPushButton:hover {{
  background-color: {BUTTON_HOVER_BG};
  border-color: {ACCENT};
  color: #ffffff;
}}

QPushButton:pressed {{
  background-color: rgba(188, 163, 255, 0.05);
}}

QPushButton:disabled {{
  background-color: rgba(255, 255, 255, 0.02);
  color: {MUTED};
  border-color: transparent;
}}

/* Inputs & Form Fields */
QLineEdit, QComboBox, QTextEdit, QPlainTextEdit, QSpinBox {{
  background-color: {SECONDARY};
  color: {TEXT};
  border: {WIDGET_BORDER};
  padding: 8px 12px;
  border-radius: {BORDER_RADIUS_WIDGET};
  selection-background-color: {ACCENT};
  selection-color: {PRIMARY};
}}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus {{
  border: 1px solid {ACCENT};
  background-color: {CARD};
}}

QComboBox::drop-down {{
  subcontrol-origin: padding;
  subcontrol-position: top right;
  width: 24px;
  border-left: none;
}}

/* Table Views */
QTableView, QTableWidget {{
  background-color: {SECONDARY};
  alternate-background-color: rgba(255, 255, 255, 0.01);
  gridline-color: rgba(255, 255, 255, 0.04);
  color: {TEXT};
  border: {BORDER_STYLE_CARD};
  border-radius: {BORDER_RADIUS_CARD};
  selection-background-color: {ACCENT};
  selection-color: {PRIMARY};
}}

QHeaderView::section {{
  background-color: {CARD};
  color: {ACCENT};
  padding: 8px;
  border: none;
  font-weight: bold;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}}

QTableWidget::item:hover, QTableView::item:hover {{
  background-color: rgba(255, 255, 255, 0.03);
}}

QTableWidget::item:selected, QTableView::item:selected {{
  background-color: {ACCENT};
  color: {PRIMARY};
  font-weight: bold;
}}

/* Lists */
QListWidget {{
  background-color: {SECONDARY};
  border: {BORDER_STYLE_CARD};
  border-radius: {BORDER_RADIUS_CARD};
  padding: 8px;
}}

QListWidget::item {{
  padding: 10px 14px;
  border-radius: {BORDER_RADIUS_WIDGET};
  margin-bottom: 2px;
  color: {MUTED};
  font-weight: 500;
}}

QListWidget::item:hover {{
  background-color: rgba(255, 255, 255, 0.03);
  color: {TEXT};
}}

QListWidget::item:selected {{
  background-color: {ACCENT};
  color: {PRIMARY};
  font-weight: bold;
}}

/* Progress Bars */
QProgressBar {{
  background-color: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: {BORDER_RADIUS_WIDGET};
  text-align: center;
  font-weight: bold;
  color: {TEXT};
}}

QProgressBar::chunk {{
  background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT}, stop:1 {MUTED});
  border-radius: {BORDER_RADIUS_WIDGET};
}}

/* Group Boxes (Clean Card Layout) */
QGroupBox {{
  border: {BORDER_STYLE_CARD};
  background-color: {CARD};
  margin-top: 14px;
  padding: {PADDING_CARD};
  border-radius: {BORDER_RADIUS_CARD};
  font-weight: bold;
  font-size: 13px;
}}

QGroupBox::title {{
  subcontrol-origin: margin;
  subcontrol-position: top left;
  left: 14px;
  padding: 0 6px;
  color: {ACCENT};
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}

/* Scrollbars */
QScrollBar:vertical {{
  background-color: transparent;
  width: 8px;
  margin: 0;
}}

QScrollBar::handle:vertical {{
  background-color: rgba(255, 255, 255, 0.08);
  min-height: 24px;
  border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
  background-color: {SCROLLBAR_ACCENT};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
  border: none;
  background: none;
}}

QScrollBar:horizontal {{
  background-color: transparent;
  height: 8px;
  margin: 0;
}}

QScrollBar::handle:horizontal {{
  background-color: rgba(255, 255, 255, 0.08);
  min-width: 24px;
  border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
  background-color: {SCROLLBAR_ACCENT};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
  border: none;
  background: none;
}}

/* Status Indicators Badge Category */
QListWidget::item[recCategory="STORY"] {{ color: #7fb3ff; }}
QListWidget::item[recCategory="MOD"] {{ color: #7fffb3; }}
QListWidget::item[recCategory="ARCANE"] {{ color: #caa3ff; }}
QListWidget::item[recCategory="WEAPON"] {{ color: #ffb76b; }}
QListWidget::item[recCategory="ENDGAME"] {{ color: #ff7b7b; }}
QListWidget::item[recCategory="PROGRESSION"] {{ color: #6fffe8; }}

/* Sidebar Nav Styles */
QTreeWidget#sidebarNav {{
  border: none;
  background-color: {SECONDARY};
  padding: 10px 4px;
}}

QTreeWidget#sidebarNav::item {{
  padding: 8px 10px;
  margin-bottom: 2px;
  border-radius: {BORDER_RADIUS_WIDGET};
  color: {MUTED};
  font-weight: 500;
}}

QTreeWidget#sidebarNav::item:hover {{
  background-color: rgba(255, 255, 255, 0.03);
  color: {TEXT};
}}

QTreeWidget#sidebarNav::item:selected {{
  background-color: {ACCENT};
  color: {PRIMARY};
  font-weight: bold;
}}
"""


class ThemeEngine:
    """Compiles template stylesheet parameters into PySide6 stylesheets."""

    def compile_stylesheet(self, theme_data: dict[str, str]) -> str:
        """Substitute theme colors and design tokens into structural template CSS."""
        font_family = theme_data.get("FONT_FAMILY", '"Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", Arial, sans-serif')
        border_radius_card = theme_data.get("BORDER_RADIUS_CARD", "8px")
        border_radius_widget = theme_data.get("BORDER_RADIUS_WIDGET", "6px")
        border_radius_tab = theme_data.get("BORDER_RADIUS_TAB", "6px")
        border_style_card = theme_data.get("BORDER_STYLE_CARD", "1px solid rgba(255, 255, 255, 0.05)")
        border_style_button = theme_data.get("BORDER_STYLE_BUTTON", "1px solid rgba(188, 163, 255, 0.15)")
        padding_card = theme_data.get("PADDING_CARD", "16px")
        button_hover_bg = theme_data.get("BUTTON_HOVER_BG", "rgba(188, 163, 255, 0.1)")
        widget_border = theme_data.get("WIDGET_BORDER", "1px solid rgba(255, 255, 255, 0.08)")
        scrollbar_accent = theme_data.get("ACCENT", "#00a3cc")

        return TEMPLATE.format(
            PRIMARY=theme_data.get("PRIMARY", "#0b1220"),
            SECONDARY=theme_data.get("SECONDARY", "#0f1724"),
            ACCENT=theme_data.get("ACCENT", "#00a3cc"),
            TEXT=theme_data.get("TEXT", "#e6eef6"),
            MUTED=theme_data.get("MUTED", "#9fb6c8"),
            CARD=theme_data.get("CARD", "#0f1a24"),
            FONT_FAMILY=font_family,
            BORDER_RADIUS_CARD=border_radius_card,
            BORDER_RADIUS_WIDGET=border_radius_widget,
            BORDER_RADIUS_TAB=border_radius_tab,
            BORDER_STYLE_CARD=border_style_card,
            BORDER_STYLE_BUTTON=border_style_button,
            PADDING_CARD=padding_card,
            BUTTON_HOVER_BG=button_hover_bg,
            WIDGET_BORDER=widget_border,
            SCROLLBAR_ACCENT=scrollbar_accent
        )

