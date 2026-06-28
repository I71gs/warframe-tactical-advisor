from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QComboBox, QPushButton,
    QProgressBar, QScrollArea, QFrame, QGridLayout
)
from src.core.economy_engine import EconomyEngine, GOAL_RESOURCE_REQUIREMENTS
from src.core.app_context import AppContext

class EconomyTab(QWidget):
    """GUI tab tracking overall resource stats, targets, deficits, farming times, and booster recommendations."""

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        self.engine = EconomyEngine()
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_economy())

        root = QVBoxLayout(self)
        root.setSpacing(10)

        # Header
        header = QLabel("💎  Endgame Economy & Resource Planner")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff9fd4; margin-bottom: 2px;")
        root.addWidget(header)

        # Upper Layout: Goal Planner and Recommendations
        upper_layout = QHBoxLayout()

        # Goal Planner Group
        goal_box = QGroupBox("Target Crafting Goal")
        goal_box.setStyleSheet("""
            QGroupBox {
                background: #0d1117; border: 1px solid #ff9fd444;
                border-radius: 6px; font-weight: bold; color: #ff9fd4; margin-top: 8px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; }
        """)
        goal_lay = QVBoxLayout(goal_box)
        
        goal_sel_lay = QHBoxLayout()
        goal_sel_lay.addWidget(QLabel("Select Target Item:"))
        self.goal_combo = QComboBox()
        self.goal_combo.addItems([g.upper() for g in GOAL_RESOURCE_REQUIREMENTS.keys()])
        goal_sel_lay.addWidget(self.goal_combo)
        
        calc_btn = QPushButton("Calculate Blueprint Costs")
        calc_btn.setStyleSheet("""
            QPushButton {
                background: #0f1a24; border: 1px solid #ff9fd4;
                border-radius: 4px; color: #ff9fd4; font-weight: bold; padding: 5px 12px;
            }
            QPushButton:hover { background: rgba(255,159,212,0.1); }
        """)
        calc_btn.clicked.connect(self._run_goal_calc)
        goal_sel_lay.addWidget(calc_btn)
        goal_lay.addLayout(goal_sel_lay)

        self.goal_summary_lbl = QLabel("Select a goal above to compute missing resources.")
        self.goal_summary_lbl.setWordWrap(True)
        self.goal_summary_lbl.setStyleSheet("color: #7a8fa6; font-size: 11px;")
        goal_lay.addWidget(self.goal_summary_lbl)
        upper_layout.addWidget(goal_box, 1)

        # Booster Advice Group
        booster_box = QGroupBox("Booster Optimization Strategy")
        booster_box.setStyleSheet(goal_box.styleSheet().replace("#ff9fd4", "#7fffb3"))
        booster_lay = QVBoxLayout(booster_box)
        
        self.booster_info = QLabel("No active resource bottlenecks detected. Keep farming, Tenno!")
        self.booster_info.setWordWrap(True)
        self.booster_info.setStyleSheet("color: #7fffb3; font-size: 11px; font-weight: 500;")
        booster_lay.addWidget(self.booster_info)
        upper_layout.addWidget(booster_box, 1)

        root.addLayout(upper_layout)

        # Overview Progress Box
        self.summary_box = QGroupBox("Overall Economy Deficit Status")
        self.summary_box.setStyleSheet(goal_box.styleSheet().replace("#ff9fd4", "#00a3cc"))
        self.summary_layout = QVBoxLayout(self.summary_box)
        self.total_time_lbl = QLabel("Total Estimated Farming Time: -")
        self.total_time_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffb76b;")
        self.summary_layout.addWidget(self.total_time_lbl)
        root.addWidget(self.summary_box)

        # Table view
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Resource", "Required Target", "Current Owned", "Missing Deficit", "Farm Time (Hrs)", "Recommended Farm Node / Source"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0d1117;
                alternate-background-color: #12181f;
                gridline-color: #1e2a38;
                color: #c8d6e5;
                border: 1px solid #1e2a38;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #0f1a24;
                color: #ff9fd4;
                padding: 4px;
                border: none;
                font-weight: bold;
            }
        """)
        root.addWidget(self.table)

        self.setLayout(root)
        QTimer.singleShot(0, self.load_economy)

    def load_economy(self) -> None:
        plan = self.engine.get_economy_plan()
        
        # Calculate overall farm hours
        total_hours = sum(p["farm_hours"] for p in plan)
        self.total_time_lbl.setText(f"Total Estimated Farming Time to reach Target Goals: {total_hours:.1f} Hours")
        
        self.table.setRowCount(len(plan))
        bold_font = QFont()
        bold_font.setBold(True)
        
        missing_resources = []
        for row, item in enumerate(plan):
            res_name = item["resource"]
            self.table.setItem(row, 0, QTableWidgetItem(res_name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{item['required']:,}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{item['owned']:,}"))
            
            missing = item["missing"]
            missing_item = QTableWidgetItem(f"{missing:,}" if missing > 0 else "✓ Completed")
            if missing > 0:
                missing_item.setForeground(QColor("#ef4444"))
                missing_item.setFont(bold_font)
                missing_resources.append(res_name)
            else:
                missing_item.setForeground(QColor("#22c55e"))
            self.table.setItem(row, 3, missing_item)
            
            hours = item["farm_hours"]
            hours_item = QTableWidgetItem(f"{hours:.2f} hrs" if hours > 0 else "-")
            if hours > 0:
                hours_item.setFont(bold_font)
                hours_item.setForeground(QColor("#ffb76b"))
            self.table.setItem(row, 4, hours_item)
            
            self.table.setItem(row, 5, QTableWidgetItem(item["best_node"] or item["notes"]))

        # Update Booster Panel
        if missing_resources:
            boosters = self.engine.recommend_boosters(missing_resources)
            self.booster_info.setText("Recommended Boosters:\n• " + "\n• ".join(boosters))
        else:
            self.booster_info.setText("All resource targets successfully met! No boosters required.")

    def _run_goal_calc(self) -> None:
        goal = self.goal_combo.currentText().lower()
        res = self.engine.get_resource_farm_plan(goal)
        if not res["found"]:
            self.goal_summary_lbl.setText(res.get("message", "Error calculating."))
            return

        lines = [
            f"Farming Plan for {goal.upper()}:",
            f"  Total Estimated Farming Time: {res['total_farm_hours']} hours",
            "",
            "Deficit Breakdown:"
        ]
        for item in res["resources"]:
            miss = item["missing"]
            status = f"Need {miss:,}" if miss > 0 else "✓ Met"
            lines.append(f"  • {item['resource']}: {status} (Best: {item['best_node']})")
        
        self.goal_summary_lbl.setText("\n".join(lines))

# Alias mapping
network_economy = EconomyTab
