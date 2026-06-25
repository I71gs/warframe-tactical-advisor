from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QGroupBox, QPushButton
from PySide6.QtCore import Qt
from src.core.player_loader import PlayerLoader
from src.core.replay_engine import ReplayEngine
from src.core.snapshot_repository import SnapshotRepository
from src.core.app_context import AppContext

class ReplayTab(QWidget):
    """GUI tab visualizing player milestone replay logs and history playback velocities."""

    def __init__(self, main_window=None) -> None:
        super().__init__()
        self.main_window = main_window
        self.context = AppContext()
        self.engine = ReplayEngine()
        self.repo = SnapshotRepository()
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_timeline())
        self.context.event_bus.subscribe("SNAPSHOT_CREATED", lambda data: self.load_timeline())
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Header Row
        header_layout = QHBoxLayout()
        self.header = QLabel("Historical Milestones Replay")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #caa3ff;")
        header_layout.addWidget(self.header)
        header_layout.addStretch()
        
        # Take Snapshot Button
        self.snapshot_btn = QPushButton("Save Daily State Snapshot")
        self.snapshot_btn.clicked.connect(self.save_daily_snapshot)
        header_layout.addWidget(self.snapshot_btn)
        
        self.layout.addLayout(header_layout)
        
        # Velocity telemetry
        self.velocity_lbl = QLabel("Initializing progression speed statistics...")
        self.velocity_lbl.setStyleSheet("font-style: italic; color: #9fb6c8; margin-bottom: 10px;")
        self.layout.addWidget(self.velocity_lbl)
        
        # Replay List Box
        self.timeline_box = QGroupBox("Progression Timeline Pathway")
        timeline_layout = QVBoxLayout(self.timeline_box)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: 1px solid rgba(255,255,255,0.05);
                font-size: 13px;
                padding: 5px;
            }
        """)
        timeline_layout.addWidget(self.list_widget)
        self.layout.addWidget(self.timeline_box)
        
        self.setLayout(self.layout)
        self.load_timeline()

    def load_timeline(self) -> None:
        """Fetch and populate progression timeline statuses."""
        self.list_widget.clear()
        player = PlayerLoader().load_player()
        
        timeline = self.engine.get_timeline_data(player, self.repo)
        
        # Display velocity speed
        velocity = self.engine.calculate_progression_speed(timeline)
        self.velocity_lbl.setText(velocity)
        
        for idx, t in enumerate(timeline):
            status_symbol = "✔" if t["status"] == "unlocked" else "🔒"
            date_info = f" ({t['date_unlocked']})" if t["status"] == "unlocked" else ""
            
            item_text = f"{status_symbol} {t['name']}{date_info} - {t['description']}"
            item = QListWidgetItem(item_text)
            
            # Apply styling matching status
            if t["status"] == "unlocked":
                item.setForeground(Qt.green)
            else:
                item.setForeground(Qt.gray)
                
            self.list_widget.addItem(item)

    def save_daily_snapshot(self) -> None:
        """Manually trigger daily state snapshot creation."""
        player = PlayerLoader().load_player()
        self.repo.save_snapshot(player)
        self.context.event_bus.publish("SNAPSHOT_CREATED")
        if self.main_window and hasattr(self.main_window, "show_status"):
            self.main_window.show_status("Progress snapshot saved successfully!")
