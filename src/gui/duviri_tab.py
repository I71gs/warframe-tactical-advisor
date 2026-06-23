from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QProgressBar, QGroupBox, QListWidget, QPushButton
from PySide6.QtCore import Qt
from src.core.duviri_engine import DuviriEngine

from src.core.app_context import AppContext

class DuviriTab(QWidget):
    """GUI tab tracking Duviri Pathos Clamps, resource counts, and checking Intrinsic levels."""

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        self.engine = self.context.resource_service.duviri_engine
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_duviri())
        
        self.spinboxes = {}
        self.layout = QHBoxLayout()
        
        # Left Panel - Intrinsics
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.header = QLabel("Duviri Intrinsics Manager")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc; margin-bottom: 5px;")
        left_layout.addWidget(self.header)
        
        # Intrinsics group
        int_group = QGroupBox("My Intrinsic Levels (Max Rank 10)")
        int_layout = QVBoxLayout(int_group)
        
        categories = ["Combat", "Riding", "Opportunity", "Endurance"]
        for cat in categories:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 4, 0, 4)
            
            lbl = QLabel(f"{cat} Intrinsic:")
            lbl.setStyleSheet("font-weight: 500;")
            row_layout.addWidget(lbl)
            
            row_layout.addStretch()
            
            sb = QSpinBox()
            sb.setRange(1, 10)
            sb.setFixedWidth(80)
            sb.setStyleSheet("background-color: #0f1724; color: #e6eef6; padding: 4px;")
            row_layout.addWidget(sb)
            self.spinboxes[cat] = sb
            
            int_layout.addWidget(row)
            
        left_layout.addWidget(int_group)
        
        # Progress Bar
        left_layout.addWidget(QLabel("Intrinsics Completion Status:"))
        self.progress_bar = QProgressBar()
        left_layout.addWidget(self.progress_bar)
        
        self.layout.addWidget(left_widget, 1)
        
        # Right Panel - Clamps and Farm Guidelines
        right_panel = QGroupBox("Pathos Clamps & Farm Suggestions")
        right_layout = QVBoxLayout(right_panel)
        
        clamp_row = QWidget()
        clamp_layout = QHBoxLayout(clamp_row)
        clamp_layout.setContentsMargins(0, 0, 0, 10)
        
        clamp_layout.addWidget(QLabel("Pathos Clamps Owned:"))
        self.clamp_spin = QSpinBox()
        self.clamp_spin.setRange(0, 99999)
        self.clamp_spin.setFixedWidth(100)
        self.clamp_spin.setStyleSheet("background-color: #0f1724; color: #e6eef6; padding: 4px;")
        clamp_layout.addWidget(self.clamp_spin)
        
        right_layout.addLayout(clamp_layout)
        
        # Guidelines list
        right_layout.addWidget(QLabel("<b>Duviri Coach Targets:</b>"))
        self.recs_list = QListWidget()
        self.recs_list.setStyleSheet("border: none; background: transparent;")
        right_layout.addWidget(self.recs_list)
        
        self.save_btn = QPushButton("Save Duviri State")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f1a24;
                border: 1px solid #00a3cc;
                border-radius: 4px;
                color: #00a3cc;
                font-weight: bold;
                padding: 8px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: rgba(0, 163, 204, 0.1);
            }
        """)
        self.save_btn.clicked.connect(self.save_state)
        right_layout.addWidget(self.save_btn)
        right_layout.addStretch()
        
        self.layout.addWidget(right_panel, 1)
        
        self.setLayout(self.layout)
        self.load_duviri()

    def load_duviri(self) -> None:
        state = self.engine.load_duviri_state()
        
        # Load Intrinsics spinboxes
        intrinsics = state.get("intrinsics", {})
        for cat, sb in self.spinboxes.items():
            sb.setValue(intrinsics.get(cat, 1))
            
        # Load Clamps spinbox
        self.clamp_spin.setValue(state.get("pathos_clamps_owned", 0))
        
        # Recalculate progress bar
        pct = self.engine.get_progress_percentage(state)
        self.progress_bar.setValue(int(pct))
        
        # Load Guidelines
        self.recs_list.clear()
        recs = self.engine.get_recommendations(state)
        for r in recs:
            self.recs_list.addItem(f"• {r}")

    def save_state(self) -> None:
        intrinsics_update = {}
        for cat, sb in self.spinboxes.items():
            intrinsics_update[cat] = sb.value()
            
        state_data = {
            "intrinsics": intrinsics_update,
            "pathos_clamps_owned": self.clamp_spin.value()
        }
        self.engine.save_duviri_state(state_data)
        self.load_duviri()
