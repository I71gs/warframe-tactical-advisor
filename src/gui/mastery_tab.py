from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QGroupBox, QGridLayout, QFrame
from PySide6.QtCore import Qt
from src.core.player_loader import PlayerLoader
from src.core.mastery_planner import MasteryPlanner
from src.core.app_context import AppContext
from src.gui.widgets.custom_charts import CircularProgress

class MasteryTab(QWidget):
    """GUI tab visualizing Mastery Rank XP deficits and prioritizing optimal leveling routes."""

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        self.planner = self.context.resource_service.mastery_planner
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_planner())
        
        self.layout = QVBoxLayout()
        self.header = QLabel("Mastery Rank Progression Planner")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc; margin-bottom: 5px;")
        self.layout.addWidget(self.header)
        
        # Summary Box
        self.summary_box = QGroupBox("Mastery Progress Summary")
        self.summary_layout = QHBoxLayout(self.summary_box)
        
        info_panel = QFrame()
        info_panel.setStyleSheet("border: none; background: transparent;")
        info_grid = QGridLayout(info_panel)
        info_grid.setContentsMargins(0, 0, 0, 0)
        
        self.mr_lbl = QLabel("Current Mastery Rank: -")
        self.mr_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #e6eef6;")
        self.next_lbl = QLabel("Next Rank Target: -")
        self.next_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #caa3ff;")
        
        self.xp_lbl = QLabel("XP Needed for Next Rank: -")
        self.xp_lbl.setStyleSheet("color: #ffb76b; font-weight: 500;")
        self.eta_lbl = QLabel("Estimated Timeframe: -")
        self.eta_lbl.setStyleSheet("color: #22c55e; font-weight: bold;")
        
        info_grid.addWidget(self.mr_lbl, 0, 0)
        info_grid.addWidget(self.next_lbl, 0, 1)
        info_grid.addWidget(self.xp_lbl, 1, 0)
        info_grid.addWidget(self.eta_lbl, 1, 1)
        
        self.summary_layout.addWidget(info_panel, 1)
        
        # Add Circular Progress for MR 30 completion
        self.mr_progress = CircularProgress(self, color="#caa3ff", min_size=90, subtitle="To MR 30")
        self.summary_layout.addWidget(self.mr_progress)
        
        self.layout.addWidget(self.summary_box)
        
        # Split List Layout
        lists_layout = QHBoxLayout()
        
        # Weapons List
        weap_box = QGroupBox("Recommended Weapons to Level (+3,000 XP)")
        weap_layout = QVBoxLayout(weap_box)
        self.weap_list = QListWidget()
        weap_layout.addWidget(self.weap_list)
        lists_layout.addWidget(weap_box)
        
        # Warframes List
        frame_box = QGroupBox("Recommended Warframes to Level (+6,000 XP)")
        frame_layout = QVBoxLayout(frame_box)
        self.frame_list = QListWidget()
        frame_layout.addWidget(self.frame_list)
        lists_layout.addWidget(frame_box)
        
        self.layout.addLayout(lists_layout)
        self.setLayout(self.layout)
        self.load_planner()

    def load_planner(self) -> None:
        player = PlayerLoader().load_player()
        res = self.planner.calculate_plan(player)
        
        # Update summary values
        self.mr_lbl.setText(f"Current Mastery Rank: {res['current_mr']}")
        self.next_lbl.setText(f"Next Rank Target: MR {res['next_mr']}")
        self.xp_lbl.setText(f"XP Needed for Next Rank: {res['xp_needed']:,} XP")
        self.eta_lbl.setText(f"Estimated Timeframe: {res['days_estimate']}")
        
        # Set MR circle value and text label
        self.mr_progress.label = f"MR {res['current_mr']}"
        self.mr_progress.set_value(res['current_mr'] / 30.0 * 100)
        
        # Populate Weapons List
        self.weap_list.clear()
        for w in res["weapons_to_level"]:
            text = f"• {w['name']} ({w['category']})\n  Source: {w['source']}"
            self.weap_list.addItem(QListWidgetItem(text))
            
        # Populate Warframes List
        self.frame_list.clear()
        for f in res["frames_to_build"]:
            text = f"• {f['name']} Warframe\n  Source: {f['source']}"
            self.frame_list.addItem(QListWidgetItem(text))
