from typing import Any

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QSplitter,
    QTextEdit,
    QSizePolicy,
    QListWidgetItem
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from src.core.player_loader import PlayerLoader
from src.core.recommendation_engine import RecommendationEngine
from src.core.scoring_engine import ScoringEngine


class RecommendationsTab(QWidget):

    def __init__(self) -> None:

        super().__init__()

        self.layout = QVBoxLayout()

        self.refresh_button = QPushButton(
            "Refresh Recommendations"
        )

        self.splitter = QSplitter(
            Qt.Horizontal
        )

        self.list_widget = QListWidget()

        self.list_widget.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Expanding
        )

        self.details = QTextEdit()

        self.details.setReadOnly(True)

        self.splitter.addWidget(
            self.list_widget
        )

        self.splitter.addWidget(
            self.details
        )

        self.splitter.setStretchFactor(
            0,
            2
        )

        self.splitter.setStretchFactor(
            1,
            3
        )

        self.layout.addWidget(
            self.refresh_button
        )

        self.layout.addWidget(
            self.splitter
        )

        self.count_label = QLabel()

        self.layout.addWidget(
            self.count_label
        )

        self.setLayout(
            self.layout
        )

        self.refresh_button.clicked.connect(
            self.load_recommendations
        )

        self.list_widget.currentItemChanged.connect(
            self.on_selection
        )

        self.category_colors = {

            "STORY":
                QColor("#7fb3ff"),

            "MOD":
                QColor("#7fffb3"),

            "ARCANE":
                QColor("#caa3ff"),

            "WEAPON":
                QColor("#ffb76b"),

            "ENDGAME":
                QColor("#ff7b7b"),

            "PROGRESSION":
                QColor("#6fffe8")
        }

        self.recommendation_map = {}

        self.load_recommendations()

    def load_recommendations(self) -> Any:

        self.list_widget.clear()

        self.details.clear()

        self.recommendation_map.clear()

        player = (
            PlayerLoader()
            .load_player()
        )

        engine = RecommendationEngine()

        scorer = ScoringEngine()

        recommendations = (
            engine.generate_recommendations(
                player
            )
        )

        scored = []

        for rec in recommendations:

            score = scorer.calculate_score(
                rec
            )

            scored.append(
                (rec, score)
            )

        scored.sort(
            key=lambda x: x[1],
            reverse=True
        )

        self.count_label.setText(
            f"Recommendations Found: {len(scored)}"
        )

        for index, (rec, score) in enumerate(
            scored,
            start=1
        ):

            text = (
                f"#{index} "
                f"[{rec.category}] "
                f"{rec.action}"
            )

            item = QListWidgetItem(
                text
            )

            color = self.category_colors.get(
                rec.category,
                QColor("#ffffff")
            )

            item.setForeground(
                color
            )

            self.list_widget.addItem(
                item
            )

            self.recommendation_map[id(item)] = {
                "recommendation": rec,
                "score": score
            }

        if self.list_widget.count() > 0:

            self.list_widget.setCurrentRow(
                0
            )

    def on_selection(
        self,
        current,
        previous
    ) -> Any:

        if current is None:

            self.details.clear()

            return

        data = self.recommendation_map.get(
            id(current)
        )

        if not data:

            self.details.clear()

            return

        rec = data["recommendation"]

        score = data["score"]

        text = (
            f"Action\n"
            f"────────────────────\n"
            f"{rec.action}\n\n"

            f"Category\n"
            f"────────────────────\n"
            f"{rec.category}\n\n"

            f"Reason\n"
            f"────────────────────\n"
            f"{rec.reason}\n\n"

            f"Priority Score\n"
            f"────────────────────\n"
            f"{score:.1f}\n\n"

            f"Power Gain: {rec.power_gain}\n"
            f"Account Progress: {rec.account_progress}\n"
            f"Time Efficiency: {rec.time_efficiency}"
        )

        self.details.setPlainText(
            text
        )