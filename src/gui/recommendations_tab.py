from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QPushButton
)

from src.core.player_loader import PlayerLoader
from src.core.recommendation_engine import RecommendationEngine
from src.core.scoring_engine import ScoringEngine


class RecommendationsTab(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QVBoxLayout()

        self.refresh_button = QPushButton(
            "Refresh Recommendations"
        )

        self.list_widget = QListWidget()

        self.layout.addWidget(
            self.refresh_button
        )

        self.layout.addWidget(
            self.list_widget
        )

        self.setLayout(
            self.layout
        )

        self.refresh_button.clicked.connect(
            self.load_recommendations
        )

        self.load_recommendations()

    def load_recommendations(self):

        self.list_widget.clear()

        player = PlayerLoader().load_player()

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

        for rec, score in scored:

            self.list_widget.addItem(
                f"{rec.action}\n"
                f"Reason: {rec.reason}\n"
                f"Score: {score:.1f}"
            )