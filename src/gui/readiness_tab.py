from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from src.core.player_loader import PlayerLoader
from src.core.readiness_analyzer import ReadinessAnalyzer

class ReadinessTab(QWidget):
    """Class ReadinessTab documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Activity Readiness'))
        self.result_list = QListWidget()
        self.layout.addWidget(self.result_list)
        self.setLayout(self.layout)
        self.load_readiness()

    def load_readiness(self) -> Any:
        """Method load_readiness."""
        print('Readiness Refreshed')
        self.result_list.clear()
        player = PlayerLoader().load_player()
        analyzer = ReadinessAnalyzer()
        checks = {'Steel Path': analyzer.check_steel_path(player), 'The New War': analyzer.check_new_war(player), 'Archon Hunts': analyzer.check_archon_hunts(player)}
        for activity, missing in checks.items():
            if not missing:
                self.result_list.addItem(f'✅ {activity} READY')
            else:
                self.result_list.addItem(f'❌ {activity}')
                for item in missing:
                    self.result_list.addItem(f'    • {item}')
                self.result_list.addItem('')