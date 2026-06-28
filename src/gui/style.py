from pathlib import Path

PRIMARY = "#0c0919"
SECONDARY = "#130f26"
ACCENT = "#bb86fc"
TEXT = "#eae6f8"
MUTED = "#8e85a6"
CARD = "#1f183a"
POSITIVE = "#a855f7"
NEGATIVE = "#ff5555"

SHEET = f"""
/* Global Widget Styles */
QWidget {{
  background-color: {PRIMARY};
  color: {TEXT};
  font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", "Helvetica Neue", Arial, sans-serif;
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
  border-radius: 4px;
  padding: 4px;
}}

/* Tab Bar Overhaul */
QTabWidget::pane {{
  border: 1px solid rgba(255, 255, 255, 0.05);
  background-color: {PRIMARY};
  border-radius: 6px;
}}

QTabWidget::tab-bar {{
  alignment: left;
}}

QTabBar::tab {{
  background-color: {SECONDARY};
  color: {MUTED};
  padding: 8px 16px;
  margin-right: 4px;
  margin-bottom: 2px;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.03);
  font-weight: 500;
}}

QTabBar::tab:hover {{
  background-color: {CARD};
  color: {TEXT};
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
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 6px 14px;
  border-radius: 4px;
  color: {TEXT};
  font-weight: 600;
}}

QPushButton:hover {{
  background-color: rgba(255, 255, 255, 0.05);
  border-color: {ACCENT};
}}

QPushButton:pressed {{
  background-color: rgba(255, 255, 255, 0.02);
}}

QPushButton:disabled {{
  background-color: rgba(255, 255, 255, 0.01);
  color: {MUTED};
  border-color: transparent;
}}

/* Inputs & Form Fields */
QLineEdit, QComboBox, QTextEdit, QPlainTextEdit, QSpinBox {{
  background-color: {SECONDARY};
  color: {TEXT};
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 6px 10px;
  border-radius: 4px;
}}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus {{
  border: 1px solid {ACCENT};
}}

QComboBox::drop-down {{
  subcontrol-origin: padding;
  subcontrol-position: top right;
  width: 20px;
  border-left: none;
}}

/* Table Views */
QTableView, QTableWidget {{
  background-color: {SECONDARY};
  alternate-background-color: rgba(255, 255, 255, 0.01);
  gridline-color: rgba(255, 255, 255, 0.04);
  color: {TEXT};
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}}

QHeaderView::section {{
  background-color: {CARD};
  color: {ACCENT};
  padding: 6px;
  border: none;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}}

QTableWidget::item:hover, QTableView::item:hover {{
  background-color: rgba(255, 255, 255, 0.03);
}}

QTableWidget::item:selected, QTableView::item:selected {{
  background-color: {ACCENT};
  color: {PRIMARY};
}}

/* Lists */
QListWidget {{
  background-color: {SECONDARY};
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  padding: 4px;
}}

QListWidget::item {{
  padding: 6px 10px;
  border-radius: 2px;
}}

QListWidget::item:hover {{
  background-color: rgba(255, 255, 255, 0.03);
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
  border-radius: 4px;
  text-align: center;
  font-weight: bold;
}}

QProgressBar::chunk {{
  background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT}, stop:1 {MUTED});
  border-radius: 3px;
}}


/* Group Boxes (Clean Card Layout) */
QGroupBox {{
  border: 1px solid rgba(255, 255, 255, 0.05);
  background-color: {SECONDARY};
  margin-top: 10px;
  padding: 12px;
  border-radius: 6px;
  font-weight: bold;
}}

QGroupBox::title {{
  subcontrol-origin: margin;
  subcontrol-position: top left;
  left: 10px;
  padding: 0 4px;
  color: {ACCENT};
}}

/* Scrollbars */
QScrollBar:vertical {{
  background-color: transparent;
  width: 8px;
  margin: 0;
}}

QScrollBar::handle:vertical {{
  background-color: rgba(255, 255, 255, 0.1);
  min-height: 20px;
  border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
  background-color: {ACCENT};
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
  background-color: rgba(255, 255, 255, 0.1);
  min-width: 20px;
  border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
  background-color: {ACCENT};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
  border: none;
  background: none;
}}

/* Hero Title Label */
QLabel#heroTitle {{
  font-size: 20px;
  font-weight: 700;
  color: {ACCENT};
}}

/* Status Indicators Badge Category */
QListWidget::item[recCategory="STORY"] {{ color: #7fb3ff; }}
QListWidget::item[recCategory="MOD"] {{ color: #7fffb3; }}
QListWidget::item[recCategory="ARCANE"] {{ color: #caa3ff; }}
QListWidget::item[recCategory="WEAPON"] {{ color: #ffb76b; }}
QListWidget::item[recCategory="ENDGAME"] {{ color: #ff7b7b; }}
QListWidget::item[recCategory="PROGRESSION"] {{ color: #6fffe8; }}
"""
