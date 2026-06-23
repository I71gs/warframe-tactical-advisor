from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from src.core.player_loader import PlayerLoader
from src.core.progression_engine import ProgressionEngine
from src.core.cache_manager import CacheManager

class StatisticsTab(QWidget):
    """GUI tab to display summary statistics and historical progression logs."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.layout = QVBoxLayout()
        
        # Header
        self.header = QLabel("Account Progress Statistics")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc; margin-bottom: 10px;")
        self.layout.addWidget(self.header)
        
        # Grid layout/labels for stats
        self.stats_layout = QVBoxLayout()
        self.weapons_label = QLabel()
        self.mods_label = QLabel()
        self.arcanes_label = QLabel()
        self.quests_label = QLabel()
        self.account_label = QLabel()
        self.completion_bar = QProgressBar()
        
        self.stats_layout.addWidget(self.weapons_label)
        self.stats_layout.addWidget(self.mods_label)
        self.stats_layout.addWidget(self.arcanes_label)
        self.stats_layout.addWidget(self.quests_label)
        self.stats_layout.addWidget(self.account_label)
        self.stats_layout.addWidget(self.completion_bar)
        self.layout.addLayout(self.stats_layout)
        
        # History section
        self.history_header = QLabel("Progression History Snapshots")
        self.history_header.setStyleSheet("font-size: 14px; font-weight: bold; color: #caa3ff; margin-top: 15px; margin-bottom: 5px;")
        self.layout.addWidget(self.history_header)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Readiness (%)", "Story (%)", "Mods (%)", "Arcanes (%)", "Weapons (%)", "Mastery (%)", "Builds (%)"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: #0f1724;
                border: 1px solid rgba(255, 255, 255, 0.05);
                gridline-color: rgba(255, 255, 255, 0.05);
                color: #e6eef6;
            }
            QHeaderView::section {
                background-color: #0b1220;
                color: #caa3ff;
                padding: 6px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                font-weight: bold;
            }
        """)
        self.layout.addWidget(self.history_table)
        
        self.setLayout(self.layout)
        self.load_stats()

    def load_stats(self) -> Any:
        """Load current stats and historical data from database/cache."""
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
        
        # Load and populate history snapshots
        cm = CacheManager()
        history = cm.load_cache("history").get("data", {})
        snapshots = history.get("snapshots", [])
        
        # Sort snapshots in reverse chronological order
        sorted_snapshots = sorted(snapshots, key=lambda s: s.get("timestamp", 0), reverse=True)
        
        self.history_table.setRowCount(len(sorted_snapshots))
        for row, s in enumerate(sorted_snapshots):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(s.get("date", ""))))
            self.history_table.setItem(row, 1, QTableWidgetItem(f"{s.get('readiness', 0.0)}%"))
            self.history_table.setItem(row, 2, QTableWidgetItem(f"{s.get('story', 0.0)}%"))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"{s.get('mods', 0.0)}%"))
            self.history_table.setItem(row, 4, QTableWidgetItem(f"{s.get('arcanes', 0.0)}%"))
            self.history_table.setItem(row, 5, QTableWidgetItem(f"{s.get('weapons', 0.0)}%"))
            self.history_table.setItem(row, 6, QTableWidgetItem(f"{s.get('mastery', 0.0)}%"))
            self.history_table.setItem(row, 7, QTableWidgetItem(f"{s.get('builds', 0.0)}%"))