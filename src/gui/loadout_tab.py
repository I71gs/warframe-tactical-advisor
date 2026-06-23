from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from src.core.loadout_advisor import LoadoutAdvisor
from src.core.loadout_engine import LoadoutEngine

class LoadoutTab(QWidget):
    """Class LoadoutTab documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Loadout Advisor'))
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)
        self.load_data()

    def load_data(self) -> Any:
        """Method load_data."""
        self.list_widget.clear()
        advisor = LoadoutAdvisor()
        legacy = advisor.analyze_account()
        engine = LoadoutEngine()
        player = None
        try:
            from src.core.player_loader import PlayerLoader
            player = PlayerLoader().load_player()
        except Exception:
            player = None
        self.list_widget.addItem('=== OWNED META WEAPONS ===')
        for weapon in legacy['owned']:
            self.list_widget.addItem(f'✓ {weapon}')
        self.list_widget.addItem('')
        self.list_widget.addItem('=== RECOMMENDED FARMS ===')
        for weapon in legacy['missing']:
            self.list_widget.addItem(f'• {weapon}')
        self.list_widget.addItem('')
        self.list_widget.addItem('=== RECOMMENDED LOADOUT ===')
        if player:
            rec = engine.recommend_loadout(player)
            self.list_widget.addItem(f"Overall Score: {rec.get('overall_score')}")
            for s in rec.get('strengths', []):
                self.list_widget.addItem(f'+ {s}')
            for w in rec.get('weaknesses', []):
                self.list_widget.addItem(f'- {w}')
            self.list_widget.addItem('')
            self.list_widget.addItem(f"Synergy Rating: {rec.get('synergy_rating')} (Score: {rec.get('synergy_score')}/100)")
            for reason in rec.get('synergy_reasons', []):
                self.list_widget.addItem(f"  • {reason}")
        else:
            self.list_widget.addItem('Player data unavailable for scoring')