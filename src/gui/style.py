from pathlib import Path

# Centralized dark theme stylesheet for the application.

PRIMARY = "#0b1220"
SECONDARY = "#0f1724"
ACCENT = "#00a3cc"
TEXT = "#e6eef6"
MUTED = "#9fb6c8"
CARD = "#0f1a24"
POSITIVE = "#22c55e"
NEGATIVE = "#ef4444"

SHEET = f"""
QWidget {{
  background: {PRIMARY};
  color: {TEXT};
  font-family: Segoe UI, Roboto, Arial;
  font-size: 12px;
}}

QMainWindow::separator {{ background: {SECONDARY}; }}

QTabWidget::pane {{
  border: none;
}}

QTabBar::tab {{
  background: {SECONDARY};
  padding: 8px 12px;
  margin: 2px;
  border-radius: 4px;
}}

QTabBar::tab:selected {{
  background: {CARD};
  color: {TEXT};
}}

QPushButton {{
  background: {CARD};
  border: 1px solid rgba(255,255,255,0.06);
  padding: 6px 10px;
  border-radius: 4px;
}}

QPushButton:hover {{ background: rgba(255,255,255,0.03); }}

QLineEdit, QComboBox, QTextEdit {{
  background: {SECONDARY};
  border: 1px solid rgba(255,255,255,0.04);
  padding: 6px;
  border-radius: 4px;
}}

QListWidget {{
  background: transparent;
  border: 1px solid rgba(255,255,255,0.03);
}}

QProgressBar {{
  background: rgba(255,255,255,0.03);
  border-radius: 6px;
  text-align: center;
}}

QProgressBar::chunk {{
  background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT}, stop:1 #60d7ff);
  border-radius: 6px;
}}

QGroupBox {{
  border: 1px solid rgba(255,255,255,0.03);
  margin-top: 6px;
  padding: 8px;
  border-radius: 6px;
}}

QLabel#heroTitle {{
  font-size: 20px;
  font-weight: 700;
  color: {ACCENT};
}}

/* Scrollbar */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background: rgba(255,255,255,0.06);
    min-height: 20px;
    border-radius: 5px;
}}

/* Recommendation color badges */
QListWidget::item[recCategory="STORY"] {{ color: #7fb3ff; }}
QListWidget::item[recCategory="MOD"] {{ color: #7fffb3; }}
QListWidget::item[recCategory="ARCANE"] {{ color: #caa3ff; }}
QListWidget::item[recCategory="WEAPON"] {{ color: #ffb76b; }}
QListWidget::item[recCategory="ENDGAME"] {{ color: #ff7b7b; }}
QListWidget::item[recCategory="PROGRESSION"] {{ color: #6fffe8; }}

"""
