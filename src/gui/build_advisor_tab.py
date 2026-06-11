from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget
from src.core.build_advisor import BuildAdvisor

class BuildAdvisorTab(QWidget):
    """Class BuildAdvisorTab documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Weapon Name'))
        self.weapon_input = QLineEdit()
        self.weapon_input.setPlaceholderText('Example: Phenmor')
        self.layout.addWidget(self.weapon_input)
        self.search_button = QPushButton('Analyze Build')
        self.layout.addWidget(self.search_button)
        self.results = QListWidget()
        self.layout.addWidget(self.results)
        self.setLayout(self.layout)
        self.search_button.clicked.connect(self.analyze_build)

    def analyze_build(self) -> Any:
        """Method analyze_build."""
        self.results.clear()
        weapon = self.weapon_input.text().strip()
        if not weapon:
            self.results.addItem('Enter a weapon name.')
            return
        advisor = BuildAdvisor()
        recommendations = advisor.recommend_for_weapon(weapon)
        for item in recommendations:
            self.results.addItem(item)