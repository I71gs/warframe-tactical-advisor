from __future__ import annotations
from typing import Any

from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QGridLayout, QGroupBox, QFrame, QPushButton, QFileDialog,
    QScrollArea, QSizePolicy,
)
from pathlib import Path

from src.core.player_loader import PlayerLoader
from src.core.progression_engine import ProgressionEngine
from src.core.recommendation_engine import RecommendationEngine
from src.core.readiness_analyzer import ReadinessAnalyzer
from src.gui.widgets.circle_progress import CircleProgress



# ── tiny helpers ──────────────────────────────────────────────────────────────

def _card(title: str, color: str | None = None, min_h: int = 120) -> tuple[QGroupBox, QVBoxLayout]:
    from src.core.theme_manager import ThemeManager
    theme_colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
    accent = color or theme_colors.get("ACCENT", "#bb86fc")
    bg = theme_colors.get("CARD", "#1f183a")
    
    box = QGroupBox(title)
    box.setMinimumHeight(min_h)
    box.setStyleSheet(f"""
        QGroupBox {{
            background-color: {bg};
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            margin-top: 8px;
            font-weight: bold;
            color: {accent};
            padding: 6px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            color: {accent};
        }}
    """)
    lay = QVBoxLayout(box)
    lay.setSpacing(4)
    return box, lay


def _row_label(text: str, color: str | None = None, bold: bool = False) -> QLabel:
    from src.core.theme_manager import ThemeManager
    theme_colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
    fg = color or theme_colors.get("TEXT", "#eae6f8")
    
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    weight = "bold" if bold else "normal"
    lbl.setStyleSheet(f"color: {fg}; font-weight: {weight}; font-size: 11px;")
    return lbl


def _progress_bar(color: str | None = None, height: int = 10) -> QProgressBar:
    from src.core.theme_manager import ThemeManager
    theme_colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
    bg = theme_colors.get("SECONDARY", "#130f26")
    accent = color or theme_colors.get("ACCENT", "#bb86fc")

    bar = QProgressBar()
    bar.setTextVisible(False)
    bar.setFixedHeight(height)
    bar.setStyleSheet(f"""
        QProgressBar {{ background-color: {bg}; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 4px; }}
        QProgressBar::chunk {{ background-color: {accent}; border-radius: 4px; }}
    """)
    return bar



class DashboardTab(QWidget):
    """Command Centre Dashboard v2.

    4-column layout:
      Col 1  Today's Priorities (daily tasks, Nightwave acts)
      Col 2  Live World State (fissures, alerts, sorties, Archon)
      Col 3  Goal Tracker + Economy Bottlenecks
      Col 4  MR Progress + Power Score + Readiness badges
    """

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self.load_dashboard()

        # Auto-refresh world state every 5 minutes
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_world_state)
        self._refresh_timer.start(5 * 60 * 1000)

    # ── UI construction ───────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        # ── top header ─────────────────────────────────────────────────────
        header_row = QHBoxLayout()

        logo_lbl = QLabel()
        logo_path = Path.cwd() / "assets" / "logo.png"
        if logo_path.exists():
            try:
                pix = QPixmap(str(logo_path))
                if not pix.isNull():
                    logo_lbl.setPixmap(pix.scaledToWidth(140))
            except Exception:
                pass
        header_row.addWidget(logo_lbl)

        from src.core.theme_manager import ThemeManager
        theme_colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
        accent = theme_colors.get("ACCENT", "#bb86fc")
        primary = theme_colors.get("PRIMARY", "#0c0919")
        secondary = theme_colors.get("SECONDARY", "#130f26")
        card_bg = theme_colors.get("CARD", "#1f183a")
        muted = theme_colors.get("MUTED", "#8e85a6")

        title_col = QVBoxLayout()
        hero_title = QLabel("WARFRAME TACTICAL ADVISOR")
        hero_title.setObjectName("heroTitle")
        hero_title.setStyleSheet(
            f"font-size: 22px; font-weight: 900; color: {accent}; letter-spacing: 2px;"
        )
        self.sub_title = QLabel("Loading…")
        self.sub_title.setStyleSheet(f"color: {muted}; font-size: 11px;")
        title_col.addWidget(hero_title)
        title_col.addWidget(self.sub_title)
        header_row.addLayout(title_col)
        header_row.addStretch()

        # "Today at a Glance" banner
        self.glance_banner = QLabel("⚡  Today at a Glance:  —")
        self.glance_banner.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {card_bg},stop:1 {primary});
            border: 1px solid {accent}44;
            border-radius: 6px;
            color: {accent};
            font-size: 12px;
            font-weight: bold;
            padding: 6px 16px;
        """)
        header_row.addWidget(self.glance_banner, 1)

        screenshot_btn = QPushButton("📸 Export PNG")
        screenshot_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {card_bg}; border: 1px solid {accent};
                border-radius: 4px; color: {accent}; font-weight: bold; padding: 6px 12px;
            }}
            QPushButton:hover {{ background-color: rgba(255, 255, 255, 0.05); }}
        """)
        screenshot_btn.clicked.connect(self.export_screenshot)
        header_row.addWidget(screenshot_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(screenshot_btn.styleSheet())
        refresh_btn.clicked.connect(self.load_dashboard)
        header_row.addWidget(refresh_btn)

        root.addLayout(header_row)

        # thin separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {secondary}; border: 1px solid rgba(255, 255, 255, 0.05);")
        root.addWidget(sep)


        # ── hero row (MR + score badges) ───────────────────────────────────
        hero_row = QHBoxLayout()

        self.hero_mr      = self._hero_chip("MR —",      "#caa3ff")
        self.hero_stage   = self._hero_chip("Stage —",    "#ffb76b")
        self.hero_score   = self._hero_chip("Score —%",   "#7fffb3")
        self.hero_sp      = self._hero_chip("SP: —",      "#ff9fd4")
        self.hero_uptime  = self._hero_chip("Session —",  "#7fb3ff")
        self.hero_top_rec = self._hero_chip("🎯 —",       "#00d4ff", wide=True)

        for chip in (self.hero_mr, self.hero_stage, self.hero_score,
                     self.hero_sp, self.hero_uptime, self.hero_top_rec):
            hero_row.addWidget(chip)
        hero_row.addStretch()
        root.addLayout(hero_row)

        # ── 4-column command centre ────────────────────────────────────────
        cols_row = QHBoxLayout()
        cols_row.setSpacing(10)

        # Col 1 — Today's Priorities
        col1_box, col1_lay = _card("📅  Today's Priorities", "#00d4ff", 280)
        self.daily_items_lay = col1_lay
        self.daily_labels: list[QLabel] = []
        for _ in range(8):
            lbl = _row_label("—")
            col1_lay.addWidget(lbl)
            self.daily_labels.append(lbl)
        col1_lay.addStretch()

        # Weekly strip
        weekly_strip, weekly_lay = _card("📆  Weekly Goals", "#7fb3ff", 100)
        self.weekly_progress_bar = _progress_bar("#7fb3ff")
        self.weekly_label = _row_label("—/— Goals met")
        weekly_lay.addWidget(self.weekly_label)
        weekly_lay.addWidget(self.weekly_progress_bar)
        weekly_lay.addStretch()

        col1_wrap = QVBoxLayout()
        col1_wrap.addWidget(col1_box, 2)
        col1_wrap.addWidget(weekly_strip, 1)
        cols_row.addLayout(col1_wrap, 1)

        # Col 2 — World State
        col2_box, col2_lay = _card("🌍  World State", "#ffb76b", 380)
        self.ws_status_lbl = _row_label("● Online", "#7fffb3", bold=True)
        col2_lay.addWidget(self.ws_status_lbl)

        ws_sections = [
            ("Fissures",    "fissures"),
            ("Alert",       "alert"),
            ("Sortie",      "sortie"),
            ("Archon Hunt", "archon"),
            ("Nightwave",   "nightwave"),
            ("Void Trader", "void_trader"),
        ]
        self.ws_labels: dict[str, QLabel] = {}
        for title_ws, key in ws_sections:
            row_w = QHBoxLayout()
            t_lbl = QLabel(f"{title_ws}:")
            t_lbl.setStyleSheet("color: #7a8fa6; font-size: 10px; min-width: 78px;")
            v_lbl = QLabel("—")
            v_lbl.setStyleSheet("color: #ffb76b; font-size: 10px; font-weight: bold;")
            v_lbl.setWordWrap(True)
            row_w.addWidget(t_lbl)
            row_w.addWidget(v_lbl, 1)
            col2_lay.addLayout(row_w)
            self.ws_labels[key] = v_lbl
        col2_lay.addStretch()
        cols_row.addWidget(col2_box, 1)

        # Col 3 — Goal Tracker + Economy
        col3_box, col3_lay = _card("🎯  Goal Tracker", "#caa3ff", 200)
        self.goal_labels: list[QLabel] = []
        for _ in range(5):
            lbl = _row_label("—")
            col3_lay.addWidget(lbl)
            self.goal_labels.append(lbl)
        col3_lay.addStretch()

        econ_box, econ_lay = _card("💎  Resource Bottlenecks", "#ff9fd4", 180)
        self.econ_labels: list[QLabel] = []
        for _ in range(5):
            lbl = _row_label("—")
            econ_lay.addWidget(lbl)
            self.econ_labels.append(lbl)
        econ_lay.addStretch()

        col3_wrap = QVBoxLayout()
        col3_wrap.addWidget(col3_box, 1)
        col3_wrap.addWidget(econ_box, 1)
        cols_row.addLayout(col3_wrap, 1)

        # Col 4 — MR + Scores + Readiness
        col4_box, col4_lay = _card("📊  Progression Metrics", "#7fffb3", 380)

        # Circular progress layout
        circles_lay = QHBoxLayout()
        self.mr_circle = CircleProgress(self, size=60, width=4.0, color="#caa3ff")
        self.mr_circle_lbl = _row_label("Mastery Rank\nXP Progress", "#caa3ff", bold=True)
        self.mr_circle_lbl.setAlignment(Qt.AlignCenter)

        self.readiness_circle = CircleProgress(self, size=60, width=4.0, color="#7fffb3")
        self.readiness_circle_lbl = _row_label("Overall\nReadiness", "#7fffb3", bold=True)
        self.readiness_circle_lbl.setAlignment(Qt.AlignCenter)

        c1 = QVBoxLayout()
        c1.addWidget(self.mr_circle, 0, Qt.AlignCenter)
        c1.addWidget(self.mr_circle_lbl, 0, Qt.AlignCenter)

        c2 = QVBoxLayout()
        c2.addWidget(self.readiness_circle, 0, Qt.AlignCenter)
        c2.addWidget(self.readiness_circle_lbl, 0, Qt.AlignCenter)

        circles_lay.addLayout(c1)
        circles_lay.addLayout(c2)
        col4_lay.addLayout(circles_lay)

        self.mr_lbl = _row_label("MR: —  |  XP needed: —")
        col4_lay.addWidget(self.mr_lbl)


        score_sections = [
            ("Story",    "story",    "#7fb3ff"),
            ("Mods",     "mods",     "#7fffb3"),
            ("Weapons",  "weapons",  "#ffb76b"),
            ("Arcanes",  "arcanes",  "#ff9fd4"),
            ("Build",    "build",    "#caa3ff"),
            ("Mastery",  "mastery",  "#ffd56b"),
        ]
        self.score_bars: dict[str, tuple[QLabel, QProgressBar]] = {}
        for name, key, color in score_sections:
            lbl = _row_label(f"{name}: —%", color)
            bar = _progress_bar(color, 8)
            col4_lay.addWidget(lbl)
            col4_lay.addWidget(bar)
            self.score_bars[key] = (lbl, bar)

        col4_lay.addWidget(_row_label("Readiness Badges:", "#7a8fa6"))
        self.badge_layout = QHBoxLayout()
        col4_lay.addLayout(self.badge_layout)
        col4_lay.addStretch()

        col4_wrap = QVBoxLayout()
        col4_wrap.addWidget(col4_box)
        cols_row.addLayout(col4_wrap, 1)

        root.addLayout(cols_row)

    @staticmethod
    def _hero_chip(text: str, color: str, wide: bool = False) -> QLabel:
        from src.core.theme_manager import ThemeManager
        theme_colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
        card_bg = theme_colors.get("CARD", "#1f183a")
        
        lbl = QLabel(text)
        min_w = 180 if wide else 100
        lbl.setStyleSheet(f"""
            background: {card_bg};
            border: 1px solid {color}66;
            border-radius: 6px;
            color: {color};
            font-size: 11px;
            font-weight: bold;
            padding: 4px 10px;
            min-width: {min_w}px;
        """)
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    # ── data loading ──────────────────────────────────────────────────────────

    def load_dashboard(self) -> None:
        """Refresh all dashboard panels from engine data."""
        player = PlayerLoader().load_player()
        engine = ProgressionEngine()
        rec_engine = RecommendationEngine()

        # Hero row
        score = engine.get_readiness_score(player)
        stage = engine.determine_stage(player)
        recs = rec_engine.generate_recommendations(player)
        top_rec = recs[0].action if recs else "No recommendations"

        self.hero_mr.setText(f"MR {player.mastery_rank}")
        self.hero_stage.setText(stage.title())
        self.hero_score.setText(f"Score {score}%")
        self.hero_sp.setText("✓ Steel Path" if player.steel_path_unlocked else "✗ Steel Path")
        self.hero_uptime.setText(f"🕐 {QDateTime.currentDateTime().toString('hh:mm')}")
        self.hero_top_rec.setText(f"🎯 {top_rec[:50]}")
        self.sub_title.setText(f"Last refreshed: {QDateTime.currentDateTime().toString('ddd dd MMM yyyy  hh:mm:ss')}")

        # Sub-scores
        score_map = {
            "story":   engine.get_story_score(player),
            "mods":    engine.get_mod_score(player),
            "weapons": engine.get_weapon_score(player),
            "arcanes": engine.get_arcane_score(player),
            "build":   engine.get_build_score(player),
            "mastery": engine.get_mastery_score(player),
        }
        for key, (lbl, bar) in self.score_bars.items():
            val = int(score_map.get(key, 0))
            lbl.setText(f"{key.title()}: {val}%")
            bar.setValue(val)

        # Update readiness circle
        self.readiness_circle.setValue(score)

        # MR circles
        try:
            from src.core.mastery_planner import MasteryPlanner, _xp_needed_for_rank, _xp_gap_to_next
            mp = MasteryPlanner()
            plan = mp.calculate_plan(player)
            mr_pct = int(player.mastery_rank / 30 * 100)
            self.mr_lbl.setText(
                f"MR {plan['current_mr']} → {plan['next_mr']}  |  XP needed: {plan['xp_needed']:,}"
            )
            self.mr_circle.setValue(mr_pct)
        except Exception:
            self.mr_circle.setValue(int(player.mastery_rank / 30 * 100))


        # Readiness badges
        analyzer = ReadinessAnalyzer()
        while self.badge_layout.count():
            item = self.badge_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        badge_defs = [
            ("Story", engine.get_story_score(player) >= 100),
            ("Steel Path", player.steel_path_unlocked),
            ("Archon", len(analyzer.check_archon_hunts(player)) == 0),
            ("New War", len(analyzer.check_new_war(player)) == 0),
        ]
        for name, achieved in badge_defs:
            lbl = QLabel("✓" if achieved else "○")
            color = "#22c55e" if achieved else "#3a4a5a"
            lbl.setToolTip(name)
            lbl.setStyleSheet(f"""
                background: {color}22; border: 1px solid {color}66;
                border-radius: 4px; color: {color};
                font-size: 11px; font-weight: bold;
                padding: 2px 8px; margin-right: 4px;
            """)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setToolTip(name)
            self.badge_layout.addWidget(lbl)

        # Col 1 — Daily tasks
        self._load_daily(player)

        # Col 2 — World state
        self._refresh_world_state()

        # Col 3 — Goals + Economy
        self._load_goals(player)
        self._load_economy()

        # Glance banner
        self.glance_banner.setText(
            f"⚡  Today at a Glance:  MR {player.mastery_rank}  ·  Score {score}%  ·  🎯 {top_rec[:40]}"
        )

    def _load_daily(self, player: Any) -> None:
        """Fill the daily-tasks column."""
        items: list[str] = []
        try:
            from src.core.daily_objectives_engine import DailyObjectivesEngine
            doe = DailyObjectivesEngine()
            dailies = doe.get_daily_objectives(player)
            for obj in dailies.get("objectives", [])[:8]:
                icon = "✅" if obj.get("completed") else "⬜"
                items.append(f"{icon} {obj['name']}")
        except Exception:
            items = ["Daily data unavailable"]

        for i, lbl in enumerate(self.daily_labels):
            lbl.setText(items[i] if i < len(items) else "—")

        # Weekly
        try:
            from src.core.weekly_planner import WeeklyPlanner
            wp = WeeklyPlanner()
            weeklies = wp.get_weekly_state(player)
            total_w = len(weeklies.get("goals", []))
            done_w = sum(1 for g in weeklies.get("goals", []) if g.get("completed"))
            self.weekly_label.setText(f"{done_w}/{total_w} weekly goals met")
            self.weekly_progress_bar.setValue(int(done_w / total_w * 100) if total_w else 0)
        except Exception:
            self.weekly_label.setText("Weekly data unavailable")

    def _refresh_world_state(self) -> None:
        """Pull live world state; fall back to 'Offline' gracefully."""
        try:
            from src.core.app_context import AppContext
            wss = AppContext().world_state_service
            state = wss.get_world_state()

            fissures = state.get("fissures", [])
            fissure_text = ", ".join(
                f"{f.get('tier','?')} ({f.get('missionType','?')})" for f in fissures[:3]
            ) or "None active"

            alert = state.get("alerts", [{}])[0] if state.get("alerts") else {}
            alert_text = alert.get("mission", {}).get("reward", {}).get("asString", "None") if alert else "None"

            sortie = state.get("sortie", {})
            sortie_text = f"{sortie.get('boss', '?')} — {sortie.get('faction', '?')}" if sortie else "Unavailable"

            archon = state.get("archonHunt", {})
            archon_text = f"{archon.get('boss', '?')} ({archon.get('faction', '?')})" if archon else "Unavailable"

            nightwave = state.get("nightwave", {})
            nw_season = nightwave.get("season", "?")
            nw_phase = nightwave.get("phase", "?")
            nw_text = f"Season {nw_season} — Phase {nw_phase}" if nightwave else "Unavailable"

            baro = state.get("voidTrader", {})
            baro_text = "Baro at " + baro.get("location", "Unknown") if baro.get("active") else "Not visiting"

            self.ws_labels["fissures"].setText(fissure_text)
            self.ws_labels["alert"].setText(alert_text)
            self.ws_labels["sortie"].setText(sortie_text)
            self.ws_labels["archon"].setText(archon_text)
            self.ws_labels["nightwave"].setText(nw_text)
            self.ws_labels["void_trader"].setText(baro_text)
            self.ws_status_lbl.setText("● Online")
            self.ws_status_lbl.setStyleSheet("color: #22c55e; font-size: 10px; font-weight: bold;")

        except Exception:
            for lbl in self.ws_labels.values():
                lbl.setText("—")
            self.ws_status_lbl.setText("● Offline (cached)")
            self.ws_status_lbl.setStyleSheet("color: #f59e0b; font-size: 10px; font-weight: bold;")

    def _load_goals(self, player: Any) -> None:
        """Fill the goal tracker column."""
        items: list[str] = []
        try:
            from src.core.goal_planner import GoalPlanner
            gp = GoalPlanner()
            goals = gp.get_active_goals(player) if hasattr(gp, "get_active_goals") else []
            for g in goals[:5]:
                name = g.get("name", str(g))
                pct = g.get("progress_pct", 0)
                items.append(f"🔸 {name} ({pct}%)")
        except Exception:
            items = ["Goal tracker unavailable"]

        for i, lbl in enumerate(self.goal_labels):
            lbl.setText(items[i] if i < len(items) else "—")

    def _load_economy(self) -> None:
        """Fill the economy bottleneck column."""
        items: list[str] = []
        try:
            from src.core.economy_engine import EconomyEngine
            ee = EconomyEngine()
            bottlenecks = ee.get_bottleneck_resources(top_n=5)
            for b in bottlenecks:
                res = b["resource"]
                miss = b["missing"]
                hrs = b["farm_hours"]
                items.append(f"⚠ {res}: need {miss:,}  ({hrs}h)")
        except Exception:
            items = ["Economy data unavailable"]

        for i, lbl in enumerate(self.econ_labels):
            lbl.setText(items[i] if i < len(items) else "—")

    # ── export ────────────────────────────────────────────────────────────────

    def export_screenshot(self) -> None:
        """Grab a PNG screenshot of the dashboard."""
        pixmap = self.grab()
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Dashboard Screenshot", "", "PNG Image (*.png)"
        )
        if path:
            try:
                pixmap.save(path, "PNG")
            except Exception:
                pass