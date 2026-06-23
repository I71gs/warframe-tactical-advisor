from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QGroupBox, QProgressBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from src.core.player_loader import PlayerLoader
from src.core.circuit_engine import CircuitEngine

from src.core.app_context import AppContext

class CircuitTab(QWidget):
    """GUI tab providing weekly Steel Path Circuit rotations and inventory preparation audits."""

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        self.engine = self.context.resource_service.circuit_engine
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_circuit())
        
        self.layout = QVBoxLayout()
        self.header = QLabel("Steel Path Circuit Planner")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc; margin-bottom: 5px;")
        self.layout.addWidget(self.header)
        
        # Horizontal Split Panel
        split_layout = QHBoxLayout()
        
        # Left Panel - Rotation
        rot_box = QGroupBox("Weekly Rotation Rewards")
        rot_layout = QVBoxLayout(rot_box)
        
        self.week_lbl = QLabel("Week -")
        self.week_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #caa3ff;")
        rot_layout.addWidget(self.week_lbl)
        
        self.rot_list = QListWidget()
        rot_layout.addWidget(self.rot_list)
        
        self.rec_lbl = QLabel("Coach Pick: -")
        self.rec_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #ffb76b; margin-top: 8px;")
        rot_layout.addWidget(self.rec_lbl)
        
        split_layout.addWidget(rot_box, 1)
        
        # Right Panel - Readiness
        readiness_box = QGroupBox("SP Circuit Combat Readiness")
        readiness_layout = QVBoxLayout(readiness_box)
        
        self.ready_status_lbl = QLabel("Readiness: -")
        self.ready_status_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        readiness_layout.addWidget(self.ready_status_lbl)
        
        self.ready_bar = QProgressBar()
        readiness_layout.addWidget(self.ready_bar)
        
        # Recommendation details list
        readiness_layout.addWidget(QLabel("<b>Preparation Checklist:</b>"))
        self.prep_list = QListWidget()
        self.prep_list.setStyleSheet("border: none; background: transparent;")
        readiness_layout.addWidget(self.prep_list)
        
        split_layout.addWidget(readiness_box, 1)
        
        self.layout.addLayout(split_layout)
        self.setLayout(self.layout)
        self.load_circuit()

    def load_circuit(self) -> None:
        player = PlayerLoader().load_player()
        res = self.engine.get_circuit_recommendation(player)
        
        # Update weekly rotation UI
        self.week_lbl.setText(res["week"])
        self.rot_list.clear()
        
        bold_font = QFont()
        bold_font.setBold(True)
        
        for item in res["rotation_items"]:
            list_item = QListWidgetItem(f"  • {item}")
            if item == res["recommended_pick"]:
                list_item.setForeground(QColor("#00a3cc"))
                list_item.setFont(bold_font)
                list_item.setText(f"  ★ {item} (RECOMMENDED)")
            self.rot_list.addItem(list_item)
            
        self.rec_lbl.setText(f"Coach Pick: {res['recommended_pick']} (Priority: {res['priority']})")
        
        # Update readiness UI
        self.ready_status_lbl.setText(f"Readiness Status: {res['readiness_status']}")
        self.ready_bar.setValue(int(res["readiness_score"]))
        
        # Populate preparation checklist
        self.prep_list.clear()
        if not player.steel_path_unlocked:
            self.prep_list.addItem("• Unlock Steel Path difficulty from Teshin.")
            self.prep_list.addItem("• Clear remaining nodes on normal Star Chart.")
        else:
            self.prep_list.addItem("• Upgrade primary build scores to 90% (mitigates random loadout penalty).")
            self.prep_list.addItem("• Level multiple frames to rank 30 to unlock wider options.")
            self.prep_list.addItem("• Buy duplicate mods to support secondary config slots.")
