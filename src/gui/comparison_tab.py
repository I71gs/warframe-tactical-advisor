from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QGroupBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import math

from src.core.save_manager import SaveManager
from src.core.comparison_engine import ComparisonEngine

class ComparisonTab(QWidget):
    """GUI tab rendering side-by-side profile metrics, radar charts, and difference tables."""

    def __init__(self) -> None:
        super().__init__()
        self.sm = SaveManager()
        self.engine = ComparisonEngine()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Title
        self.header = QLabel("⚔️  Multi-Profile Account Comparison")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #caa3ff;")
        self.layout.addWidget(self.header)

        # Profile Selectors
        sel_layout = QHBoxLayout()
        sel_layout.addWidget(QLabel("Profile 1 (Baseline):"))
        self.prof1_combo = QComboBox()
        sel_layout.addWidget(self.prof1_combo)

        sel_layout.addWidget(QLabel("Profile 2 (Comparison):"))
        self.prof2_combo = QComboBox()
        sel_layout.addWidget(self.prof2_combo)

        self.compare_btn = QPushButton("Compare Accounts")
        self.compare_btn.setStyleSheet("""
            QPushButton {
                background: #0f1a24; border: 1px solid #caa3ff;
                border-radius: 4px; color: #caa3ff; font-weight: bold; padding: 5px 12px;
            }
            QPushButton:hover { background: rgba(202,163,255,0.1); }
        """)
        self.compare_btn.clicked.connect(self.run_comparison)
        sel_layout.addWidget(self.compare_btn)
        self.layout.addLayout(sel_layout)

        # Splitter to divide graphics and details
        splitter = QSplitter(Qt.Horizontal)

        # Left Column: Radar Chart + Badges
        left_panel = QWidget()
        left_lay = QVBoxLayout(left_panel)
        left_lay.setContentsMargins(0, 0, 0, 0)

        # Radar canvas container
        self.chart_container = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_container)
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        left_lay.addWidget(self.chart_container)

        # Recommendation box
        self.rec_box = QGroupBox("Strategic Advisor Action Plan")
        self.rec_box.setStyleSheet("""
            QGroupBox {
                background: #0d1117; border: 1px solid #7fffb344;
                border-radius: 6px; font-weight: bold; color: #7fffb3; margin-top: 8px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; }
        """)
        rec_lay = QVBoxLayout(self.rec_box)
        self.rec_text = QLabel("Select profiles and click 'Compare Accounts'.")
        self.rec_text.setWordWrap(True)
        self.rec_text.setStyleSheet("color: #c8d6e5; font-size: 11px; font-weight: 500;")
        rec_lay.addWidget(self.rec_text)
        left_lay.addWidget(self.rec_box)

        splitter.addWidget(left_panel)

        # Right Column: Comparison text output + resource difference table
        right_panel = QWidget()
        right_lay = QVBoxLayout(right_panel)
        right_lay.setContentsMargins(0, 0, 0, 0)

        self.results_box = QTextEdit()
        self.results_box.setReadOnly(True)
        self.results_box.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                border: 1px solid #1e2a38;
                color: #c8d6e5;
                font-family: Consolas, monospace;
                font-size: 11px;
                padding: 6px;
            }
        """)
        right_lay.addWidget(self.results_box)

        self.res_table = QTableWidget()
        self.res_table.setColumnCount(4)
        self.res_table.setHorizontalHeaderLabels(["Resource", "Profile 1 Qty", "Profile 2 Qty", "Difference"])
        self.res_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.res_table.verticalHeader().setVisible(False)
        self.res_table.setStyleSheet("""
            QTableWidget {
                background-color: #0d1117;
                alternate-background-color: #12181f;
                gridline-color: #1e2a38;
                color: #c8d6e5;
                border: 1px solid #1e2a38;
            }
            QHeaderView::section {
                background-color: #0f1a24;
                color: #caa3ff;
                font-weight: bold;
                border: none;
            }
        """)
        right_lay.addWidget(self.res_table)

        splitter.addWidget(right_panel)
        self.layout.addWidget(splitter)

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

        # Clear canvas
        for i in reversed(range(self.chart_layout.count())):
            w = self.chart_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

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

            # Update Recommendation
            self.rec_text.setText(report.get("overall_recommendation", ""))

            # Draw Radar Comparison Chart
            fig = self._draw_radar_comparison(p1, p2, report["dimensions"])
            canvas = FigureCanvas(fig)
            self.chart_layout.addWidget(canvas)

        except Exception as e:
            self.results_box.setText(f"Comparison failed: {e}")

    def _draw_radar_comparison(self, name1: str, name2: str, dims: dict) -> Figure:
        categories = list(dims.keys())
        N = len(categories)
        
        values1 = [dims[c]["p1"] for c in categories]
        values2 = [dims[c]["p2"] for c in categories]

        # Close the loop
        values1 += values1[:1]
        values2 += values2[:1]
        angles = [n / float(N) * 2 * math.pi for n in range(N)]
        angles += angles[:1]

        fig = Figure(facecolor='#0b1220')
        ax = fig.add_subplot(111, polar=True)
        ax.set_facecolor('#0f1724')
        ax.set_theta_offset(math.pi / 2)
        ax.set_theta_direction(-1)

        ax.set_rgrids([20, 40, 60, 80, 100], color='#2a384e')
        ax.set_thetagrids([n / float(N) * 360 for n in range(N)], categories, color='#e6eef6', fontsize=8)

        # Plot Profile 1
        ax.plot(angles, values1, color='#caa3ff', linewidth=2, label=name1)
        ax.fill(angles, values1, color='#caa3ff', alpha=0.15)

        # Plot Profile 2
        ax.plot(angles, values2, color='#00a3cc', linewidth=2, label=name2)
        ax.fill(angles, values2, color='#00a3cc', alpha=0.15)

        ax.set_ylim(0, 100)
        ax.tick_params(colors='#9fb6c8', grid_color='#2a384e')
        ax.spines['polar'].set_color('#2a384e')
        
        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.2), facecolor='#0b1220', edgecolor='#2a384e', labelcolor='#e6eef6')
        return fig
