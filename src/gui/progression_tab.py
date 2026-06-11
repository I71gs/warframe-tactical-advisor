from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from src.core.player_loader import PlayerLoader
from src.core.progression_engine import ProgressionEngine

class ProgressionTab(QWidget):
    """Class ProgressionTab documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.layout = QVBoxLayout()
        self.stage_label = QLabel()
        self.goal_label = QLabel()
        self.quest_label = QLabel()
        self.story_label = QLabel()
        self.readiness_label = QLabel()
        self.mods_label = QLabel()
        self.arcanes_label = QLabel()
        self.weapons_label = QLabel()
        self.story_progress = QProgressBar()
        self.readiness_progress = QProgressBar()
        self.mods_progress = QProgressBar()
        self.arcanes_progress = QProgressBar()
        self.weapons_progress = QProgressBar()
        self.layout.addWidget(self.stage_label)
        self.layout.addWidget(self.goal_label)
        self.layout.addWidget(self.quest_label)
        self.layout.addWidget(self.story_label)
        self.layout.addWidget(self.story_progress)
        self.layout.addWidget(self.readiness_label)
        self.layout.addWidget(self.readiness_progress)
        self.layout.addWidget(self.mods_label)
        self.layout.addWidget(self.mods_progress)
        self.layout.addWidget(self.arcanes_label)
        self.layout.addWidget(self.arcanes_progress)
        self.layout.addWidget(self.weapons_label)
        self.layout.addWidget(self.weapons_progress)
        self.setLayout(self.layout)
        self.load_progress()

    def load_progress(self) -> Any:
        """Method load_progress."""
        player = PlayerLoader().load_player()
        engine = ProgressionEngine()
        stage = engine.determine_stage(player)
        primary_goal = engine.get_primary_goal(player)
        next_quest = engine.get_next_story_quest(player)
        story_completion = engine.get_story_completion_percentage(player)
        readiness_score = engine.get_readiness_score(player)
        mods_completion = engine.get_mod_completion_percentage(player)
        arcane_completion = engine.get_arcane_completion_percentage(player)
        weapon_completion = engine.get_weapon_completion_percentage(player)
        self.stage_label.setText(f'Stage: {stage}')
        self.goal_label.setText(f'Primary Goal: {primary_goal}')
        self.quest_label.setText(f'Next Quest: {next_quest}')
        self.story_label.setText(f'Story Completion: {story_completion}%')
        self.readiness_label.setText(f'Readiness Score: {readiness_score}%')
        self.mods_label.setText(f'Mods Completion: {mods_completion}%')
        self.arcanes_label.setText(f'Arcane Completion: {arcane_completion}%')
        self.weapons_label.setText(f'Weapon Completion: {weapon_completion}%')
        self.story_progress.setValue(int(story_completion))
        self.readiness_progress.setValue(int(readiness_score))
        self.mods_progress.setValue(int(mods_completion))
        self.arcanes_progress.setValue(int(arcane_completion))
        self.weapons_progress.setValue(int(weapon_completion))