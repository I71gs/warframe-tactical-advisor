from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QHBoxLayout, QComboBox, QMessageBox
from src.core.player_loader import PlayerLoader
from src.database.database import DatabaseManager
from PySide6.QtWidgets import QFileDialog
from src.core.profile_manager import ProfileManager

class ProfileTab(QWidget):
    """Class ProfileTab documentation."""

    def __init__(self, refresh_callback: Any=None, status_callback: Any=None) -> None:
        """Initialize the class."""
        super().__init__()
        self.refresh_callback = refresh_callback
        self.status_callback = status_callback
        self.db = DatabaseManager()
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
        self.save_button.clicked.connect(self.save_profile)
        self.export_button.clicked.connect(self.export_profile)
        self.import_button.clicked.connect(self.import_profile)
        self.add_weapon_btn.clicked.connect(self.add_weapon)
        self.remove_weapon_btn.clicked.connect(self.remove_weapon)
        self.load_profile()

    def filter_quests(self, text: Any) -> Any:
        """Method filter_quests."""
        q = text.lower()
        self.quest_list.clear()
        for quest in self.db.get_completed_quests():
            if q in quest.lower():
                self.quest_list.addItem(quest)

    def filter_mods(self, text: Any) -> Any:
        """Method filter_mods."""
        q = text.lower()
        self.mod_list.clear()
        for mod in self.db.get_owned_mods():
            if q in mod.lower():
                self.mod_list.addItem(mod)

    def filter_arcanes(self, text: Any) -> Any:
        """Method filter_arcanes."""
        q = text.lower()
        self.arcane_list.clear()
        for a in self.db.get_owned_arcanes():
            if q in a.lower():
                self.arcane_list.addItem(a)

    def filter_weapons(self, text: Any) -> Any:
        """Method filter_weapons."""
        q = text.lower()
        self.weapon_list.clear()
        for w in self.db.get_owned_weapons():
            if q in w.lower():
                self.weapon_list.addItem(w)

    def load_profile(self) -> Any:
        """Method load_profile."""
        player = PlayerLoader().load_player()
        self.mr_input.setText(str(player.mastery_rank))
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
        """Method add_quest."""
        quest = self.quest_input.text().strip() or self.quest_combo.currentText().strip()
        if not quest:
            return
        existing = [q.lower() for q in self.db.get_completed_quests()]
        if quest.lower() in existing:
            QMessageBox.information(self, 'Already Exists', 'Quest already recorded.')
            return
        self.db.add_completed_quest(quest)
        self.quest_input.clear()
        self.load_profile()
        if self.status_callback:
            self.status_callback('Quest added')
        if self.refresh_callback:
            self.refresh_callback()

    def remove_quest(self) -> Any:
        """Method remove_quest."""
        item = self.quest_list.currentItem()
        if not item:
            return
        resp = QMessageBox.question(self, 'Confirm', f"Remove quest '{item.text()}'?")
        if resp != QMessageBox.StandardButton.Yes:
            return
        self.db.remove_completed_quest(item.text())
        self.load_profile()
        if self.status_callback:
            self.status_callback('Quest removed')
        if self.refresh_callback:
            self.refresh_callback()

    def add_mod(self) -> Any:
        """Method add_mod."""
        mod = self.mod_input.currentText().strip()
        if not mod:
            return
        existing = [m.lower() for m in self.db.get_owned_mods()]
        if mod.lower() in existing:
            QMessageBox.information(self, 'Already Exists', 'Mod already recorded.')
            return
        self.db.add_owned_mod(mod)
        self.load_profile()
        if self.status_callback:
            self.status_callback('Mod added')
        if self.refresh_callback:
            self.refresh_callback()

    def remove_mod(self) -> Any:
        """Method remove_mod."""
        item = self.mod_list.currentItem()
        if not item:
            return
        resp = QMessageBox.question(self, 'Confirm', f"Remove mod '{item.text()}'?")
        if resp != QMessageBox.StandardButton.Yes:
            return
        self.db.remove_owned_mod(item.text())
        self.load_profile()
        if self.status_callback:
            self.status_callback('Mod removed')
        if self.refresh_callback:
            self.refresh_callback()

    def add_arcane(self) -> Any:
        """Method add_arcane."""
        arcane = self.arcane_input.currentText().strip()
        if not arcane:
            return
        existing = [a.lower() for a in self.db.get_owned_arcanes()]
        if arcane.lower() in existing:
            QMessageBox.information(self, 'Already Exists', 'Arcane already recorded.')
            return
        self.db.add_owned_arcane(arcane)
        self.load_profile()
        if self.status_callback:
            self.status_callback('Arcane added')
        if self.refresh_callback:
            self.refresh_callback()

    def remove_arcane(self) -> Any:
        """Method remove_arcane."""
        item = self.arcane_list.currentItem()
        if not item:
            return
        resp = QMessageBox.question(self, 'Confirm', f"Remove arcane '{item.text()}'?")
        if resp != QMessageBox.StandardButton.Yes:
            return
        self.db.remove_owned_arcane(item.text())
        self.load_profile()
        if self.status_callback:
            self.status_callback('Arcane removed')
        if self.refresh_callback:
            self.refresh_callback()

    def save_profile(self) -> Any:
        """Method save_profile."""
        try:
            mastery_rank = int(self.mr_input.text() or 0)
        except ValueError:
            QMessageBox.warning(self, 'Invalid Input', 'Mastery Rank must be a whole number.')
            return
        self.db.save_player(mastery_rank, False)
        if self.status_callback:
            self.status_callback('Profile saved')
        QMessageBox.information(self, 'Saved', 'Profile saved successfully.')
        if self.refresh_callback:
            self.refresh_callback()

    def export_profile(self) -> Any:
        """Method export_profile."""
        filename, _ = QFileDialog.getSaveFileName(self, 'Export Profile', 'profile.json', 'JSON Files (*.json)')
        if not filename:
            return
        manager = ProfileManager()
        try:
            manager.export_profile(filename)
            QMessageBox.information(self, 'Exported', 'Profile exported successfully.')
            if self.status_callback:
                self.status_callback('Export successful')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Export failed: {e}')

    def import_profile(self) -> Any:
        """Method import_profile."""
        filename, _ = QFileDialog.getOpenFileName(self, 'Import Profile', '', 'JSON Files (*.json)')
        if not filename:
            return
        manager = ProfileManager()
        try:
            manager.import_profile(filename)
            QMessageBox.information(self, 'Imported', 'Profile imported successfully.')
            if self.status_callback:
                self.status_callback('Import successful')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Import failed: {e}')
        self.load_profile()
        if self.refresh_callback:
            self.refresh_callback()

    def add_weapon(self) -> Any:
        """Method add_weapon."""
        weapon = self.weapon_input.currentText().strip()
        if not weapon:
            return
        existing = [w.lower() for w in self.db.get_owned_weapons()]
        if weapon.lower() in existing:
            QMessageBox.information(self, 'Already Exists', 'Weapon already recorded.')
            return
        self.db.add_owned_weapon(weapon)
        self.load_profile()
        if self.status_callback:
            self.status_callback('Weapon added')
        if self.refresh_callback:
            self.refresh_callback()

    def remove_weapon(self) -> Any:
        """Method remove_weapon."""
        item = self.weapon_list.currentItem()
        if not item:
            return
        resp = QMessageBox.question(self, 'Confirm', f"Remove weapon '{item.text()}'?")
        if resp != QMessageBox.StandardButton.Yes:
            return
        self.db.remove_owned_weapon(item.text())
        self.load_profile()
        if self.status_callback:
            self.status_callback('Weapon removed')
        if self.refresh_callback:
            self.refresh_callback()