from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QHBoxLayout, QComboBox, QMessageBox, QCheckBox
from PySide6.QtWidgets import QFileDialog
from src.core.app_context import AppContext

class ProfileTab(QWidget):
    """GUI tab to manage user mastery, story quest records, mods, arcanes, and weapons inventory."""

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        
        from src.core.knowledge_base import KnowledgeBase
        from src.core.weapon_database import WEAPONS
        from src.core.arcane_database import ARCANES
        self.kb = KnowledgeBase()
        self.weapon_names = [w['name'] for w in WEAPONS]
        self.arcane_names = [a['name'] for a in ARCANES]
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Mastery Rank'))
        self.mr_input = QLineEdit()
        self.mr_input.setPlaceholderText('Enter Mastery Rank')
        self.layout.addWidget(self.mr_input)
        self.steel_path_check = QCheckBox('Steel Path Unlocked')
        self.arbitrations_check = QCheckBox('Arbitrations Unlocked')
        self.helminth_check = QCheckBox('Helminth Unlocked')
        self.layout.addWidget(self.steel_path_check)
        self.layout.addWidget(self.arbitrations_check)
        self.layout.addWidget(self.helminth_check)
        
        self.layout.addWidget(QLabel('Completed Quests'))
        self.quest_search = QLineEdit()
        self.quest_search.setPlaceholderText('Search quests')
        self.quest_search.textChanged.connect(self.filter_quests)
        self.layout.addWidget(self.quest_search)
        self.quest_list = QListWidget()
        self.layout.addWidget(self.quest_list)
        
        self.quest_combo = QComboBox()
        quest_names = [q.get('name') if isinstance(q, dict) else q for q in self.kb.quests]
        for q in sorted([n for n in quest_names if n]):
            self.quest_combo.addItem(q)
        self.quest_input = QLineEdit()
        self.quest_input.setPlaceholderText('Or type a quest to add')
        self.add_quest_btn = QPushButton('Add Quest')
        self.remove_quest_btn = QPushButton('Remove Selected')
        quest_layout = QHBoxLayout()
        quest_layout.addWidget(self.quest_combo)
        quest_layout.addWidget(self.quest_input)
        quest_layout.addWidget(self.add_quest_btn)
        quest_layout.addWidget(self.remove_quest_btn)
        self.layout.addLayout(quest_layout)
        
        self.layout.addWidget(QLabel('Owned Mods'))
        self.mod_search = QLineEdit()
        self.mod_search.setPlaceholderText('Search mods')
        self.mod_search.textChanged.connect(self.filter_mods)
        self.layout.addWidget(self.mod_search)
        self.mod_list = QListWidget()
        self.layout.addWidget(self.mod_list)
        
        self.mod_input = QComboBox()
        for m in sorted([x.get('name') for x in self.kb.mods]):
            if m:
                self.mod_input.addItem(m)
        self.add_mod_btn = QPushButton('Add Mod')
        self.remove_mod_btn = QPushButton('Remove Selected')
        mod_layout = QHBoxLayout()
        mod_layout.addWidget(self.mod_input)
        mod_layout.addWidget(self.add_mod_btn)
        mod_layout.addWidget(self.remove_mod_btn)
        self.layout.addLayout(mod_layout)
        
        self.layout.addWidget(QLabel('Owned Arcanes'))
        self.arcane_search = QLineEdit()
        self.arcane_search.setPlaceholderText('Search arcanes')
        self.arcane_search.textChanged.connect(self.filter_arcanes)
        self.layout.addWidget(self.arcane_search)
        self.arcane_list = QListWidget()
        self.layout.addWidget(self.arcane_list)
        
        self.arcane_input = QComboBox()
        for a in sorted(self.arcane_names):
            self.arcane_input.addItem(a)
        self.add_arcane_btn = QPushButton('Add Arcane')
        self.remove_arcane_btn = QPushButton('Remove Selected')
        arcane_layout = QHBoxLayout()
        arcane_layout.addWidget(self.arcane_input)
        arcane_layout.addWidget(self.add_arcane_btn)
        arcane_layout.addWidget(self.remove_arcane_btn)
        self.layout.addLayout(arcane_layout)
        
        self.layout.addWidget(QLabel('Owned Weapons'))
        self.weapon_search = QLineEdit()
        self.weapon_search.setPlaceholderText('Search weapons')
        self.weapon_search.textChanged.connect(self.filter_weapons)
        self.layout.addWidget(self.weapon_search)
        self.weapon_list = QListWidget()
        self.layout.addWidget(self.weapon_list)
        
        self.weapon_input = QComboBox()
        for w in sorted(self.weapon_names):
            self.weapon_input.addItem(w)
        self.add_weapon_btn = QPushButton('Add Weapon')
        self.remove_weapon_btn = QPushButton('Remove Selected')
        weapon_layout = QHBoxLayout()
        weapon_layout.addWidget(self.weapon_input)
        weapon_layout.addWidget(self.add_weapon_btn)
        weapon_layout.addWidget(self.remove_weapon_btn)
        self.layout.addLayout(weapon_layout)
        
        self.save_button = QPushButton('Save Profile')
        self.export_button = QPushButton('Export Profile')
        self.import_button = QPushButton('Import Profile')
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.export_button)
        self.layout.addWidget(self.import_button)
        
        self.setLayout(self.layout)
        
        self.add_quest_btn.clicked.connect(self.add_quest)
        self.remove_quest_btn.clicked.connect(self.remove_quest)
        self.add_mod_btn.clicked.connect(self.add_mod)
        self.remove_mod_btn.clicked.connect(self.remove_mod)
        self.add_arcane_btn.clicked.connect(self.add_arcane)
        self.remove_arcane_btn.clicked.connect(self.remove_arcane)
        self.add_weapon_btn.clicked.connect(self.add_weapon)
        self.remove_weapon_btn.clicked.connect(self.remove_weapon)
        self.save_button.clicked.connect(self.save_profile)
        self.export_button.clicked.connect(self.export_profile)
        self.import_button.clicked.connect(self.import_profile)
        
        # Subscribe tab to reload automatically on profile or database swaps
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_profile())
        
        self.load_profile()

    def filter_quests(self, text: Any) -> Any:
        q = text.lower()
        self.quest_list.clear()
        player = self.context.player_service.get_player()
        for quest in player.completed_quests:
            if q in quest.lower():
                self.quest_list.addItem(quest.title())

    def filter_mods(self, text: Any) -> Any:
        q = text.lower()
        self.mod_list.clear()
        player = self.context.player_service.get_player()
        for mod in player.owned_mods:
            if q in mod.lower():
                self.mod_list.addItem(mod.title())

    def filter_arcanes(self, text: Any) -> Any:
        q = text.lower()
        self.arcane_list.clear()
        player = self.context.player_service.get_player()
        for a in player.owned_arcanes:
            if q in a.lower():
                self.arcane_list.addItem(a.title())

    def filter_weapons(self, text: Any) -> Any:
        q = text.lower()
        self.weapon_list.clear()
        player = self.context.player_service.get_player()
        for w in player.owned_weapons:
            if q in w.lower():
                self.weapon_list.addItem(w)

    def load_profile(self) -> Any:
        player = self.context.player_service.get_player()
        
        # Temporarily block signals when updating input fields programmatically
        self.mr_input.blockSignals(True)
        self.steel_path_check.blockSignals(True)
        self.arbitrations_check.blockSignals(True)
        self.helminth_check.blockSignals(True)
        
        self.mr_input.setText(str(player.mastery_rank))
        self.steel_path_check.setChecked(player.steel_path_unlocked)
        self.arbitrations_check.setChecked(player.arbitrations_unlocked)
        self.helminth_check.setChecked(player.helminth_unlocked)
        
        self.mr_input.blockSignals(False)
        self.steel_path_check.blockSignals(False)
        self.arbitrations_check.blockSignals(False)
        self.helminth_check.blockSignals(False)
        
        self.quest_list.clear()
        for quest in player.completed_quests:
            self.quest_list.addItem(quest.title())
        self.mod_list.clear()
        for mod in player.owned_mods:
            self.mod_list.addItem(mod.title())
        self.arcane_list.clear()
        for arcane in player.owned_arcanes:
            self.arcane_list.addItem(arcane.title())
        self.weapon_list.clear()
        for weapon in player.owned_weapons:
            self.weapon_list.addItem(weapon)

    def add_quest(self) -> Any:
        quest = self.quest_input.text().strip() or self.quest_combo.currentText().strip()
        if not quest:
            return
        player = self.context.player_service.get_player()
        existing = [q.lower() for q in player.completed_quests]
        if quest.lower() in existing:
            QMessageBox.information(self, 'Already Exists', 'Quest already recorded.')
            return
        self.context.player_service.add_completed_quest(quest)
        self.quest_input.clear()
        self.context.event_bus.publish("STATUS_MESSAGE", {"message": f"Quest added: {quest}"})

    def remove_quest(self) -> Any:
        item = self.quest_list.currentItem()
        if not item:
            return
        resp = QMessageBox.question(self, 'Confirm', f"Remove quest '{item.text()}'?")
        if resp != QMessageBox.StandardButton.Yes:
            return
        self.context.player_service.remove_completed_quest(item.text())
        self.context.event_bus.publish("STATUS_MESSAGE", {"message": f"Quest removed: {item.text()}"})

    def add_mod(self) -> Any:
        mod = self.mod_input.currentText().strip()
        if not mod:
            return
        player = self.context.player_service.get_player()
        existing = [m.lower() for m in player.owned_mods]
        if mod.lower() in existing:
            QMessageBox.information(self, 'Already Exists', 'Mod already recorded.')
            return
        self.context.player_service.add_owned_mod(mod)
        self.context.event_bus.publish("STATUS_MESSAGE", {"message": f"Mod added: {mod}"})

    def remove_mod(self) -> Any:
        item = self.mod_list.currentItem()
        if not item:
            return
        resp = QMessageBox.question(self, 'Confirm', f"Remove mod '{item.text()}'?")
        if resp != QMessageBox.StandardButton.Yes:
            return
        self.context.player_service.remove_owned_mod(item.text())
        self.context.event_bus.publish("STATUS_MESSAGE", {"message": f"Mod removed: {item.text()}"})

    def add_arcane(self) -> Any:
        arcane = self.arcane_input.currentText().strip()
        if not arcane:
            return
        player = self.context.player_service.get_player()
        existing = [a.lower() for a in player.owned_arcanes]
        if arcane.lower() in existing:
            QMessageBox.information(self, 'Already Exists', 'Arcane already recorded.')
            return
        self.context.player_service.add_owned_arcane(arcane)
        self.context.event_bus.publish("STATUS_MESSAGE", {"message": f"Arcane added: {arcane}"})

    def remove_arcane(self) -> Any:
        item = self.arcane_list.currentItem()
        if not item:
            return
        resp = QMessageBox.question(self, 'Confirm', f"Remove arcane '{item.text()}'?")
        if resp != QMessageBox.StandardButton.Yes:
            return
        self.context.player_service.remove_owned_arcane(item.text())
        self.context.event_bus.publish("STATUS_MESSAGE", {"message": f"Arcane removed: {item.text()}"})

    def add_weapon(self) -> Any:
        weapon = self.weapon_input.currentText().strip()
        if not weapon:
            return
        player = self.context.player_service.get_player()
        existing = [w.lower() for w in player.owned_weapons]
        if weapon.lower() in existing:
            QMessageBox.information(self, 'Already Exists', 'Weapon already recorded.')
            return
        self.context.player_service.add_owned_weapon(weapon)
        self.context.event_bus.publish("STATUS_MESSAGE", {"message": f"Weapon added: {weapon}"})

    def remove_weapon(self) -> Any:
        item = self.weapon_list.currentItem()
        if not item:
            return
        resp = QMessageBox.question(self, 'Confirm', f"Remove weapon '{item.text()}'?")
        if resp != QMessageBox.StandardButton.Yes:
            return
        self.context.player_service.remove_owned_weapon(item.text())
        self.context.event_bus.publish("STATUS_MESSAGE", {"message": f"Weapon removed: {item.text()}"})

    def save_profile(self) -> Any:
        try:
            mastery_rank = int(self.mr_input.text() or 0)
        except ValueError:
            QMessageBox.warning(self, 'Invalid Input', 'Mastery Rank must be a whole number.')
            return
        self.context.player_service.save_player(
            mastery_rank,
            self.steel_path_check.isChecked(),
            self.arbitrations_check.isChecked(),
            self.helminth_check.isChecked()
        )
        self.context.event_bus.publish("STATUS_MESSAGE", {"message": "Profile saved successfully"})
        QMessageBox.information(self, 'Saved', 'Profile saved successfully.')

    def export_profile(self) -> Any:
        filename, _ = QFileDialog.getSaveFileName(self, 'Export Profile', 'profile.json', 'JSON Files (*.json)')
        if not filename:
            return
        from src.core.profile_manager import ProfileManager
        try:
            ProfileManager().export_profile(filename)
            QMessageBox.information(self, 'Exported', 'Profile exported successfully.')
            self.context.event_bus.publish("STATUS_MESSAGE", {"message": f"Profile exported: {filename}"})
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Export failed: {e}')

    def import_profile(self) -> Any:
        filename, _ = QFileDialog.getOpenFileName(self, 'Import Profile', '', 'JSON Files (*.json)')
        if not filename:
            return
        from src.core.profile_manager import ProfileManager
        try:
            ProfileManager().import_profile(filename)
            QMessageBox.information(self, 'Imported', 'Profile imported successfully.')
            self.context.event_bus.publish("STATUS_MESSAGE", {"message": f"Profile imported: {filename}"})
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Import failed: {e}')