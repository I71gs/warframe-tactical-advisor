from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QSlider
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from src.core.player_loader import PlayerLoader
from src.core.long_term_planner import LongTermPlanner
from src.core.timeline_replay_engine import TimelineReplayEngine

class TimelineTab(QWidget):
    """GUI tab rendering an interactive history playback timeline of milestones."""

    def __init__(self) -> None:
        super().__init__()
        self.planner = LongTermPlanner()
        self.replay_engine = TimelineReplayEngine()
        self.replay_steps: list[dict[str, Any]] = []
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        self.header = QLabel("Interactive Progression Timeline Playback")
        self.header.setStyleSheet("font-size: 14px; font-weight: bold; color: #6fffe8;")
        self.layout.addWidget(self.header)
        
        self.details_label = QLabel()
        self.details_label.setStyleSheet("padding: 8px; background: rgba(0, 163, 204, 0.05); border: 1px solid rgba(255,255,255,0.06); border-radius: 4px;")
        self.layout.addWidget(self.details_label)
        
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        
        # Playback Slider Layout
        slider_layout = QHBoxLayout()
        self.slider_label = QLabel("Playback Step: Select Day")
        self.slider_label.setStyleSheet("font-weight: bold; color: #caa3ff;")
        slider_layout.addWidget(self.slider_label)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.update_playback)
        slider_layout.addWidget(self.slider)
        
        self.layout.addLayout(slider_layout)
        
        self.setLayout(self.layout)
        self.load_timeline()

    def load_timeline(self) -> None:
        """Loads timeline datasets and sets up playback slider ranges."""
        player = PlayerLoader().load_player()
        self.replay_steps = self.replay_engine.get_replay_data(player)
        
        # Set up slider ranges
        if self.replay_steps:
            self.slider.setMinimum(0)
            self.slider.setMaximum(len(self.replay_steps) - 1)
            self.slider.setValue(len(self.replay_steps) - 1)
            self.update_playback(self.slider.value())

    def update_playback(self, index: int) -> None:
        """Drives timeline visualization updates based on active slider positions."""
        if not self.replay_steps or index >= len(self.replay_steps):
            return
            
        step = self.replay_steps[index]
        self.slider_label.setText(f"Playback Step: {step['step_name']}")
        
        # Render details Panel
        details_text = (
            f"<b>Milestone Step:</b> <span style='color: #6fffe8;'>{step['milestone']}</span><br>"
            f"<b>Mastery Rank:</b> MR {step['mastery_rank']}<br>"
            f"<b>Account Readiness:</b> {step['readiness']}%<br>"
            f"<b>Details:</b> {step['details']}"
        )
        self.details_label.setText(details_text)
        
        # Populate List highlights
        self.list_widget.clear()
        for idx, s in enumerate(self.replay_steps):
            is_active = (idx == index)
            is_completed = (idx < index)
            
            status_prefix = "  [✓] " if is_completed else ("  [➔] " if is_active else "  [ ] ")
            text = f"{status_prefix}{s['milestone']}\n      {s['step_name']} - MR {s['mastery_rank']} ({s['readiness']}% Readiness)"
            
            item = QListWidgetItem(text)
            
            if is_completed:
                item.setForeground(QColor("#22c55e"))
            elif is_active:
                item.setForeground(QColor("#6fffe8"))
            else:
                item.setForeground(QColor("#9fb6c8"))
                
            self.list_widget.addItem(item)
            
            if idx < len(self.replay_steps) - 1:
                arrow = QListWidgetItem("         ↓")
                arrow.setForeground(QColor("#9fb6c8"))
                self.list_widget.addItem(arrow)
