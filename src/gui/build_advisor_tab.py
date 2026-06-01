from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget
)

from src.core.build_advisor import (
    BuildAdvisor
)


class BuildAdvisorTab(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QVBoxLayout()

        self.layout.addWidget(
            QLabel("Weapon Name")
        )

        self.weapon_input = QLineEdit()

        self.layout.addWidget(
            self.weapon_input
        )

        self.search_button = QPushButton(
            "Analyze Build"
        )

        self.layout.addWidget(
            self.search_button
        )

        self.results = QListWidget()

        self.layout.addWidget(
            self.results
        )

        self.setLayout(
            self.layout
        )

        self.search_button.clicked.connect(
            self.analyze_build
        )

    def analyze_build(self):

        self.results.clear()

        weapon = (
            self.weapon_input.text()
        )

        advisor = BuildAdvisor()

        recommendations = (
            advisor.recommend_for_weapon(
                weapon
            )
        )

        for item in recommendations:

            self.results.addItem(item)