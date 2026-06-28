from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QGroupBox, QTextEdit, QPushButton, QSpinBox,
    QMessageBox, QCheckBox, QComboBox, QTabWidget, QSplitter
)
from PySide6.QtCore import Qt
from src.core.build_library_engine import BuildLibraryEngine

class BuildLibraryTab(QWidget):
    """GUI tab providing a custom weapon builds library editor and curated target scenarios."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = BuildLibraryEngine()

        root_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        root_layout.addWidget(self.tabs)

        self.tabs.addTab(self._build_custom_tab(), "✏️ Custom Builds")
        self.tabs.addTab(self._build_curated_tab(), "🏆 Curated Tier Templates")

        self.setLayout(root_layout)

    def _build_custom_tab(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)

        # Left Panel: Add/Delete & Build List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.header = QLabel("Custom Builds")
        self.header.setStyleSheet("font-size: 14px; font-weight: bold; color: #caa3ff; margin-bottom: 5px;")
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

        layout.addWidget(left_widget, 1)

        # Right Panel: Build Editor Card
        self.editor_box = QGroupBox("Build Configuration & Editor")
        self.editor_layout = QVBoxLayout(self.editor_box)
        self.editor_layout.setSpacing(8)

        # Form fields
        self.editor_layout.addWidget(QLabel("Weapon Name:"))
        self.weapon_input = QLineEdit()
        self.editor_layout.addWidget(self.weapon_input)

        self.editor_layout.addWidget(QLabel("Target Scenario / Activity:"))
        self.scenario_input = QComboBox()
        self.scenario_input.addItems(["General Use", "Steel Path General", "Eidolon Hunting", "Profit-Taker Speedrun", "Archon Hunt Boss", "Level Cap / Endurance"])
        self.scenario_input.setEditable(True)
        self.editor_layout.addWidget(self.scenario_input)

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

        layout.addWidget(self.editor_box, 2)

        # Seed default data if empty
        self.seed_defaults()
        self.refresh_list()
        return w

    def _build_curated_tab(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)

        # Left list of templates
        left_w = QWidget()
        left_lay = QVBoxLayout(left_w)
        left_lay.addWidget(QLabel("Select Template to Apply:"))
        
        self.curated_list = QListWidget()
        self.curated_list.currentTextChanged.connect(self.load_curated_details)
        left_lay.addWidget(self.curated_list)

        apply_btn = QPushButton("📥 Copy to Custom Library")
        apply_btn.setStyleSheet("background-color: #00a3cc; color: white; font-weight: bold; padding: 6px;")
        apply_btn.clicked.connect(self.apply_curated_build)
        left_lay.addWidget(apply_btn)

        lay.addWidget(left_w, 1)

        # Right detail card
        self.curated_box = QGroupBox("Curated Blueprint Details")
        curated_lay = QVBoxLayout(self.curated_box)
        self.curated_details = QTextEdit()
        self.curated_details.setReadOnly(True)
        self.curated_details.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        curated_lay.addWidget(self.curated_details)

        lay.addWidget(self.curated_box, 2)
        
        self.load_curated_templates()
        return w

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
                is_favorite=True,
                scenario="Steel Path General"
            )
            self.engine.add_or_update_build(
                weapon="Kuva Bramma Cluster",
                mods=["Serration", "Split Chamber", "Point Strike", "Cryo Rounds"],
                arcane="Primary Merciless",
                element="Viral",
                rating=88,
                notes="AOE clearing bow, excellent for lower level speed runs.",
                is_favorite=False,
                scenario="General Use"
            )

    def refresh_list(self) -> None:
        self.build_list.clear()
        builds = self.engine.load_library()
        self.loaded_builds_cache = {f"{b['weapon'].lower()} ({b.get('scenario', 'General Use').lower()})": b for b in builds}
        
        for b in builds:
            fav_star = "★ " if b.get("is_favorite", False) else ""
            scen = b.get("scenario", "General Use")
            item_text = f"{fav_star}{b['weapon']} [{scen}] (Score: {b.get('rating', 90)})"
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
            
        build_match = None
        for key, val in self.loaded_builds_cache.items():
            # Check matching pattern safely
            if val["weapon"].lower() in item_text.lower() and val.get("scenario", "General Use").lower() in item_text.lower():
                build_match = val
                break
                
        if not build_match:
            self.clear_editor()
            return
            
        self.weapon_input.setText(build_match["weapon"])
        self.scenario_input.setCurrentText(build_match.get("scenario", "General Use"))
        self.mods_input.setText(", ".join(build_match.get("mods", [])))
        self.arcane_input.setText(build_match.get("arcane", ""))
        self.element_input.setText(build_match.get("element", ""))
        self.rating_spin.setValue(build_match.get("rating", 90))
        self.fav_check.setChecked(build_match.get("is_favorite", False))
        self.notes_input.setText(build_match.get("notes", ""))

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
        scenario = self.scenario_input.currentText().strip()

        self.engine.add_or_update_build(
            weapon=weapon,
            mods=mods_list,
            arcane=arcane,
            element=element,
            rating=rating,
            notes=notes,
            is_favorite=is_favorite,
            scenario=scenario
        )
        self.refresh_list()
        QMessageBox.information(self, "Build Saved", f"Successfully saved custom build for '{weapon}' [{scenario}].")

    def delete_selected(self) -> None:
        current_item = self.build_list.currentItem()
        if not current_item:
            return
        
        item_text = current_item.text()
        build_match = None
        for key, val in self.loaded_builds_cache.items():
            if val["weapon"].lower() in item_text.lower() and val.get("scenario", "General Use").lower() in item_text.lower():
                build_match = val
                break
                
        if not build_match:
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the build for '{build_match['weapon']}' [{build_match.get('scenario', 'General Use')}]?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.engine.delete_build(build_match["weapon"], build_match.get("scenario", "General Use"))
            self.refresh_list()

    # Curated tab details
    def load_curated_templates(self) -> None:
        self.curated_list.clear()
        self.curated_cache = self.engine.get_curated_builds()
        for cb in self.curated_cache:
            self.curated_list.addItem(f"{cb['weapon']} — {cb['scenario']}")

    def load_curated_details(self, item_text: str) -> None:
        if not item_text:
            self.curated_details.clear()
            return
        target = next((cb for cb in self.curated_cache if f"{cb['weapon']} — {cb['scenario']}" == item_text), None)
        if not target:
            self.curated_details.clear()
            return
        
        lines = [
            f"Weapon:     {target['weapon']}",
            f"Scenario:   {target['scenario']}",
            f"Element:    {target['element']}",
            f"Rating:     {target['rating']}/100",
            f"Arcane:     {target['arcane']}",
            "",
            "Mods List:",
            *[f"  • {m}" for m in target['mods']],
            "",
            "Design / Rationale:",
            f"  {target['notes']}"
        ]
        self.curated_details.setPlainText("\n".join(lines))

    def apply_curated_build(self) -> None:
        cur_item = self.curated_list.currentItem()
        if not cur_item:
            return
        item_text = cur_item.text()
        target = next((cb for cb in self.curated_cache if f"{cb['weapon']} — {cb['scenario']}" == item_text), None)
        if not target:
            return
        
        self.engine.add_or_update_build(
            weapon=target["weapon"],
            mods=target["mods"],
            arcane=target["arcane"],
            element=target["element"],
            rating=target["rating"],
            notes=target["notes"],
            is_favorite=True,
            scenario=target["scenario"]
        )
        self.refresh_list()
        QMessageBox.information(self, "Build Imported", f"Copied '{target['weapon']}' template to custom library.")
