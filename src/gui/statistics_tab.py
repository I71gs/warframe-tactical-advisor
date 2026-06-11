from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from src.core.player_loader import PlayerLoader
from src.core.progression_engine import ProgressionEngine

class StatisticsTab(QWidget):
    """Class StatisticsTab documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Statistics'))
        self.weapons_label = QLabel()
        self.mods_label = QLabel()
        self.arcanes_label = QLabel()
        self.quests_label = QLabel()
        self.account_label = QLabel()
        self.completion_bar = QProgressBar()
        self.layout.addWidget(self.weapons_label)
        self.layout.addWidget(self.mods_label)
        self.layout.addWidget(self.arcanes_label)
        self.layout.addWidget(self.quests_label)
        self.layout.addWidget(self.account_label)
        self.layout.addWidget(self.completion_bar)
        self.setLayout(self.layout)
        self.load_stats()

    def load_stats(self) -> Any:
        """Method load_stats."""
        player = PlayerLoader().load_player()
        engine = ProgressionEngine()
        total_weapons = len(player.owned_weapons)
        total_mods = len(player.owned_mods)
        total_arcanes = len(player.owned_arcanes)
        total_quests = len(player.completed_quests)
        account_completion = engine.get_readiness_score(player)
        self.weapons_label.setText(f'Total Weapons Owned: {total_weapons}')
        self.mods_label.setText(f'Total Mods Owned: {total_mods}')
        self.arcanes_label.setText(f'Total Arcanes Owned: {total_arcanes}')
        self.quests_label.setText(f'Total Quests Completed: {total_quests}')
        self.account_label.setText(f'Account Completion: {account_completion}%')
        self.completion_bar.setValue(int(account_completion))