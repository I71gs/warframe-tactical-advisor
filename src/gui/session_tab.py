from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QProgressBar
from src.core.session_engine import SessionEngine

from src.core.app_context import AppContext

class SessionTab(QWidget):
    """GUI tab providing interactive customized checklists for game sessions of varying lengths."""

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        self.engine = self.context.resource_service.session_engine
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_session())
        
        self.checkboxes = []
        self.current_itinerary = []

        self.layout = QVBoxLayout()
        
        # Header layout
        header_layout = QHBoxLayout()
        self.header = QLabel("Personalized Session Planner")
        self.header.setStyleSheet("font-size: 14px; font-weight: bold; color: #00a3cc;")
        header_layout.addWidget(self.header)
        
        header_layout.addStretch()
        
        # Duration selector
        duration_label = QLabel("Session Duration:")
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["30 Minutes", "1 Hour", "2 Hours"])
        self.duration_combo.currentIndexChanged.connect(self.load_session)
        
        header_layout.addWidget(duration_label)
        header_layout.addWidget(self.duration_combo)
        self.layout.addLayout(header_layout)
        
        # Checkbox container for activities
        self.checkbox_container = QWidget()
        self.checkbox_layout = QVBoxLayout()
        self.checkbox_container.setLayout(self.checkbox_layout)
        self.layout.addWidget(self.checkbox_container)
        
        self.layout.addStretch()
        
        # Progress Tracking
        self.progress_label = QLabel("Session Progress: 0%")
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_label)
        self.layout.addWidget(self.progress_bar)
        
        self.setLayout(self.layout)
        self.load_session()

    def load_session(self) -> None:
        # Clear previous widgets
        self.checkboxes.clear()
        for i in reversed(range(self.checkbox_layout.count())):
            w = self.checkbox_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
                
        # Parse selected duration
        txt = self.duration_combo.currentText()
        if "30" in txt:
            duration = 30
        elif "1" in txt:
            duration = 60
        else:
            duration = 120
            
        self.current_itinerary = self.engine.generate_itinerary(duration)
        
        for idx, item in enumerate(self.current_itinerary):
            text = f"{item['activity']} ({item['duration']} mins) - Location: {item['location']} | Reward: {item['reward']}"
            cb = QCheckBox(text)
            cb.setChecked(item["completed"])
            cb.stateChanged.connect(lambda state, index=idx: self.on_check_toggled(index, state))
            self.checkbox_layout.addWidget(cb)
            self.checkboxes.append(cb)
            
        self.update_progress_ui()

    def on_check_toggled(self, index: int, state: int) -> None:
        if 0 <= index < len(self.current_itinerary):
            self.current_itinerary[index]["completed"] = (state == 2)
        self.update_progress_ui()

    def update_progress_ui(self) -> None:
        total = len(self.current_itinerary)
        completed = sum(1 for item in self.current_itinerary if item["completed"])
        pct = int(completed / total * 100) if total > 0 else 0
        
        self.progress_label.setText(f"Session Progress: {pct}% ({completed}/{total} tasks complete)")
        self.progress_bar.setValue(pct)
