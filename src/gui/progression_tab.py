from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel
)

from src.core.player_loader import PlayerLoader
from src.core.progression_engine import (
    ProgressionEngine
)


class ProgressionTab(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QVBoxLayout()

        self.stage_label = QLabel()
        self.goal_label = QLabel()
        self.quest_label = QLabel()
        self.story_label = QLabel()
        self.readiness_label = QLabel()
        
        self.mods_label = QLabel()
        self.arcanes_label = QLabel()

        self.layout.addWidget(self.stage_label)
        self.layout.addWidget(self.goal_label)
        self.layout.addWidget(self.quest_label)
        self.layout.addWidget(self.story_label)
        self.layout.addWidget(self.readiness_label)
        self.layout.addWidget(self.mods_label)
        self.setLayout(self.layout)

        self.load_progress()

    def load_progress(self):

        player = PlayerLoader().load_player()

        engine = ProgressionEngine()

        self.stage_label.setText(
            f"Stage: {engine.determine_stage(player)}"
        )

        self.goal_label.setText(
            f"Primary Goal: {engine.get_primary_goal(player)}"
        )

        self.quest_label.setText(
            f"Next Quest: {engine.get_next_story_quest(player)}"
        )

        self.story_label.setText(
            f"Story Completion: "
            f"{engine.get_story_completion_percentage(player)}%"
        )

        self.readiness_label.setText(
            f"Readiness Score: "
            f"{engine.get_readiness_score(player)}%"
        )

        self.mods_label.setText(
            f"Mods Completion: "
            f"{engine.get_mod_completion_percentage(player)}%"
        )

        self.arcanes_label.setText(
            f"Arcanes Completion: "
            f"{engine.get_arcane_completion_percentage(player)}%"
        )