from __future__ import annotations

TEMPLATE = """
QWidget {{
  background: {PRIMARY};
  color: {TEXT};
  font-family: Segoe UI, Roboto, Arial;
  font-size: 12px;
}}

QMainWindow::separator {{ background: {SECONDARY}; }}

QTabWidget::pane {{ border: none; }}

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
  color: {TEXT};
}}

QPushButton:hover {{ background: rgba(255,255,255,0.03); }}

QLineEdit, QComboBox, QTextEdit {{
  background: {SECONDARY};
  color: {TEXT};
  border: 1px solid rgba(255,255,255,0.04);
  padding: 6px;
  border-radius: 4px;
}}

QListWidget {{
  background: transparent;
  border: 1px solid rgba(255,255,255,0.03);
  color: {TEXT};
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
"""

class ThemeEngine:
    """Compiles template stylesheet parameters into PySide6 stylesheets."""

    def compile_stylesheet(self, theme_data: dict[str, str]) -> str:
        """Substitute theme colors into structural template CSS."""
        return TEMPLATE.format(
            PRIMARY=theme_data.get("PRIMARY", "#0b1220"),
            SECONDARY=theme_data.get("SECONDARY", "#0f1724"),
            ACCENT=theme_data.get("ACCENT", "#00a3cc"),
            TEXT=theme_data.get("TEXT", "#e6eef6"),
            MUTED=theme_data.get("MUTED", "#9fb6c8"),
            CARD=theme_data.get("CARD", "#0f1a24")
        )
