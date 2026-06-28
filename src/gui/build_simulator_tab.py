from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QGroupBox, QFrame, QGridLayout, QProgressBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from src.core.player_loader import PlayerLoader
from src.core.build_simulator import BuildSimulator

class BuildSimulatorTab(QWidget):
    """GUI tab providing a professional weapon build planner with visual mod grids and stats."""

    def __init__(self) -> None:
        super().__init__()
        self.simulator = BuildSimulator()

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Left Column: Configuration & Status Details
        left_widget = QWidget()
        left_lay = QVBoxLayout(left_widget)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(10)

        left_lay.addWidget(QLabel("Select Target Weapon Blueprint:"))
        self.weapon_selector = QComboBox()
        self.weapon_selector.addItems(sorted(list(self.simulator.build_templates.keys())))
        self.weapon_selector.currentTextChanged.connect(self.run_simulation)
        left_lay.addWidget(self.weapon_selector)

        # Stats Card
        stats_box = QGroupBox("Physical Weapon Calculations")
        stats_box.setStyleSheet("""
            QGroupBox {
                background: #0d111d; border: 1px solid rgba(0, 240, 255, 0.2);
                border-radius: 6px; font-weight: bold; color: #00f0ff; margin-top: 8px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; }
        """)
        self.stats_lay = QVBoxLayout(stats_box)
        self.stats_lay.setSpacing(8)

        self.score_lbl = QLabel("Current Build Score: —")
        self.score_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #f0f6fc;")
        self.stats_lay.addWidget(self.score_lbl)

        self.score_bar = QProgressBar()
        self.score_bar.setStyleSheet("QProgressBar::chunk { background: #caa3ff; }")
        self.stats_lay.addWidget(self.score_bar)

        self.dps_lbl = QLabel("Estimated Sustained DPS: 0")
        self.dps_lbl.setStyleSheet("font-size: 12px; color: #ffb76b; font-weight: bold;")
        self.stats_lay.addWidget(self.dps_lbl)

        self.status_lbl = QLabel("Status Weighting: —")
        self.stats_lay.addWidget(self.status_lbl)

        self.crit_lbl = QLabel("Crit Probability: —")
        self.stats_lay.addWidget(self.crit_lbl)

        self.polarities_lbl = QLabel("Required Polarities: —")
        self.stats_lay.addWidget(self.polarities_lbl)

        left_lay.addWidget(stats_box)
        left_lay.addStretch()

        main_layout.addWidget(left_widget, 1)

        # Right Column: Visual Slots & Upgrades Layout
        right_widget = QWidget()
        right_lay = QVBoxLayout(right_widget)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(10)

        # Mod Slots Layout
        mod_box = QGroupBox("Primary & Secondary Mod Config (8 Slots)")
        mod_box.setStyleSheet(stats_box.styleSheet())
        self.mod_grid = QGridLayout(mod_box)
        self.mod_grid.setSpacing(8)
        right_lay.addWidget(mod_box, 2)

        # Arcane / Exilus Slots
        utility_box = QGroupBox("Arcane & Exilus Integration Slots")
        utility_box.setStyleSheet(stats_box.styleSheet().replace("#00f0ff", "#7fffb3"))
        self.util_grid = QGridLayout(utility_box)
        self.util_grid.setSpacing(8)
        right_lay.addWidget(utility_box, 1)

        main_layout.addWidget(right_widget, 2)
        self.setLayout(main_layout)

        self.run_simulation()

    def run_simulation(self) -> None:
        weapon = self.weapon_selector.currentText()
        if not weapon:
            return

        player = PlayerLoader().load_player()
        result = self.simulator.simulate_build(player, weapon)

        if not result:
            self.score_lbl.setText("No build details available.")
            return

        # 1. Update stats
        current_score = result.get("current_score", 50)
        potential_score = result.get("potential_score", 100)
        
        self.score_lbl.setText(f"Current Build Score: {current_score} / 100")
        self.score_bar.setValue(int(current_score))

        # Dynamic DPS & Calculations based on score
        base_dps = 2450.0
        est_dps = int(base_dps * (current_score / 100.0))
        self.dps_lbl.setText(f"Estimated Sustained DPS: {est_dps:,} (Potential: {int(base_dps):,})")
        self.status_lbl.setText(f"Status Weighting: {int(current_score * 0.4)}% (Viral / Heat Synergy)")
        self.crit_lbl.setText(f"Crit Probability: {round(current_score * 0.8, 1)}% (Tier-1 Yellow Crits)")
        self.polarities_lbl.setText(f"Catalyst Installed: Yes  |  Required Forma: {max(0, int((100 - current_score) / 10))}")

        # Clear Mod grid
        for i in reversed(range(self.mod_grid.count())):
            self.mod_grid.itemAt(i).widget().deleteLater()

        # Clear Utility grid
        for i in reversed(range(self.util_grid.count())):
            self.util_grid.itemAt(i).widget().deleteLater()

        # 2. Populate 8 Mod Slots (2 rows of 4)
        components = result.get("components", [])
        for idx in range(8):
            row = idx // 4
            col = idx % 4
            
            if idx < len(components):
                comp = components[idx]
                name = comp["name"]
                owned = comp["owned"]
                bg = "#22c55e22" if owned else "#ef444422"
                border = "#22c55e" if owned else "#ef4444"
                status_txt = "OWNED" if owned else "LOCKED"
            else:
                name = "Empty Slot"
                bg = "rgba(255,255,255,0.01)"
                border = "rgba(255,255,255,0.05)"
                status_txt = "—"

            slot_frame = QFrame()
            slot_frame.setStyleSheet(f"""
                QFrame {{
                    background: {bg}; border: 1px solid {border};
                    border-radius: 6px; padding: 4px;
                }}
            """)
            slot_lay = QVBoxLayout(slot_frame)
            
            lbl_name = QLabel(name)
            lbl_name.setWordWrap(True)
            lbl_name.setAlignment(Qt.AlignCenter)
            lbl_name.setStyleSheet("font-size: 10px; font-weight: bold; border: none; background: transparent;")
            slot_lay.addWidget(lbl_name)

            lbl_status = QLabel(status_txt)
            lbl_status.setAlignment(Qt.AlignCenter)
            lbl_status.setStyleSheet("font-size: 9px; font-weight: 500; border: none; background: transparent; color: #8b949e;")
            slot_lay.addWidget(lbl_status)

            self.mod_grid.addWidget(slot_frame, row, col)

        # 3. Populate Arcane & Exilus slots (1 row of 3)
        util_names = ["Arcane Slot 1", "Arcane Slot 2", "Exilus Utility"]
        util_colors = ["#7fffb3", "#7fffb3", "#00f0ff"]
        for idx in range(3):
            # Pick a placeholder/arcane status
            slot_name = util_names[idx]
            color = util_colors[idx]
            
            slot_frame = QFrame()
            slot_frame.setStyleSheet(f"""
                QFrame {{
                    background: {color}11; border: 1px dashed {color}66;
                    border-radius: 6px; padding: 4px;
                }}
            """)
            slot_lay = QVBoxLayout(slot_frame)

            lbl_name = QLabel(slot_name)
            lbl_name.setAlignment(Qt.AlignCenter)
            lbl_name.setStyleSheet("font-size: 10px; font-weight: bold; border: none; background: transparent;")
            slot_lay.addWidget(lbl_name)

            lbl_status = QLabel("INTEGRATED")
            lbl_status.setAlignment(Qt.AlignCenter)
            lbl_status.setStyleSheet(f"font-size: 9px; border: none; background: transparent; color: {color};")
            slot_lay.addWidget(lbl_status)

            self.util_grid.addWidget(slot_frame, 0, idx)
