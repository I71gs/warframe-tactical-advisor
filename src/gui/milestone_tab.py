from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from src.core.player_loader import PlayerLoader
from src.core.milestone_engine import MilestoneEngine

class MilestoneTab(QWidget):
    """GUI tab rendering the progression flowchart of immediate, short, mid, and long term milestones."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = MilestoneEngine()
        
        self.layout = QVBoxLayout()
        self.header = QLabel("Personalized Milestone Roadmap")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc; margin-bottom: 10px;")
        self.layout.addWidget(self.header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignHCenter)
        self.scroll.setWidget(self.scroll_content)
        
        self.layout.addWidget(self.scroll)
        self.setLayout(self.layout)
        self.load_milestones()

    def load_milestones(self) -> None:
        # Clear scroll area
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
                
        player = PlayerLoader().load_player()
        milestones = self.engine.get_milestones(player)
        
        stages = [
            ("immediate", "Immediate Milestone", milestones["immediate"]),
            ("short_term", "Short-Term target", milestones["short_term"]),
            ("mid_term", "Mid-Term Target", milestones["mid_term"]),
            ("long_term", "Long-Term Endgame Goal", milestones["long_term"])
        ]
        
        for idx, (key, title, data) in enumerate(stages):
            card = QFrame()
            card.setFixedWidth(500)
            
            # Stylize card based on completion status
            is_comp = data["completed"]
            
            # Active node is the first incomplete milestone
            is_active = False
            if not is_comp:
                # Find if any previous is incomplete
                any_prev_incomplete = False
                for prev_key, _, prev_data in stages[:idx]:
                    if not prev_data["completed"]:
                        any_prev_incomplete = True
                        break
                is_active = not any_prev_incomplete

            if is_comp:
                border_color = "#22c55e" # Green
                bg_color = "rgba(34, 197, 94, 0.05)"
                title_color = "#22c55e"
                icon = "✔"
            elif is_active:
                border_color = "#00a3cc" # Cyan
                bg_color = "rgba(0, 163, 204, 0.08)"
                title_color = "#00a3cc"
                icon = "➔"
            else:
                border_color = "rgba(255, 255, 255, 0.1)" # Muted grey
                bg_color = "rgba(255, 255, 255, 0.01)"
                title_color = "#9fb6c8"
                icon = "🔒"
                
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 2px solid {border_color};
                    border-radius: 8px;
                    padding: 12px;
                }}
            """)
            
            card_layout = QVBoxLayout(card)
            
            header_lbl = QLabel(f"{icon} {title.upper()}: {data['label']}")
            header_lbl.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {title_color}; border: none; background: transparent;")
            card_layout.addWidget(header_lbl)
            
            desc_lbl = QLabel(data["description"])
            desc_lbl.setStyleSheet("color: #e6eef6; border: none; background: transparent; margin-top: 4px;")
            desc_lbl.setWordWrap(True)
            card_layout.addWidget(desc_lbl)
            
            self.scroll_layout.addWidget(card)
            
            # Add connector arrow between steps
            if idx < len(stages) - 1:
                arrow = QLabel("▼")
                arrow.setAlignment(Qt.AlignCenter)
                arrow_color = "#00a3cc" if is_comp else "rgba(255, 255, 255, 0.2)"
                arrow.setStyleSheet(f"color: {arrow_color}; font-size: 18px; margin: 5px 0; border: none; background: transparent;")
                self.scroll_layout.addWidget(arrow)
