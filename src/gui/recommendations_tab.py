from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel, QSplitter, QTextEdit, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from src.core.player_loader import PlayerLoader
from src.core.recommendation_engine import RecommendationEngine
from src.core.scoring_engine import ScoringEngine

class RecommendationsTab(QWidget):
    """Class RecommendationsTab documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.layout = QVBoxLayout()
        self.refresh_button = QPushButton('Refresh Recommendations')
        self.splitter = QSplitter(Qt.Horizontal)
        self.list_widget = QListWidget()
        self.list_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.splitter.addWidget(self.list_widget)
        self.splitter.addWidget(self.details)
        self.layout.addWidget(self.refresh_button)
        self.layout.addWidget(self.splitter)
        self.count_label = QLabel()
        self.layout.addWidget(self.count_label)
        self.setLayout(self.layout)
        self.refresh_button.clicked.connect(self.load_recommendations)
        self.list_widget.currentItemChanged.connect(self.on_selection)
        self.category_colors = {'STORY': QColor('#7fb3ff'), 'MOD': QColor('#7fffb3'), 'ARCANE': QColor('#caa3ff'), 'WEAPON': QColor('#ffb76b'), 'ENDGAME': QColor('#ff7b7b'), 'PROGRESSION': QColor('#6fffe8')}
        self.load_recommendations()

    def load_recommendations(self) -> Any:
        """Method load_recommendations."""
        self.list_widget.clear()
        player = PlayerLoader().load_player()
        engine = RecommendationEngine()
        scorer = ScoringEngine()
        recommendations = engine.generate_recommendations(player)
        scored = []
        for rec in recommendations:
            score = scorer.calculate_score(rec)
            scored.append((rec, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        self.count_label.setText(f'Recommendations Found: {len(scored)}')
        for index, (rec, score) in enumerate(scored, start=1):
            item_text = f'PRIORITY #{index} | [{rec.category}] | {rec.action}'
            item = self.list_widget.addItem(item_text)
            list_item = self.list_widget.item(self.list_widget.count() - 1)
            color = self.category_colors.get(rec.category, QColor('#ffffff'))
            list_item.setForeground(color)
            list_item.rec = rec
            list_item.score = score

    def on_selection(self, current: Any, previous: Any) -> Any:
        """Method on_selection."""
        if not current:
            self.details.clear()
            return
        rec = getattr(current, 'rec', None)
        score = getattr(current, 'score', None)
        if not rec:
            self.details.clear()
            return
        text = f'Action: {rec.action}\nCategory: {rec.category}\n\nReason: {rec.reason}\nCalculated Score: {score:.1f}\n\n'
        self.details.setPlainText(text)