from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QGroupBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from src.core.theme_manager import ThemeManager

class ThemeTab(QWidget):
    """GUI tab providing real-time base theme & accent pack selector and CSS preview cards."""

    def __init__(self, main_window: Any = None) -> None:
        super().__init__()
        self.main_window = main_window
        self.theme_manager = ThemeManager()
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        self.header = QLabel("Visual Theme Selector")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #caa3ff; margin-bottom: 10px;")
        self.layout.addWidget(self.header)
        
        # Selector Layout
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Base Theme:"))
        self.base_combo = QComboBox()
        self.base_combo.addItems(["Dark", "Light"])
        self.base_combo.currentTextChanged.connect(self.on_selection_changed)
        select_layout.addWidget(self.base_combo)
        
        select_layout.addWidget(QLabel("Accent Pack:"))
        self.accent_combo = QComboBox()
        self.accent_combo.addItems(["None", "Lotus", "Corpus", "Orokin", "Zariman", "Grineer", "Cosmic Twilight"])
        self.accent_combo.currentTextChanged.connect(self.on_selection_changed)
        select_layout.addWidget(self.accent_combo)
        
        self.layout.addLayout(select_layout)
        
        # Preview Panel
        self.preview_box = QGroupBox("Theme Color Mapping Preview")
        preview_layout = QVBoxLayout(self.preview_box)
        
        self.color_labels: dict[str, QLabel] = {}
        for key in ["PRIMARY", "SECONDARY", "ACCENT", "TEXT", "MUTED", "CARD"]:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{key}:"))
            color_lbl = QLabel("Color Block")
            color_lbl.setAlignment(Qt.AlignCenter)
            row.addWidget(color_lbl)
            preview_layout.addLayout(row)
            self.color_labels[key] = color_lbl
            
        self.layout.addWidget(self.preview_box)
        
        # Apply button
        self.apply_btn = QPushButton("Apply Active Theme")
        self.apply_btn.clicked.connect(self.apply_theme)
        self.layout.addWidget(self.apply_btn)
        
        self.layout.addStretch()
        self.setLayout(self.layout)
        
        # Initialize values
        active_theme = self.theme_manager.get_active_theme_name()
        base_val = "Dark"
        accent_val = "None"
        if " (" in active_theme and active_theme.endswith(")"):
            base_val, rest = active_theme.split(" (", 1)
            accent_val = rest[:-1]
        elif active_theme in ["Dark", "Light"]:
            base_val = active_theme
            accent_val = "None"
            
        self.base_combo.setCurrentText(base_val)
        self.accent_combo.setCurrentText(accent_val)
        self.update_preview()

    def get_selected_theme_name(self) -> str:
        base = self.base_combo.currentText()
        accent = self.accent_combo.currentText()
        if accent == "None":
            return base
        return f"{base} ({accent})"

    def on_selection_changed(self, text: str) -> None:
        self.update_preview()

    def update_preview(self) -> None:
        """Update color block previews when selection changes."""
        theme_name = self.get_selected_theme_name()
        colors = self.theme_manager.get_theme_colors(theme_name)
        for key, lbl in self.color_labels.items():
            color = colors.get(key, "#ffffff")
            lbl.setText(color)
            txt_color = "#000000" if key in ["ACCENT", "TEXT", "MUTED"] else "#ffffff"
            lbl.setStyleSheet(f"background-color: {color}; color: {txt_color}; font-weight: bold; border-radius: 4px; padding: 2px;")

    def apply_theme(self) -> None:
        """Saves selected theme selection and publishes to the system."""
        theme_name = self.get_selected_theme_name()
        self.theme_manager.save_active_theme(theme_name)
        
        # Publish event
        from src.core.app_context import AppContext
        AppContext().event_bus.publish("SETTINGS_CHANGED")
        
        # Apply style to parent window directly if available
        parent = self.main_window
        if not parent:
            from PySide6.QtWidgets import QApplication
            for widget in QApplication.topLevelWidgets():
                if widget.inherits("QMainWindow"):
                    parent = widget
                    break
                    
        if parent and hasattr(parent, "apply_settings"):
            parent.apply_settings()
            if hasattr(parent, "show_status"):
                parent.show_status(f"Applied visual theme: {theme_name}")
