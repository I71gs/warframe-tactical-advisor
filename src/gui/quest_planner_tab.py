from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from src.core.player_loader import PlayerLoader
from src.core.quest_planner import QuestPlanner

class QuestPlannerTab(QWidget):
    """Class QuestPlannerTab documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.layout = QVBoxLayout()
        self.title = QLabel('Recommended Story Progression')
        self.quest_list = QListWidget()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.quest_list)
        self.setLayout(self.layout)
        self.load_quests()

    def load_quests(self) -> Any:
        """Method load_quests."""
        print('Quest Planner Refreshed')
        self.quest_list.clear()
        player = PlayerLoader().load_player()
        planner = QuestPlanner()
        roadmap = planner.get_roadmap(player)
        for quest in roadmap:
            self.quest_list.addItem(quest)