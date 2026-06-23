from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
from PySide6.QtCore import Qt
from src.core.player_loader import PlayerLoader
from src.core.achievement_engine import AchievementEngine

class AchievementsTab(QWidget):
    """GUI tab displaying player progress badges and profile achievements."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = AchievementEngine()
        
        self.layout = QVBoxLayout()
        self.header = QLabel("Account Progress Achievements")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #caa3ff; margin-bottom: 10px;")
        self.layout.addWidget(self.header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        
        self.layout.addWidget(self.scroll)
        self.setLayout(self.layout)
        self.load_achievements()

    def load_achievements(self) -> None:
        # Clear layout
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
                
        player = PlayerLoader().load_player()
        badges = self.engine.get_badges(player)
        
        unlocked_count = sum(1 for b in badges if b["unlocked"])
        summary_lbl = QLabel(f"Achievements Completed: {unlocked_count} of {len(badges)}")
        summary_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #00a3cc; margin-bottom: 8px;")
        self.scroll_layout.addWidget(summary_lbl)
        
        for b in badges:
            card = QFrame()
            
            # Formatting variables based on unlock state
            is_unlocked = b["unlocked"]
            if is_unlocked:
                border_color = "#ffd700" # Gold
                bg_color = "rgba(255, 215, 0, 0.05)"
                title_color = "#ffd700"
                icon = "🏆"
                status_txt = "UNLOCKED"
                status_style = "color: #ffd700; font-weight: bold;"
            else:
                border_color = "rgba(255, 255, 255, 0.05)"
                bg_color = "rgba(255, 255, 255, 0.01)"
                title_color = "#9fb6c8"
                icon = "🔒"
                status_txt = "LOCKED"
                status_style = "color: #9fb6c8;"
                
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 6px;
                    padding: 10px;
                    margin-bottom: 8px;
                }}
            """)
            
            card_layout = QHBoxLayout(card)
            
            # Badge icon/visual
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 24px; border: none; background: transparent;")
            card_layout.addWidget(icon_lbl)
            
            # Text information
            text_widget = QWidget()
            text_layout = QVBoxLayout(text_widget)
            text_layout.setContentsMargins(5, 0, 5, 0)
            
            name_lbl = QLabel(b["name"])
            name_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {title_color}; border: none; background: transparent;")
            text_layout.addWidget(name_lbl)
            
            desc_lbl = QLabel(b["description"])
            desc_lbl.setStyleSheet("color: #e6eef6; border: none; background: transparent;")
            desc_lbl.setWordWrap(True)
            text_layout.addWidget(desc_lbl)
            
            req_lbl = QLabel(f"Prerequisite: {b['requirement']}")
            req_lbl.setStyleSheet("font-size: 11px; color: #9fb6c8; border: none; background: transparent;")
            req_lbl.setWordWrap(True)
            text_layout.addWidget(req_lbl)
            
            card_layout.addWidget(text_widget, 1)
            
            # Status label
            status_lbl = QLabel(status_txt)
            status_lbl.setStyleSheet(status_style)
            status_lbl.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(status_lbl)
            
            self.scroll_layout.addWidget(card)
            
        self.scroll_layout.addStretch()
