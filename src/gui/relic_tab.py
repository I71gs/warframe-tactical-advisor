from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from src.core.relic_engine import RelicEngine

from src.core.app_context import AppContext

class RelicTab(QWidget):
    """GUI tab matching prime drop targets to specific void relics and refinement guides."""

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        self.engine = self.context.resource_service.relic_engine
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_relics())
        
        self.layout = QVBoxLayout()
        self.header = QLabel("Prime Parts & Void Relics Planner")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #caa3ff; margin-bottom: 5px;")
        self.layout.addWidget(self.header)
        
        # Search row
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search Prime Part / Relic:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("e.g. Glaive, Axi, Saryn...")
        self.search_input.textChanged.connect(self.load_relics)
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)
        
        # Relics Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Target Prime Item", "Relic Required", "Item Rarity", "Recommended Refinement", "Drop Chance", "Best Farm Location"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
        self.load_relics()

    def load_relics(self) -> None:
        query = self.search_input.text()
        results = self.engine.search_relics(query)
        
        self.table.setRowCount(len(results))
        bold_font = QFont()
        bold_font.setBold(True)
        
        for row, item in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(item["item"]))
            
            relic_item = QTableWidgetItem(item["relic"])
            relic_item.setFont(bold_font)
            relic_item.setForeground(QColor("#00a3cc"))
            self.table.setItem(row, 1, relic_item)
            
            self.table.setItem(row, 2, QTableWidgetItem(item["rarity"]))
            
            refine = item["best_refinement"]
            refine_item = QTableWidgetItem(refine)
            if refine == "Radiant":
                refine_item.setForeground(QColor("#ffd700")) # Gold
                refine_item.setFont(bold_font)
            self.table.setItem(row, 3, refine_item)
            
            self.table.setItem(row, 4, QTableWidgetItem(item["drop_chance"]))
            self.table.setItem(row, 5, QTableWidgetItem(item["best_farm"]))
