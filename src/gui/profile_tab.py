from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QHBoxLayout
)

from src.core.player_loader import PlayerLoader
from src.database.database import DatabaseManager
from src.models import player


class ProfileTab(QWidget):

    def __init__(self, refresh_callback=None):

        super().__init__()

        self.refresh_callback = refresh_callback
        self.db = DatabaseManager()

        self.layout = QVBoxLayout()

        # -------------------------
        # Mastery Rank
        # -------------------------
        self.layout.addWidget(QLabel("Mastery Rank"))

        self.mr_input = QLineEdit()
        self.layout.addWidget(self.mr_input)

        # -------------------------
        # Quests
        # -------------------------
        self.layout.addWidget(QLabel("Completed Quests"))

        self.quest_list = QListWidget()
        self.layout.addWidget(self.quest_list)

        self.quest_input = QLineEdit()
        self.quest_input.setPlaceholderText("Add Quest")

        self.add_quest_btn = QPushButton("Add Quest")

        quest_layout = QHBoxLayout()
        quest_layout.addWidget(self.quest_input)
        quest_layout.addWidget(self.add_quest_btn)

        self.layout.addLayout(quest_layout)

        # -------------------------
        # Mods
        # -------------------------
        self.layout.addWidget(QLabel("Owned Mods"))

        self.mod_list = QListWidget()
        self.layout.addWidget(self.mod_list)

        self.mod_input = QLineEdit()
        self.mod_input.setPlaceholderText("Add Mod")

        self.add_mod_btn = QPushButton("Add Mod")

        mod_layout = QHBoxLayout()
        mod_layout.addWidget(self.mod_input)
        mod_layout.addWidget(self.add_mod_btn)

        self.layout.addLayout(mod_layout)

        # -------------------------
        # ARCANE
        # -------------------------

        self.arcane_list = QListWidget()
        self.layout.addWidget(self.arcane_list)

        self.arcane_input = QLineEdit()
        self.arcane_input.setPlaceholderText("Add Arcane")

        self.add_arcane_btn = QPushButton("Add Arcane")

        arcane_layout = QHBoxLayout()
        arcane_layout.addWidget(self.arcane_input)
        arcane_layout.addWidget(self.add_arcane_btn)

        self.layout.addLayout(arcane_layout)

        # -------------------------
        # Save Button
        # -------------------------
        self.save_button = QPushButton("Save Profile")
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        # -------------------------
        # Signals
        # -------------------------
        self.add_quest_btn.clicked.connect(self.add_quest)
        self.add_mod_btn.clicked.connect(self.add_mod)
        self.add_arcane_btn.clicked.connect(self.add_arcane)
        self.save_button.clicked.connect(self.save_profile)

        self.load_profile()

    # -------------------------
    # Load
    # -------------------------
    def load_profile(self):

        player = PlayerLoader().load_player()

        self.mr_input.setText(str(player.mastery_rank))

        self.quest_list.clear()
        for q in player.completed_quests:
            self.quest_list.addItem(q.title())

        self.mod_list.clear()
        for m in player.owned_mods:
            self.mod_list.addItem(m.title())

        self.arcane_list.clear()
        for arcane in player.owned_arcanes:

            self.arcane_list.addItem(
                arcane
            )
    # -------------------------
    # Add Quest
    # -------------------------
    def add_quest(self):

        quest = self.quest_input.text().strip()

        if not quest:
            return

        self.db.add_completed_quest(quest)

        self.quest_input.clear()

        self.load_profile()

        if self.refresh_callback:
            self.refresh_callback()

    # -------------------------
    # Add Mod
    # -------------------------
    def add_mod(self):

        mod = self.mod_input.text().strip()

        if not mod:
            return

        self.db.add_owned_mod(mod)

        self.mod_input.clear()

        self.load_profile()

        if self.refresh_callback:
            self.refresh_callback()

    # -------------------------
    # Add Arcane
    # -------------------------
    def add_arcane(self):

        arcane = (
            self.arcane_input.text()
            .strip()
        )

        if not arcane:
            return

        self.db.add_owned_arcane(
            arcane
        )

        self.arcane_input.clear()

        self.load_profile()

        if self.refresh_callback:
            self.refresh_callback()

    # -------------------------
    # Save
    # -------------------------
    def save_profile(self):

        mastery_rank = int(
            self.mr_input.text() or 0
        )

        self.db.save_player(
            mastery_rank,
            False
        )

        if self.refresh_callback:
            self.refresh_callback()