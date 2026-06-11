from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QGridLayout, QGroupBox, QFrame
from PySide6.QtGui import QPixmap
from pathlib import Path
from src.core.player_loader import PlayerLoader
from src.core.progression_engine import ProgressionEngine
from src.core.recommendation_engine import RecommendationEngine
from src.core.readiness_analyzer import ReadinessAnalyzer

class DashboardTab(QWidget):
    """Class DashboardTab documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.layout = QVBoxLayout()
        self.hero = QGroupBox()
        self.hero_layout = QVBoxLayout()
        self.hero_title = QLabel('WARFRAME TACTICAL ADVISOR')
        self.hero_title.setObjectName('heroTitle')
        logo_path = Path.cwd() / 'assets' / 'logo.png'
        if logo_path.exists():
            try:
                pix = QPixmap(str(logo_path))
                if not pix.isNull():
                    logo_lbl = QLabel()
                    logo_lbl.setPixmap(pix.scaledToWidth(160))
                    self.hero_layout.addWidget(logo_lbl)
            except Exception:
                pass
        self.hero_mr = QLabel('Mastery Rank: -')
        self.hero_stage = QLabel('Stage: -')
        self.hero_top = QLabel('Top Recommendation: -')
        self.hero_strength = QLabel('Account Strength: -')
        self.hero_layout.addWidget(self.hero_title)
        self.hero_layout.addWidget(self.hero_mr)
        self.hero_layout.addWidget(self.hero_stage)
        self.hero_layout.addWidget(self.hero_top)
        self.hero_layout.addWidget(self.hero_strength)
        self.hero.setLayout(self.hero_layout)
        grid = QGridLayout()
        self.card_story = QGroupBox('Story Completion')
        self.card_mods = QGroupBox('Mod Completion')
        self.card_arcanes = QGroupBox('Arcane Completion')
        self.card_weapons = QGroupBox('Weapon Completion')
        self.story_bar = QProgressBar()
        self.mods_bar = QProgressBar()
        self.arcanes_bar = QProgressBar()
        self.weapons_bar = QProgressBar()
        s_layout = QVBoxLayout()
        s_layout.addWidget(self.story_bar)
        self.card_story.setLayout(s_layout)
        m_layout = QVBoxLayout()
        m_layout.addWidget(self.mods_bar)
        self.card_mods.setLayout(m_layout)
        a_layout = QVBoxLayout()
        a_layout.addWidget(self.arcanes_bar)
        self.card_arcanes.setLayout(a_layout)
        w_layout = QVBoxLayout()
        w_layout.addWidget(self.weapons_bar)
        self.card_weapons.setLayout(w_layout)
        grid.addWidget(self.card_story, 0, 0)
        grid.addWidget(self.card_mods, 0, 1)
        grid.addWidget(self.card_arcanes, 1, 0)
        grid.addWidget(self.card_weapons, 1, 1)
        self.layout.addWidget(self.hero)
        self.layout.addLayout(grid)
        self.setLayout(self.layout)
        self.load_dashboard()

    def load_dashboard(self) -> Any:
        """Method load_dashboard."""
        print('Dashboard Refreshed')
        player = PlayerLoader().load_player()
        engine = ProgressionEngine()
        rec_engine = RecommendationEngine()
        score = engine.get_readiness_score(player)
        stage = engine.determine_stage(player)
        self.hero_mr.setText(f'Mastery Rank: {player.mastery_rank}')
        self.hero_stage.setText(f'Stage: {stage.upper()}')
        story_pct = engine.get_story_completion_percentage(player)
        mods_pct = engine.get_mod_completion_percentage(player)
        arcanes_pct = engine.get_arcane_completion_percentage(player)
        weapons_pct = engine.get_weapon_completion_percentage(player)
        next_quest = engine.get_next_story_quest(player)
        self.story_bar.setValue(int(story_pct))
        self.mods_bar.setValue(int(mods_pct))
        self.arcanes_bar.setValue(int(arcanes_pct))
        self.weapons_bar.setValue(int(weapons_pct))
        recs = rec_engine.generate_recommendations(player)
        top = recs[0].action if recs else 'No recommendations'
        self.hero_top.setText(f'Top Recommendation: {top}')
        self.hero_strength.setText(f'Account Strength: {score}%')
        analyzer = ReadinessAnalyzer()
        badges = []
        if story_pct >= 100:
            badges.append(('Story Complete', True))
        else:
            badges.append(('Story Complete', False))
        badges.append(('Steel Path Ready', player.steel_path_unlocked))
        archon_missing = analyzer.check_archon_hunts(player)
        badges.append(('Archon Ready', len(archon_missing) == 0))
        new_war_missing = analyzer.check_new_war(player)
        badges.append(('New War Ready', len(new_war_missing) == 0))
        try:
            for i in reversed(range(self.hero_layout.count())):
                w = self.hero_layout.itemAt(i).widget()
                if getattr(w, 'is_badge', False):
                    self.hero_layout.removeWidget(w)
                    w.deleteLater()
        except Exception:
            pass
        for name, state in badges:
            lbl = QLabel(f'✓ {name}' if state else f'✗ {name}')
            lbl.is_badge = True
            if state:
                lbl.setStyleSheet('color: #22c55e; font-weight: 600;')
            else:
                lbl.setStyleSheet('color: #9fb6c8;')
            self.hero_layout.addWidget(lbl)