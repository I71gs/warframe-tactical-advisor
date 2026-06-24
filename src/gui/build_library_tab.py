from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QGroupBox, QTextEdit, QPushButton, QSpinBox, QMessageBox, QCheckBox
from PySide6.QtCore import Qt
from src.core.build_library_engine import BuildLibraryEngine

class BuildLibraryTab(QWidget):
    """GUI tab providing a custom weapon builds library editor with favorite toggles, ratings, and notes."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = BuildLibraryEngine()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Left Panel: Add/Delete & Build List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.header = QLabel("Weapon Build Library")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #caa3ff; margin-bottom: 5px;")
        left_layout.addWidget(self.header)

        # Build list
        self.build_list = QListWidget()
        self.build_list.currentTextChanged.connect(self.load_selected_build)
        left_layout.addWidget(self.build_list)

        # Add new build button
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+ New Build")
        self.add_btn.clicked.connect(self.new_build)
        btn_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.delete_btn)
        left_layout.addLayout(btn_layout)

        self.layout.addWidget(left_widget, 1)

        # Right Panel: Build Editor Card
        self.editor_box = QGroupBox("Build Configuration & Editor")
        self.editor_layout = QVBoxLayout(self.editor_box)
        self.editor_layout.setSpacing(10)

        # Form fields
        self.editor_layout.addWidget(QLabel("Weapon Name:"))
        self.weapon_input = QLineEdit()
        self.editor_layout.addWidget(self.weapon_input)

        self.editor_layout.addWidget(QLabel("Mods (comma-separated):"))
        self.mods_input = QLineEdit()
        self.mods_input.setPlaceholderText("e.g. Serration, Split Chamber, Point Strike...")
        self.editor_layout.addWidget(self.mods_input)

        self.editor_layout.addWidget(QLabel("Arcane Target:"))
        self.arcane_input = QLineEdit()
        self.editor_layout.addWidget(self.arcane_input)

        self.editor_layout.addWidget(QLabel("Element Type:"))
        self.element_input = QLineEdit()
        self.editor_layout.addWidget(self.element_input)

        # Rating & Favorite Row
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("Rating (1-100):"))
        self.rating_spin = QSpinBox()
        self.rating_spin.setRange(1, 100)
        self.rating_spin.setValue(90)
        row_layout.addWidget(self.rating_spin)

        self.fav_check = QCheckBox("Mark as Favorite")
        row_layout.addWidget(self.fav_check)
        self.editor_layout.addLayout(row_layout)

        self.editor_layout.addWidget(QLabel("Custom Build Notes:"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Enter custom notes on performance, testing, synergy, etc...")
        self.editor_layout.addWidget(self.notes_input)

        # Save button
        self.save_btn = QPushButton("Save Build Settings")
        self.save_btn.setStyleSheet("background-color: #22c55e; color: white; font-weight: bold; padding: 6px;")
        self.save_btn.clicked.connect(self.save_current_build)
        self.editor_layout.addWidget(self.save_btn)

        self.layout.addWidget(self.editor_box, 2)
        self.setLayout(self.layout)
        
        # Seed default data if empty
        self.seed_defaults()
        self.refresh_list()

    def seed_defaults(self) -> None:
        builds = self.engine.load_library()
        if not builds:
            self.engine.add_or_update_build(
                weapon="Phenmor Prime Target",
                mods=["Galvanized Chamber", "Galvanized Aptitude", "Serration", "Hellfire"],
                arcane="Primary Merciless",
                element="Viral Heat",
                rating=95,
                notes="Primary Zariman rifle, incredible burst damage.",
                is_favorite=True
            )
            self.engine.add_or_update_build(
                weapon="Kuva Bramma Cluster",
                mods=["Serration", "Split Chamber", "Point Strike", "Cryo Rounds"],
                arcane="Primary Merciless",
                element="Viral",
                rating=88,
                notes="AOE clearing bow, excellent for lower level speed runs.",
                is_favorite=False
            )

    def refresh_list(self) -> None:
        self.build_list.clear()
        builds = self.engine.load_library()
        self.loaded_builds_cache = {b["weapon"].lower(): b for b in builds}
        
        for b in builds:
            fav_star = "★ " if b.get("is_favorite", False) else ""
            item_text = f"{fav_star}{b['weapon']} (Score: {b.get('rating', 90)})"
            item = QListWidgetItem(item_text)
            self.build_list.addItem(item)

        if self.build_list.count() > 0:
            self.build_list.setCurrentRow(0)
        else:
            self.clear_editor()

    def clear_editor(self) -> None:
        self.weapon_input.clear()
        self.mods_input.clear()
        self.arcane_input.clear()
        self.element_input.clear()
        self.rating_spin.setValue(90)
        self.fav_check.setChecked(False)
        self.notes_input.clear()

    def load_selected_build(self, item_text: str) -> None:
        if not item_text:
            self.clear_editor()
            return
            
        weapon_key = None
        for key in self.loaded_builds_cache:
            if key in item_text.lower():
                weapon_key = key
                break
                
        if not weapon_key:
            self.clear_editor()
            return
            
        build = self.loaded_builds_cache[weapon_key]
        self.weapon_input.setText(build["weapon"])
        self.mods_input.setText(", ".join(build.get("mods", [])))
        self.arcane_input.setText(build.get("arcane", ""))
        self.element_input.setText(build.get("element", ""))
        self.rating_spin.setValue(build.get("rating", 90))
        self.fav_check.setChecked(build.get("is_favorite", False))
        self.notes_input.setText(build.get("notes", ""))

    def new_build(self) -> None:
        self.clear_editor()
        self.weapon_input.setText("New Weapon Build")
        self.weapon_input.setFocus()

    def save_current_build(self) -> None:
        weapon = self.weapon_input.text().strip()
        if not weapon or weapon == "New Weapon Build":
            QMessageBox.warning(self, "Invalid Name", "Please enter a valid weapon name.")
            return

        mods_list = [m.strip() for m in self.mods_input.text().split(",") if m.strip()]
        arcane = self.arcane_input.text().strip()
        element = self.element_input.text().strip()
        rating = self.rating_spin.value()
        is_favorite = self.fav_check.isChecked()
        notes = self.notes_input.toPlainText().strip()

        self.engine.add_or_update_build(
            weapon=weapon,
            mods=mods_list,
            arcane=arcane,
            element=element,
            rating=rating,
            notes=notes,
            is_favorite=is_favorite
        )
        self.refresh_list()
        for row in range(self.build_list.count()):
            if weapon.lower() in self.build_list.item(row).text().lower():
                self.build_list.setCurrentRow(row)
                break
        QMessageBox.information(self, "Build Saved", f"Successfully saved custom build for '{weapon}'.")

    def delete_selected(self) -> None:
        current_item = self.build_list.currentItem()
        if not current_item:
            return
        
        item_text = current_item.text()
        weapon_key = None
        for key in self.loaded_builds_cache:
            if key in item_text.lower():
                weapon_key = key
                break
                
        if not weapon_key:
            return
            
        build = self.loaded_builds_cache[weapon_key]
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the build for '{build['weapon']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.engine.delete_build(build["weapon"])
            self.refresh_list()
