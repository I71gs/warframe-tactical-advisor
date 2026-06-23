from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from src.core.player_loader import PlayerLoader
from src.core.companion_engine import CompanionEngine

from src.core.app_context import AppContext

class CompanionTab(QWidget):
    """GUI tab rendering companion recommendations and detail tables."""

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        self.engine = self.context.resource_service.companion_engine
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_companions())
        
        self.layout = QVBoxLayout()
        self.header = QLabel("Companion & Sentinel Advisor")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc; margin-bottom: 5px;")
        self.layout.addWidget(self.header)
        
        # Recommended Box
        self.rec_box = QGroupBox("Recommended Active Companion")
        self.rec_layout = QVBoxLayout(self.rec_box)
        self.rec_title = QLabel("Panzer Vulpaphyla")
        self.rec_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #caa3ff;")
        self.rec_stats = QLabel("Synergy: 95% | Survivability: 100% | Utility: 98%")
        self.rec_desc = QLabel("-")
        self.rec_desc.setWordWrap(True)
        self.rec_layout.addWidget(self.rec_title)
        self.rec_layout.addWidget(self.rec_stats)
        self.rec_layout.addWidget(self.rec_desc)
        self.layout.addWidget(self.rec_box)
        
        # Table of all companions
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Companion Name", "Synergy Score", "Survivability", "Utility Rating", "Combat Rationale"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0f1724;
                border: 1px solid rgba(255, 255, 255, 0.05);
                gridline-color: rgba(255, 255, 255, 0.05);
                color: #e6eef6;
            }
            QHeaderView::section {
                background-color: #0b1220;
                color: #caa3ff;
                padding: 4px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                font-weight: bold;
            }
        """)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        self.load_companions()

    def load_companions(self) -> None:
        player = PlayerLoader().load_player()
        
        # Set Active recommendation
        rec = self.engine.recommend_companion(player)
        self.rec_title.setText(f"★ Coach Choice: {rec['name']}")
        self.rec_stats.setText(f"Synergy: {rec['synergy']} | Survivability: {rec['survivability']} | Utility: {rec['utility']}")
        self.rec_desc.setText(f"<b>Active Suggestion:</b> {rec['rationale']}")
        
        # Populate Table
        comps = self.engine.get_companions()
        self.table.setRowCount(len(comps))
        
        bold_font = QFont()
        bold_font.setBold(True)
        
        for row, c in enumerate(comps):
            name_item = QTableWidgetItem(c["name"])
            name_item.setFont(bold_font)
            if c["name"] == rec["name"]:
                name_item.setForeground(QColor("#22c55e"))
            self.table.setItem(row, 0, name_item)
            
            self.table.setItem(row, 1, QTableWidgetItem(c["synergy"]))
            self.table.setItem(row, 2, QTableWidgetItem(c["survivability"]))
            self.table.setItem(row, 3, QTableWidgetItem(c["utility"]))
            self.table.setItem(row, 4, QTableWidgetItem(c["rationale"]))
