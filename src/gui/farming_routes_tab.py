from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QGroupBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from src.core.player_loader import PlayerLoader
from src.core.farm_efficiency_engine import FarmEfficiencyEngine

class FarmingRoutesTab(QWidget):
    """GUI tab rendering farming paths sorted by priority, displaying efficiency stats and numbered steps."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = FarmEfficiencyEngine()
        
        self.layout = QVBoxLayout()
        self.header = QLabel("Optimized Farming Sequences & Routes")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc; margin-bottom: 10px;")
        self.layout.addWidget(self.header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        
        self.layout.addWidget(self.scroll)
        self.setLayout(self.layout)
        self.load_routes()

    def load_routes(self) -> None:
        # Clear scroll layout
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
                
        player = PlayerLoader().load_player()
        routes = self.engine.get_routes(player)
        
        for r in routes:
            card = QGroupBox(r["name"])
            card_layout = QVBoxLayout(card)
            
            # Subheader displaying stats
            stats_layout = QHBoxLayout()
            
            priority = r["priority"]
            if priority == "CRITICAL":
                priority_style = "color: #ef4444; font-weight: bold;"
            elif priority == "HIGH":
                priority_style = "color: #ffb76b; font-weight: bold;"
            elif priority == "MEDIUM":
                priority_style = "color: #caa3ff;"
            elif priority == "LOW":
                priority_style = "color: #9fb6c8;"
            else: # COMPLETED
                priority_style = "color: #22c55e; font-weight: 500;"
                
            priority_lbl = QLabel(f"Priority: {priority}")
            priority_lbl.setStyleSheet(priority_style)
            stats_layout.addWidget(priority_lbl)
            
            stats_layout.addWidget(QLabel("|"))
            
            eff_lbl = QLabel(f"Efficiency: {r['efficiency']}")
            eff_lbl.setStyleSheet("color: #caa3ff; font-weight: bold;")
            stats_layout.addWidget(eff_lbl)
            
            stats_layout.addWidget(QLabel("|"))
            
            dur_lbl = QLabel(f"Est. Duration: {r['duration']}")
            dur_lbl.setStyleSheet("color: #e6eef6;")
            stats_layout.addWidget(dur_lbl)
            
            stats_layout.addStretch()
            
            # Active badge
            if r["active"]:
                active_lbl = QLabel("🔥 RECOMMENDED ACTIVE ROUTE")
                active_lbl.setStyleSheet("color: #00a3cc; font-weight: bold; background: rgba(0, 163, 204, 0.1); padding: 2px 6px; border-radius: 4px;")
                stats_layout.addWidget(active_lbl)
                
            card_layout.addLayout(stats_layout)
            
            # Steps list
            steps_frame = QFrame()
            steps_frame.setStyleSheet("background: rgba(0, 0, 0, 0.15); border-radius: 4px; padding: 6px; margin-top: 5px;")
            steps_layout = QVBoxLayout(steps_frame)
            
            for idx, step in enumerate(r["steps"]):
                step_lbl = QLabel(f"{idx+1}. {step}")
                step_lbl.setWordWrap(True)
                step_lbl.setStyleSheet("color: #e6eef6; line-height: 15px; background: transparent;")
                steps_layout.addWidget(step_lbl)
                
            card_layout.addWidget(steps_frame)
            
            # Dynamic card background border based on status
            border_color = "rgba(0, 163, 204, 0.4)" if r["active"] else ("rgba(34, 197, 94, 0.3)" if priority == "COMPLETED" else "rgba(255, 255, 255, 0.05)")
            card.setStyleSheet(f"""
                QGroupBox {{
                    border: 1px solid {border_color};
                    border-radius: 6px;
                    margin-top: 10px;
                    padding-top: 15px;
                    font-weight: bold;
                    font-size: 13px;
                }}
            """)
            
            self.scroll_layout.addWidget(card)
            
        self.scroll_layout.addStretch()
