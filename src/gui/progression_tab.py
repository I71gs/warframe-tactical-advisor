from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame
from PySide6.QtCore import Qt
from src.core.player_loader import PlayerLoader
from src.core.progression_engine import ProgressionEngine
from src.gui.widgets.custom_charts import CircularProgress

class ProgressionTab(QWidget):
    """GUI tab showcasing progression stage, goals, and multi-dimensional circular progress indicators."""

    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)

        # Header Info Card
        self.header_card = QFrame()
        self.header_card.setStyleSheet("""
            QFrame {
                background-color: #0f1724;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
        """)
        header_lay = QVBoxLayout(self.header_card)
        header_lay.setContentsMargins(15, 15, 15, 15)
        header_lay.setSpacing(8)

        self.title_lbl = QLabel("🛡️ Progression Stage & Objectives")
        self.title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #caa3ff; border: none;")
        header_lay.addWidget(self.title_lbl)

        info_row = QHBoxLayout()
        self.stage_label = QLabel("Stage: -")
        self.stage_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #00d4ff; border: none;")
        info_row.addWidget(self.stage_label)

        self.goal_label = QLabel("Primary Goal: -")
        self.goal_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffb76b; border: none;")
        info_row.addWidget(self.goal_label)

        self.quest_label = QLabel("Next Quest: -")
        self.quest_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #7fffb3; border: none;")
        info_row.addWidget(self.quest_label)
        header_lay.addLayout(info_row)
        
        self.layout.addWidget(self.header_card)

        # Grid for Circular Progress Indicators
        grid_container = QFrame()
        grid_container.setStyleSheet("""
            QFrame {
                background-color: #0b1220;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }
        """)
        self.grid = QGridLayout(grid_container)
        self.grid.setContentsMargins(15, 15, 15, 15)
        self.grid.setSpacing(20)

        # Initialize native circular progress rings
        self.story_progress = CircularProgress(self, color="#00d4ff", min_size=120, subtitle="Story Completion")
        self.readiness_progress = CircularProgress(self, color="#ff9fd4", min_size=120, subtitle="Readiness Score")
        self.mods_progress = CircularProgress(self, color="#caa3ff", min_size=120, subtitle="Mods Completion")
        self.arcanes_progress = CircularProgress(self, color="#7fb3ff", min_size=120, subtitle="Arcane Completion")
        self.weapons_progress = CircularProgress(self, color="#ffb76b", min_size=120, subtitle="Weapon Completion")

        # Layout rings inside grid
        self._add_ring_to_grid(self.story_progress, "Story Completion", 0, 0)
        self._add_ring_to_grid(self.readiness_progress, "Readiness Score", 0, 1)
        self._add_ring_to_grid(self.mods_progress, "Mods Collection", 0, 2)
        self._add_ring_to_grid(self.arcanes_progress, "Arcanes Collection", 1, 0)
        self._add_ring_to_grid(self.weapons_progress, "Weapons Collection", 1, 1)

        self.layout.addWidget(grid_container, 1)
        self.load_progress()

    def _add_ring_to_grid(self, ring: CircularProgress, title: str, row: int, col: int) -> None:
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #0f1724;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 6px;
            }
        """)
        lay = QVBoxLayout(container)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #8e85a6; border: none;")
        title_lbl.setAlignment(Qt.AlignCenter)
        
        lay.addWidget(title_lbl)
        lay.addWidget(ring, 1)
        self.grid.addWidget(container, row, col)

    def load_progress(self) -> Any:
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
        
        self.stage_label.setText(f"Stage:  {stage.title().replace('_', ' ')}")
        self.goal_label.setText(f"Primary Goal:  {primary_goal}")
        self.quest_label.setText(f"Next Quest:  {next_quest}")
        
        self.story_progress.set_value(story_completion)
        self.readiness_progress.set_value(readiness_score)
        self.mods_progress.set_value(mods_completion)
        self.arcanes_progress.set_value(arcane_completion)
        self.weapons_progress.set_value(weapon_completion)