from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from src.core.save_manager import SaveManager
from src.core.comparison_engine import ComparisonEngine

class ComparisonTab(QWidget):
    """GUI tab rendering side-by-side profile metrics and missing collections checklist."""

    def __init__(self) -> None:
        super().__init__()
        self.sm = SaveManager()
        self.engine = ComparisonEngine()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)

        # Title
        self.header = QLabel("Multi-Profile Account Comparison")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #caa3ff;")
        self.layout.addWidget(self.header)

        # Profile Selectors
        sel_layout = QHBoxLayout()
        sel_layout.addWidget(QLabel("Profile 1:"))
        self.prof1_combo = QComboBox()
        sel_layout.addWidget(self.prof1_combo)

        sel_layout.addWidget(QLabel("Profile 2:"))
        self.prof2_combo = QComboBox()
        sel_layout.addWidget(self.prof2_combo)

        self.compare_btn = QPushButton("Compare Accounts")
        self.compare_btn.clicked.connect(self.run_comparison)
        sel_layout.addWidget(self.compare_btn)
        
        self.layout.addLayout(sel_layout)

        # Output Results Text Box
        self.results_box = QTextEdit()
        self.results_box.setReadOnly(True)
        self.results_box.setStyleSheet("""
            QTextEdit {
                background-color: #0f1724;
                border: 1px solid rgba(255,255,255,0.05);
                color: #e6eef6;
                font-family: Consolas, monospace;
                font-size: 12px;
                padding: 8px;
            }
        """)
        self.layout.addWidget(self.results_box)

        # Table of resource differentials
        self.res_table = QTableWidget()
        self.res_table.setColumnCount(4)
        self.res_table.setHorizontalHeaderLabels(["Resource", "Profile 1 Qty", "Profile 2 Qty", "Difference"])
        self.res_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.res_table.setStyleSheet("""
            QTableWidget {
                background-color: #0f1724;
                border: 1px solid rgba(255, 255, 255, 0.05);
                color: #e6eef6;
            }
        """)
        self.layout.addWidget(self.res_table)

        self.setLayout(self.layout)
        self.populate_dropdowns()

    def populate_dropdowns(self) -> None:
        profiles = self.sm.list_profiles()
        self.prof1_combo.clear()
        self.prof2_combo.clear()
        self.prof1_combo.addItems(profiles)
        self.prof2_combo.addItems(profiles)
        if len(profiles) > 1:
            self.prof2_combo.setCurrentIndex(1)

    def run_comparison(self) -> None:
        p1 = self.prof1_combo.currentText()
        p2 = self.prof2_combo.currentText()
        if not p1 or not p2:
            self.results_box.setText("Please select two profiles to compare.")
            return

        try:
            report = self.engine.compare_profiles(p1, p2)
            
            # Formulate text output
            diffs = report["differentials"]
            text = []
            text.append("=" * 60)
            text.append(f"  ACCOUNT COMPARISON REPORT: {p1} vs {p2}")
            text.append("=" * 60)
            text.append(f"{p1}: Mastery Rank {report['profile1']['mastery']} | Readiness Score: {report['profile1']['readiness']}%")
            text.append(f"{p2}: Mastery Rank {report['profile2']['mastery']} | Readiness Score: {report['profile2']['readiness']}%")
            text.append("-" * 60)
            text.append(f"Mastery Differential: {diffs['mastery_diff']:+d}")
            text.append(f"Readiness Differential: {diffs['readiness_diff']:+.1f}%")
            text.append(f"Rankings Order: 1st: {report['strength_rankings'][0]} | 2nd: {report['strength_rankings'][1]}")
            text.append("-" * 60)
            
            # Items only in Profile 2 compared to Profile 1
            text.append(f"Missing items in {p1} (Completed only in {p2}):")
            text.append(f"  Quests:  {', '.join(diffs['quests_p2_only']) or 'None'}")
            text.append(f"  Mods:    {', '.join(diffs['mods_p2_only']) or 'None'}")
            text.append(f"  Arcanes: {', '.join(diffs['arcanes_p2_only']) or 'None'}")
            text.append(f"  Weapons: {', '.join(diffs['weapons_p2_only']) or 'None'}")
            text.append("-" * 60)
            
            # Items only in Profile 1 compared to Profile 2
            text.append(f"Missing items in {p2} (Completed only in {p1}):")
            text.append(f"  Quests:  {', '.join(diffs['quests_p1_only']) or 'None'}")
            text.append(f"  Mods:    {', '.join(diffs['mods_p1_only']) or 'None'}")
            text.append(f"  Arcanes: {', '.join(diffs['arcanes_p1_only']) or 'None'}")
            text.append(f"  Weapons: {', '.join(diffs['weapons_p1_only']) or 'None'}")
            text.append("=" * 60)

            self.results_box.setText("\n".join(text))

            # Populate table of resources
            res = report["resources"]
            self.res_table.setRowCount(len(res))
            for idx, (res_name, data) in enumerate(res.items()):
                self.res_table.setItem(idx, 0, QTableWidgetItem(res_name))
                self.res_table.setItem(idx, 1, QTableWidgetItem(str(data["p1_qty"])))
                self.res_table.setItem(idx, 2, QTableWidgetItem(str(data["p2_qty"])))
                
                diff_val = data["diff"]
                diff_item = QTableWidgetItem(f"{diff_val:+d}")
                if diff_val > 0:
                    diff_item.setForeground(Qt.green)
                elif diff_val < 0:
                    diff_item.setForeground(Qt.red)
                self.res_table.setItem(idx, 3, diff_item)

        except Exception as e:
            self.results_box.setText(f"Comparison failed: {e}")
