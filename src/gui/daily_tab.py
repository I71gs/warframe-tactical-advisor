from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QProgressBar
from src.core.player_loader import PlayerLoader
from src.core.daily_objectives_engine import DailyObjectivesEngine

class DailyTab(QWidget):
    """GUI tab providing a checkable list of daily progress goals persisted offline."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = DailyObjectivesEngine()
        self.checkboxes = []
        
        self.layout = QVBoxLayout()
        self.header = QLabel("Today's Progression Plan")
        self.header.setStyleSheet("font-size: 14px; font-weight: bold; color: #00a3cc;")
        self.layout.addWidget(self.header)
        
        self.checkbox_container = QWidget()
        self.checkbox_layout = QVBoxLayout()
        self.checkbox_container.setLayout(self.checkbox_layout)
        self.layout.addWidget(self.checkbox_container)
        
        self.progress_label = QLabel("Daily Completion: 0%")
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_label)
        self.layout.addWidget(self.progress_bar)
        
        self.setLayout(self.layout)
        self.load_daily()

    def load_daily(self) -> None:
        # Clear previous checkbox widgets
        self.checkboxes.clear()
        for i in reversed(range(self.checkbox_layout.count())):
            w = self.checkbox_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
                
        player = PlayerLoader().load_player()
        self.state = self.engine.get_daily_objectives(player)
        
        for idx, obj in enumerate(self.state["objectives"]):
            cb = QCheckBox(obj["text"])
            cb.setChecked(obj["completed"])
            cb.stateChanged.connect(lambda state, index=idx: self.on_check_toggled(index, state))
            self.checkbox_layout.addWidget(cb)
            self.checkboxes.append(cb)
            
        self.update_progress_ui()

    def on_check_toggled(self, index: int, state: int) -> None:
        self.state["objectives"][index]["completed"] = (state == 2) # Qt.Checked is 2
        self.engine.save_daily_state(self.state)
        self.update_progress_ui()

    def update_progress_ui(self) -> None:
        total = len(self.state["objectives"])
        completed = sum(1 for obj in self.state["objectives"] if obj["completed"])
        pct = int(completed / total * 100) if total > 0 else 0
        
        self.progress_label.setText(f"Daily Completion: {pct}% ({completed}/{total} tasks complete)")
        self.progress_bar.setValue(pct)
