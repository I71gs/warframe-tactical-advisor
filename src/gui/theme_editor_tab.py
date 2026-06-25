from __future__ import annotations
import json
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QComboBox, QMessageBox, QFrame
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from src.core.theme_manager import ThemeManager
from src.core.theme_engine import ThemeEngine

ROOT = Path(__file__).resolve().parents[2]
CUSTOM_THEMES_DIR = ROOT / "themes" / "custom"
CUSTOM_THEMES_DIR.mkdir(parents=True, exist_ok=True)

class ThemeEditorTab(QWidget):
    """GUI tab providing a visual live theme preview studio and color customizer."""

    def __init__(self, main_window=None) -> None:
        super().__init__()
        self.main_window = main_window
        self.tm = ThemeManager()
        self.te = ThemeEngine()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Left Panel: Color Editors
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.header = QLabel("Theme Studio")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc; margin-bottom: 5px;")
        left_layout.addWidget(self.header)

        # Preset Loader
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Load Template:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(self.tm.get_themes())
        self.preset_combo.currentTextChanged.connect(self.load_preset_theme)
        preset_layout.addWidget(self.preset_combo)
        left_layout.addLayout(preset_layout)

        # Form Group
        form_group = QGroupBox("Color Definitions")
        form_layout = QVBoxLayout(form_group)

        form_layout.addWidget(QLabel("Custom Theme Name:"))
        self.name_input = QLineEdit("My Custom Theme")
        form_layout.addWidget(self.name_input)

        # Color fields
        self.color_inputs = {}
        self.color_swatches = {}
        for key in ["PRIMARY", "SECONDARY", "ACCENT", "TEXT", "MUTED", "CARD"]:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{key}:"))
            
            val_input = QLineEdit()
            val_input.setPlaceholderText("#hexcolor")
            val_input.textChanged.connect(self.update_live_preview)
            row.addWidget(val_input)
            self.color_inputs[key] = val_input

            # Color swatch indicator
            swatch = QLabel("   ")
            swatch.setFixedWidth(30)
            swatch.setStyleSheet("background-color: #000000; border: 1px solid #ffffff;")
            row.addWidget(swatch)
            self.color_swatches[key] = swatch

            form_layout.addLayout(row)

        left_layout.addWidget(form_group)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Export Theme")
        self.save_btn.clicked.connect(self.export_custom_theme)
        btn_layout.addWidget(self.save_btn)

        self.apply_btn = QPushButton("Apply Live")
        self.apply_btn.setStyleSheet("background-color: #22c55e; color: white; font-weight: bold;")
        self.apply_btn.clicked.connect(self.apply_theme_live)
        btn_layout.addWidget(self.apply_btn)
        
        left_layout.addLayout(btn_layout)
        left_widget.setLayout(left_layout)
        self.layout.addWidget(left_widget, 1)

        # Right Panel: Live Preview Card
        self.preview_box = QGroupBox("Interactive Live Preview")
        self.preview_layout = QVBoxLayout(self.preview_box)
        
        self.preview_card = QFrame()
        self.preview_card_layout = QVBoxLayout(self.preview_card)
        self.preview_card.setMinimumHeight(250)

        # Demo widgets
        self.demo_header = QLabel("Primary Header (Accent)")
        self.demo_body = QLabel("This is some sample text showing body colors. Muted text description appears below.")
        self.demo_muted = QLabel("Muted status context or timestamp info goes here.")
        
        self.preview_card_layout.addWidget(self.demo_header)
        self.preview_card_layout.addWidget(self.demo_body)
        self.preview_card_layout.addWidget(self.demo_muted)
        self.preview_card.setLayout(self.preview_card_layout)
        
        self.preview_layout.addWidget(self.preview_card)
        self.preview_box.setLayout(self.preview_layout)
        self.layout.addWidget(self.preview_box, 1)

        self.setLayout(self.layout)
        
        # Load active theme colors initially
        active_theme = self.tm.get_active_theme_name()
        self.preset_combo.setCurrentText(active_theme)
        self.load_preset_theme(active_theme)

    def load_preset_theme(self, theme_name: str) -> None:
        if not theme_name:
            return
        colors = self.tm.get_theme_colors(theme_name)
        self.name_input.setText(f"{theme_name} Edited")
        for key, input_widget in self.color_inputs.items():
            if key in colors:
                input_widget.setText(colors[key])

        self.update_live_preview()

    def get_editor_colors(self) -> dict[str, str]:
        colors = {
            "name": self.name_input.text().strip()
        }
        for key, val_input in self.color_inputs.items():
            colors[key] = val_input.text().strip()
        return colors

    def update_live_preview(self) -> None:
        colors = self.get_editor_colors()
        
        # Update swatches
        for key, val in colors.items():
            if key in self.color_swatches:
                try:
                    self.color_swatches[key].setStyleSheet(f"background-color: {val}; border: 1px solid #ffffff;")
                except Exception:
                    pass

        # Update preview card stylesheet
        card_bg = colors.get("CARD", "#0f1a24")
        text_color = colors.get("TEXT", "#e6eef6")
        accent_color = colors.get("ACCENT", "#00a3cc")
        muted_color = colors.get("MUTED", "#9fb6c8")

        self.preview_card.setStyleSheet(f"""
            QFrame {{
                background-color: {card_bg};
                border: 1px solid {accent_color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        self.demo_header.setStyleSheet(f"color: {accent_color}; font-size: 16px; font-weight: bold; background: transparent;")
        self.demo_body.setStyleSheet(f"color: {text_color}; font-size: 12px; background: transparent;")
        self.demo_muted.setStyleSheet(f"color: {muted_color}; font-size: 10px; background: transparent;")

    def export_custom_theme(self) -> None:
        colors = self.get_editor_colors()
        name = colors["name"]
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a theme name.")
            return

        safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_")).strip()
        filename = f"{safe_name.lower()}.json"
        dest_path = CUSTOM_THEMES_DIR / filename

        try:
            with open(dest_path, "w", encoding="utf-8") as f:
                json.dump(colors, f, indent=4)
            QMessageBox.information(self, "Export Successful", f"Theme '{name}' saved successfully to themes/custom/{filename}")
            
            # Update preset combo box choices
            self.preset_combo.clear()
            self.preset_combo.addItems(self.tm.get_themes())
            self.preset_combo.setCurrentText(name)
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to save theme: {e}")

    def apply_theme_live(self) -> None:
        colors = self.get_editor_colors()
        name = colors["name"]
        
        # Save as the custom_theme.json to match manager default custom theme
        custom_file = ROOT / "themes" / "custom_theme.json"
        try:
            with open(custom_file, "w", encoding="utf-8") as f:
                json.dump(colors, f, indent=4)
            
            self.tm.save_active_theme("Custom Theme")
            
            # Apply to main window live
            parent = self.main_window
            if not parent:
                for widget in QApplication.topLevelWidgets():
                    if widget.inherits("QMainWindow"):
                        parent = widget
                        break
            if parent:
                parent.apply_settings()
                QMessageBox.information(self, "Theme Applied", "Applied edited colors live successfully!")
            else:
                QMessageBox.warning(self, "Apply Failed", "Main window instance not found to apply styles.")
        except Exception as e:
            QMessageBox.critical(self, "Apply Failed", f"Failed to apply theme: {e}")
