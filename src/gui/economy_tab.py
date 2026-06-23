from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from src.core.economy_engine import EconomyEngine

from src.core.app_context import AppContext

class EconomyTab(QWidget):
    """GUI tab tracking overall currency stats, target quantities, and estimated farming hours."""

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        self.engine = self.context.resource_service.ee
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_economy())
        
        self.layout = QVBoxLayout()
        self.header = QLabel("Endgame Currency & Economy Planner")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc; margin-bottom: 5px;")
        self.layout.addWidget(self.header)
        
        # Summary card
        self.summary_box = QGroupBox("Economy Progression Status")
        self.summary_layout = QVBoxLayout(self.summary_box)
        self.total_time_lbl = QLabel("Total Estimated Farming Time: -")
        self.total_time_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffb76b;")
        self.summary_layout.addWidget(self.total_time_lbl)
        self.layout.addWidget(self.summary_box)
        
        # Table view
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Currency", "Required Total", "Owned", "Deficit / Missing", "Farm Time (Hours)", "Best Farming Mission Source"
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
        self.load_economy()

    def load_economy(self) -> None:
        plan = self.engine.get_economy_plan()
        
        # Calculate overall farm hours
        total_hours = sum(p["farm_hours"] for p in plan)
        self.total_time_lbl.setText(f"Total Estimated Farming Time to Endgame: {total_hours:.1f} Hours")
        
        self.table.setRowCount(len(plan))
        bold_font = QFont()
        bold_font.setBold(True)
        
        for row, item in enumerate(plan):
            self.table.setItem(row, 0, QTableWidgetItem(item["currency"]))
            self.table.setItem(row, 1, QTableWidgetItem(f"{item['required']:,}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{item['owned']:,}"))
            
            missing = item["missing"]
            missing_item = QTableWidgetItem(f"{missing:,}" if missing > 0 else "✓ Met")
            if missing > 0:
                missing_item.setForeground(QColor("#ef4444"))
                missing_item.setFont(bold_font)
            else:
                missing_item.setForeground(QColor("#22c55e"))
            self.table.setItem(row, 3, missing_item)
            
            hours = item["farm_hours"]
            hours_item = QTableWidgetItem(f"{hours} hrs" if hours > 0 else "-")
            if hours > 0:
                hours_item.setFont(bold_font)
                hours_item.setForeground(QColor("#ffb76b"))
            self.table.setItem(row, 4, hours_item)
            
            self.table.setItem(row, 5, QTableWidgetItem(item["source"]))
network_economy = EconomyTab
