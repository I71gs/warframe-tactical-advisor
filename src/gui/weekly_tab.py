from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QProgressBar
from PySide6.QtGui import QColor
from src.core.player_loader import PlayerLoader
from src.core.weekly_planner import WeeklyPlanner

class WeeklyTab(QWidget):
    """GUI tab showing weekly milestones, completion percentages, and dynamic status checks."""

    def __init__(self) -> None:
        super().__init__()
        self.planner = WeeklyPlanner()
        
        self.layout = QVBoxLayout()
        self.header = QLabel("Weekly Progression Planner")
        self.header.setStyleSheet("font-size: 14px; font-weight: bold; color: #caa3ff;")
        self.layout.addWidget(self.header)
        
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        
        self.progress_label = QLabel("Weekly Progress: 0%")
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_label)
        self.layout.addWidget(self.progress_bar)
        
        self.setLayout(self.layout)
        self.load_weekly()

    def load_weekly(self) -> None:
        self.list_widget.clear()
        player = PlayerLoader().load_player()
        state = self.planner.get_weekly_state(player)
        
        total = len(state["goals"])
        completed = sum(1 for g in state["goals"] if g["completed"])
        pct = int(completed / total * 100) if total > 0 else 0
        
        for g in state["goals"]:
            status_symbol = "✔ (Done)" if g["completed"] else "☐ (Incomplete)"
            item_text = f"  {g['text']} — {status_symbol}"
            item = QListWidgetItem(item_text)
            
            if g["completed"]:
                item.setForeground(QColor("#22c55e")) # Green
            else:
                item.setForeground(QColor("#ffb76b")) # Orange
                
            self.list_widget.addItem(item)
            
        self.progress_label.setText(f"Weekly Progress: {pct}% ({completed}/{total} goals met)")
        self.progress_bar.setValue(pct)
