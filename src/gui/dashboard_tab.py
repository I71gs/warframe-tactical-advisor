from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGridLayout, QGroupBox, QFrame, QPushButton, QFileDialog
from PySide6.QtGui import QPixmap
from pathlib import Path
from src.core.player_loader import PlayerLoader
from src.core.progression_engine import ProgressionEngine
from src.core.recommendation_engine import RecommendationEngine
from src.core.readiness_analyzer import ReadinessAnalyzer

class DashboardTab(QWidget):
    """GUI tab displaying overall player progress, gaps, sub-scores, and recommendations."""

    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout()
        
        # Header Row
        header_row = QHBoxLayout()
        self.logo_lbl = QLabel()
        logo_path = Path.cwd() / 'assets' / 'logo.png'
        if logo_path.exists():
            try:
                pix = QPixmap(str(logo_path))
                if not pix.isNull():
                    self.logo_lbl.setPixmap(pix.scaledToWidth(160))
            except Exception:
                pass
        
        self.hero_title = QLabel('WARFRAME TACTICAL ADVISOR')
        self.hero_title.setObjectName('heroTitle')
        
        self.screenshot_btn = QPushButton("📸 Export PNG")
        self.screenshot_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f1a24;
                border: 1px solid #00a3cc;
                border-radius: 4px;
                color: #00a3cc;
                font-weight: bold;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: rgba(0, 163, 204, 0.1);
            }
        """)
        self.screenshot_btn.clicked.connect(self.export_screenshot)
        
        header_row.addWidget(self.logo_lbl)
        header_row.addWidget(self.hero_title)
        header_row.addStretch()
        header_row.addWidget(self.screenshot_btn)
        self.layout.addLayout(header_row)
        
        self.hero = QGroupBox()
        self.hero_layout = QVBoxLayout()
        self.hero_mr = QLabel('Mastery Rank: -')
        self.hero_stage = QLabel('Stage: -')
        self.hero_top = QLabel('Top Recommendation: -')
        self.hero_strength = QLabel('Account Strength: -')
        self.hero_layout.addWidget(self.hero_mr)
        self.hero_layout.addWidget(self.hero_stage)
        self.hero_layout.addWidget(self.hero_top)
        self.hero_layout.addWidget(self.hero_strength)
        self.hero.setLayout(self.hero_layout)

        # Dashboard 4.0 Progression Coach Insights Panel
        self.priority_box = QGroupBox("Progression Coach Insights")
        self.priority_layout = QHBoxLayout()
        
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        self.priority_text = QLabel("Priority: -")
        self.priority_text.setStyleSheet("font-size: 12px; font-weight: bold; color: #00a3cc;")
        self.priority_reason = QLabel("Reason: -")
        self.priority_reason.setWordWrap(True)
        self.priority_gain = QLabel("Est. Power Gain: -")
        self.priority_gain.setStyleSheet("font-weight: 600; color: #22c55e;")
        left_layout.addWidget(self.priority_text)
        left_layout.addWidget(self.priority_reason)
        left_layout.addWidget(self.priority_gain)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        self.daily_status = QLabel("Daily Objectives: -")
        self.weekly_status = QLabel("Weekly Goals: -")
        self.long_term_status = QLabel("30-Day Roadmap: -")
        right_layout.addWidget(self.daily_status)
        right_layout.addWidget(self.weekly_status)
        right_layout.addWidget(self.long_term_status)
        
        self.priority_layout.addWidget(left_widget, 1)
        self.priority_layout.addWidget(right_widget, 1)
        self.priority_box.setLayout(self.priority_layout)

        # Grid Layout for sub-scores
        grid = QGridLayout()
        self.card_story = QGroupBox('Story Completion')
        self.card_mods = QGroupBox('Mod Completion')
        self.card_arcanes = QGroupBox('Arcane Completion')
        self.card_weapons = QGroupBox('Weapon Completion')
        self.card_mastery = QGroupBox('Mastery Rank Progress')
        self.card_unlocks = QGroupBox('System Unlocks')
        self.card_build = QGroupBox('Build Optimization')
        
        self.story_bar = QProgressBar()
        self.mods_bar = QProgressBar()
        self.arcanes_bar = QProgressBar()
        self.weapons_bar = QProgressBar()
        self.mastery_bar = QProgressBar()
        self.unlocks_bar = QProgressBar()
        self.build_bar = QProgressBar()
        
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
        
        mr_layout = QVBoxLayout()
        mr_layout.addWidget(self.mastery_bar)
        self.card_mastery.setLayout(mr_layout)
        
        u_layout = QVBoxLayout()
        u_layout.addWidget(self.unlocks_bar)
        self.card_unlocks.setLayout(u_layout)
        
        b_layout = QVBoxLayout()
        b_layout.addWidget(self.build_bar)
        self.card_build.setLayout(b_layout)
        
        grid.addWidget(self.card_story, 0, 0)
        grid.addWidget(self.card_mods, 0, 1)
        grid.addWidget(self.card_arcanes, 1, 0)
        grid.addWidget(self.card_weapons, 1, 1)
        grid.addWidget(self.card_mastery, 2, 0)
        grid.addWidget(self.card_unlocks, 2, 1)
        grid.addWidget(self.card_build, 3, 0, 1, 2)
        
        self.layout.addWidget(self.hero)
        self.layout.addWidget(self.priority_box)
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
        
        story_pct = engine.get_story_score(player)
        mods_pct = engine.get_mod_score(player)
        arcanes_pct = engine.get_arcane_score(player)
        weapons_pct = engine.get_weapon_score(player)
        mastery_pct = engine.get_mastery_score(player)
        unlocks_pct = engine.get_unlock_score(player)
        build_pct = engine.get_build_score(player)
        
        self.story_bar.setValue(int(story_pct))
        self.mods_bar.setValue(int(mods_pct))
        self.arcanes_bar.setValue(int(arcanes_pct))
        self.weapons_bar.setValue(int(weapons_pct))
        self.mastery_bar.setValue(int(mastery_pct))
        self.unlocks_bar.setValue(int(unlocks_pct))
        self.build_bar.setValue(int(build_pct))
        
        # Load Today's Priority Target
        from src.core.next_action_engine import NextActionEngine
        nae = NextActionEngine()
        action = nae.determine_next_action(player)
        self.priority_text.setText(f"🎯 Action: {action['priority']}")
        self.priority_reason.setText(f"Rationale: {action['reason']}")
        self.priority_gain.setText(f"Est. Gain: {action['gain']}")

        # Load Checklists statuses for Dashboard 4.0
        try:
            from src.core.daily_objectives_engine import DailyObjectivesEngine
            doe = DailyObjectivesEngine()
            dailies = doe.get_daily_objectives(player)
            total_d = len(dailies["objectives"])
            done_d = sum(1 for o in dailies["objectives"] if o["completed"])
            self.daily_status.setText(f"📅 Daily Progress: {done_d}/{total_d} Objectives Done")
        except Exception:
            self.daily_status.setText("📅 Daily Progress: Unavailable")
            
        try:
            from src.core.weekly_planner import WeeklyPlanner
            wp = WeeklyPlanner()
            weeklies = wp.get_weekly_state(player)
            total_w = len(weeklies["goals"])
            done_w = sum(1 for g in weeklies["goals"] if g["completed"])
            w_pct = int(done_w / total_w * 100) if total_w > 0 else 0
            self.weekly_status.setText(f"📆 Weekly Progress: {w_pct}% ({done_w}/{total_w} Goals Met)")
        except Exception:
            self.weekly_status.setText("📆 Weekly Progress: Unavailable")
            
        try:
            from src.core.long_term_planner import LongTermPlanner
            ltp = LongTermPlanner()
            timeline = ltp.get_timeline_state(player)
            self.long_term_status.setText(f"🚀 30-Day Milestone: {timeline['target_milestone']} (Est. {timeline['estimated_time']})")
        except Exception:
            self.long_term_status.setText("🚀 30-Day Milestone: Unavailable")

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

    def export_screenshot(self) -> None:
        """Grabs a screenshot of the dashboard tab widget and saves it as a PNG image."""
        pixmap = self.grab()
        path, _ = QFileDialog.getSaveFileName(self, "Export Dashboard Screenshot", "", "PNG Image (*.png)")
        if path:
            try:
                pixmap.save(path, "PNG")
            except Exception:
                pass