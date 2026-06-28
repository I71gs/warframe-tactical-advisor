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
        from src.core.design_system import get_icon, SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL
        
        root = QVBoxLayout(self)
        root.setSpacing(SPACE_SM)

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
        self.glance_banner = QLabel("Today at a Glance:  —")
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

        screenshot_btn = QPushButton(" Export PNG")
        screenshot_btn.setIcon(get_icon("camera", size=16, color=accent))
        screenshot_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {card_bg}; border: 1px solid {accent};
                border-radius: 4px; color: {accent}; font-weight: bold; padding: 6px 12px;
            }}
            QPushButton:hover {{ background-color: rgba(255, 255, 255, 0.05); }}
        """)
        screenshot_btn.clicked.connect(self.export_screenshot)
        header_row.addWidget(screenshot_btn)

        refresh_btn = QPushButton(" Refresh")
        refresh_btn.setIcon(get_icon("refresh", size=16, color=accent))
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
        self.hero_top_rec = self._hero_chip("Recommendation: —", "#00d4ff", wide=True)

        for chip in (self.hero_mr, self.hero_stage, self.hero_score,
                     self.hero_sp, self.hero_uptime, self.hero_top_rec):
            hero_row.addWidget(chip)
        hero_row.addStretch()
        root.addLayout(hero_row)

        # ── Responsive Scroll Area ──────────────
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")
        
        self.cols_container = QWidget()
        self.cols_container.setStyleSheet("background: transparent;")
        self.cols_layout = QGridLayout(self.cols_container)
        self.cols_layout.setContentsMargins(0, 0, 0, 0)
        self.cols_layout.setSpacing(SPACE_SM)

        # ── 1. Left Column Layout (Briefings: Directive, Operations, Alerts) ──
        self.left_col_widget = QWidget()
        self.left_col_widget.setStyleSheet("background: transparent;")
        self.left_col_lay = QVBoxLayout(self.left_col_widget)
        self.left_col_lay.setContentsMargins(0, 0, 0, 0)
        self.left_col_lay.setSpacing(SPACE_MD)

        # Tactical Directive Card
        self.directive_card, self.directive_lay = _card("Tactical Directive", "#00d4ff", 140)
        self.active_goal_lbl = QLabel("Active Objective: —")
        self.active_goal_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #9fb6c8;")
        self.next_step_title = QLabel("NEXT RECOMMENDED STEP:")
        self.next_step_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #ffb76b; text-transform: uppercase;")
        self.next_step_lbl = QLabel("—")
        self.next_step_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #00d4ff; padding: 4px 0px;")
        self.directive_desc = QLabel("—")
        self.directive_desc.setStyleSheet("font-size: 11px; color: #eae6f8;")
        self.directive_desc.setWordWrap(True)
        self.directive_progress_bar = _progress_bar("#00d4ff", height=6)
        self.directive_progress_lbl = QLabel("—/— completed")
        self.directive_progress_lbl.setStyleSheet("font-size: 10px; color: #9fb6c8;")

        self.directive_lay.addWidget(self.active_goal_lbl)
        self.directive_lay.addWidget(self.next_step_title)
        self.directive_lay.addWidget(self.next_step_lbl)
        self.directive_lay.addWidget(self.directive_desc)
        prog_row = QHBoxLayout()
        prog_row.addWidget(self.directive_progress_bar, 1)
        prog_row.addWidget(self.directive_progress_lbl)
        self.directive_lay.addLayout(prog_row)

        self.left_col_lay.addWidget(self.directive_card)

        # Active Operations Card (Sortie + Fissures + Nightwave)
        self.ops_card, self.ops_lay = _card("Active Operations Briefing", "#ffb76b", 220)
        
        # Sortie Sub-section
        sortie_title = QLabel("DAILY SORTIE")
        sortie_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #ffb76b; text-transform: uppercase; margin-top: 4px;")
        self.sortie_desc_lbl = _row_label("Loading Daily Sortie...", bold=True)
        self.ops_lay.addWidget(sortie_title)
        self.ops_lay.addWidget(self.sortie_desc_lbl)

        # Nightwave Sub-section
        nw_title = QLabel("NIGHTWAVE INTELLIGENCE")
        nw_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #caa3ff; text-transform: uppercase; margin-top: 8px;")
        self.nw_desc_lbl = _row_label("Loading Nightwave Challenges...", bold=True)
        self.ops_lay.addWidget(nw_title)
        self.ops_lay.addWidget(self.nw_desc_lbl)

        # Priority Fissures Sub-section
        fissure_title = QLabel("PRIORITY VOID FISSURES")
        fissure_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #00d4ff; text-transform: uppercase; margin-top: 8px;")
        self.fissure_desc_lbl = _row_label("Loading Fissures...", bold=True)
        self.ops_lay.addWidget(fissure_title)
        self.ops_lay.addWidget(self.fissure_desc_lbl)

        self.ops_lay.addStretch()
        self.left_col_lay.addWidget(self.ops_card)

        # Urgent Alerts Card
        self.alerts_card, self.alerts_lay = _card("Urgent Operations & Limited Events", "#ff9fd4", 100)
        self.alerts_desc_lbl = _row_label("No urgent alerts detected.", bold=True)
        self.alerts_lay.addWidget(self.alerts_desc_lbl)
        self.alerts_lay.addStretch()
        self.left_col_lay.addWidget(self.alerts_card)


        # ── 2. Right Column Layout (Player Summary: MR, Warframes count, Standings, Warnings) ──
        self.right_col_widget = QWidget()
        self.right_col_widget.setStyleSheet("background: transparent;")
        self.right_col_lay = QVBoxLayout(self.right_col_widget)
        self.right_col_lay.setContentsMargins(0, 0, 0, 0)
        self.right_col_lay.setSpacing(SPACE_MD)

        # Player Summary Card
        self.status_card, self.status_lay = _card("Player Overview", "#caa3ff", 220)
        
        # Mastery Rank progress horizontal row (circle + text)
        mr_row = QHBoxLayout()
        self.mr_circle = CircleProgress(self, size=64, width=5.0, color="#caa3ff")
        
        mr_text_lay = QVBoxLayout()
        self.mr_title_lbl = QLabel("MASTERY PROFILE")
        self.mr_title_lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #caa3ff; text-transform: uppercase;")
        self.mr_detail_lbl = QLabel("MR —")
        self.mr_detail_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #e6eef6;")
        self.mr_xp_needed = QLabel("XP needed: —")
        self.mr_xp_needed.setStyleSheet("font-size: 10px; color: #9fb6c8;")
        mr_text_lay.addWidget(self.mr_title_lbl)
        mr_text_lay.addWidget(self.mr_detail_lbl)
        mr_text_lay.addWidget(self.mr_xp_needed)
        
        mr_row.addWidget(self.mr_circle)
        mr_row.addLayout(mr_text_lay, 1)
        self.status_lay.addLayout(mr_row)

        # Owned frames count badge
        self.owned_frames_lbl = _row_label("Owned: — / — Warframes", bold=True)
        self.status_lay.addWidget(self.owned_frames_lbl)

        # Weekly goals standing
        self.weekly_standing_lbl = QLabel("WEEKLY MILESTONES PROGRESS")
        self.weekly_standing_lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #7fb3ff; text-transform: uppercase; margin-top: 8px;")
        self.weekly_label = _row_label("—/— Goals met")
        self.weekly_progress_bar = _progress_bar("#7fb3ff", height=6)
        self.status_lay.addWidget(self.weekly_standing_lbl)
        self.status_lay.addWidget(self.weekly_label)
        self.status_lay.addWidget(self.weekly_progress_bar)

        # Key Resource summary indicators
        res_title = QLabel("TACTICAL RESOURCE VAULT")
        res_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #7fffb3; text-transform: uppercase; margin-top: 8px;")
        self.status_lay.addWidget(res_title)
        
        self.resource_summary_lbl = QLabel("Credits: —  |  Endo: —  |  Forma: —")
        self.resource_summary_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #7fffb3;")
        self.status_lay.addWidget(self.resource_summary_lbl)
        self.status_lay.addStretch()

        self.right_col_lay.addWidget(self.status_card)

        # Warnings Card
        self.warnings_card, self.warnings_lay = _card("Advisor Warnings & Alerts", "#ef4444", 120)
        self.warning_labels: list[QLabel] = []
        for _ in range(4):
            lbl = _row_label("—", color="#f87171")
            self.warnings_lay.addWidget(lbl)
            self.warning_labels.append(lbl)
        self.warnings_lay.addStretch()
        self.right_col_lay.addWidget(self.warnings_card)


        # ── 3. Below the Fold Layout (Void Trader, Arbitrations, Resource Bottlenecks) ──
        self.below_fold_sep = QFrame()
        self.below_fold_sep.setFrameShape(QFrame.HLine)
        self.below_fold_sep.setStyleSheet("color: #0f1724; border: 1px solid rgba(255, 255, 255, 0.05); margin: 15px 0px;")

        self.below_fold_header = QLabel("Tactical Intelligence & Archives")
        self.below_fold_header.setStyleSheet("font-size: 14px; font-weight: bold; color: #caa3ff;")

        self.below_fold_widget = QWidget()
        self.below_fold_widget.setStyleSheet("background: transparent;")
        self.below_fold_lay = QHBoxLayout(self.below_fold_widget)
        self.below_fold_lay.setContentsMargins(0, 0, 0, 0)
        self.below_fold_lay.setSpacing(SPACE_SM)

        # Card A: Baro Ki'Teer & Arbitrations
        self.baro_card, self.baro_lay = _card("Baro Ki'Teer & Arbitrations", "#ffb76b", 160)
        self.baro_desc = _row_label("Void Trader: loading...")
        self.arbitration_desc = _row_label("Arbitration: loading...")
        self.baro_lay.addWidget(self.baro_desc)
        self.baro_lay.addWidget(self.arbitration_desc)
        self.baro_lay.addStretch()
        self.below_fold_lay.addWidget(self.baro_card, 1)

        # Card B: Resource Bottlenecks
        self.econ_card, self.econ_lay = _card("Resource Bottlenecks", "#ff9fd4", 160)
        self.econ_labels: list[QLabel] = []
        for _ in range(4):
            lbl = _row_label("—")
            self.econ_lay.addWidget(lbl)
            self.econ_labels.append(lbl)
        self.econ_lay.addStretch()
        self.below_fold_lay.addWidget(self.econ_card, 1)

        # Card C: System Status & Steel Path
        self.sys_card, self.sys_lay = _card("Honors & Milestones", "#7fffb3", 160)
        self.sp_desc_lbl = _row_label("Steel Path: loading...")
        self.sys_lay.addWidget(self.sp_desc_lbl)
        self.sys_lay.addStretch()
        self.below_fold_lay.addWidget(self.sys_card, 1)

        # Default mapping to columns
        self.cols_layout.addWidget(self.left_col_widget, 0, 0)
        self.cols_layout.addWidget(self.right_col_widget, 0, 1)
        self.cols_layout.addWidget(self.below_fold_sep, 1, 0, 1, 2)
        self.cols_layout.addWidget(self.below_fold_header, 2, 0, 1, 2)
        self.cols_layout.addWidget(self.below_fold_widget, 3, 0, 1, 2)
        self._current_bp = "standard"

        self.scroll_area.setWidget(self.cols_container)
        root.addWidget(self.scroll_area, 1)

    def resizeEvent(self, event: Any) -> None:
        super().resizeEvent(event)
        self.adjust_layout_to_width(self.width())

    def adjust_layout_to_width(self, width: int) -> None:
        """Dynamically re-assign columns to grid cells based on window width."""
        if width <= 1100:
            bp = "compact"
        else:
            bp = "standard"
             
        if hasattr(self, "_current_bp") and self._current_bp == bp:
            return
             
        self._current_bp = bp
        self.setUpdatesEnabled(False)
         
        # Detach widgets from layout
        self.cols_layout.removeWidget(self.left_col_widget)
        self.cols_layout.removeWidget(self.right_col_widget)
        self.cols_layout.removeWidget(self.below_fold_sep)
        self.cols_layout.removeWidget(self.below_fold_header)
        self.cols_layout.removeWidget(self.below_fold_widget)
         
        if bp == "compact":
            # 1 column stacked layout
            self.cols_layout.addWidget(self.left_col_widget, 0, 0)
            self.cols_layout.addWidget(self.right_col_widget, 1, 0)
            self.cols_layout.addWidget(self.below_fold_sep, 2, 0)
            self.cols_layout.addWidget(self.below_fold_header, 3, 0)
            self.cols_layout.addWidget(self.below_fold_widget, 4, 0)
            self.cols_layout.setColumnStretch(0, 1)
            self.cols_layout.setColumnStretch(1, 0)
        else:
            # 2 columns layout (60% Left column, 40% Right column)
            self.cols_layout.addWidget(self.left_col_widget, 0, 0)
            self.cols_layout.addWidget(self.right_col_widget, 0, 1)
            self.cols_layout.addWidget(self.below_fold_sep, 1, 0, 1, 2)
            self.cols_layout.addWidget(self.below_fold_header, 2, 0, 1, 2)
            self.cols_layout.addWidget(self.below_fold_widget, 3, 0, 1, 2)
            self.cols_layout.setColumnStretch(0, 6)
            self.cols_layout.setColumnStretch(1, 4)
             
        self.setUpdatesEnabled(True)
        self.update()
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

        # Hero row & score stats
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
        self.sub_title.setText(f"Tactical Advisor Last Refreshed: {QDateTime.currentDateTime().toString('ddd dd MMM yyyy  hh:mm:ss')}")
        self.glance_banner.setText(f"Today at a Glance:  MR {player.mastery_rank}  ·  Score {score}%  ·  🎯 {top_rec[:40]}")

        # 1. Primary Left Focus — Tactical Directive
        if stage == "early_game" or stage == "mid_game":
            active_goal = "Finish Main Story"
        elif stage == "late_game":
            active_goal = "Unlock Steel Path"
        else:
            active_goal = "Become Archon Ready"

        from src.core.goal_planner import GoalPlanner
        gp = GoalPlanner()
        plan_steps = gp.get_goal_plan(player, active_goal)
        
        if plan_steps:
            total = len(plan_steps)
            completed = sum(1 for s in plan_steps if s["completed"])
            pct = int(completed / total * 100) if total else 0
            
            uncompleted = [s for s in plan_steps if not s["completed"]]
            if uncompleted:
                next_step = uncompleted[0]["step"]
                unmet = uncompleted[0]["unmet"]
                unmet_text = f"Prerequisite needed: {', '.join(unmet)}" if unmet else "All pre-requisites met. Ready to execute."
            else:
                next_step = "All objectives achieved!"
                unmet_text = "Tactical operations fully completed."
                
            self.active_goal_lbl.setText(f"Active Objective: {active_goal}")
            self.next_step_lbl.setText(next_step)
            self.directive_desc.setText(unmet_text)
            self.directive_progress_bar.setValue(pct)
            self.directive_progress_lbl.setText(f"{completed}/{total} completed")
        else:
            self.active_goal_lbl.setText("Active Objective: General Progression")
            self.next_step_lbl.setText(top_rec)
            self.directive_desc.setText("Follow recommended steps to progress.")
            self.directive_progress_bar.setValue(score)
            self.directive_progress_lbl.setText(f"{score}% account score")

        # 2. Right Focus — Mastery Profiler & XP Tracker
        try:
            from src.core.mastery_planner import MasteryPlanner
            mp = MasteryPlanner()
            plan_mr = mp.calculate_plan(player)
            mr_pct = int(player.mastery_rank / 30 * 100)
            self.mr_circle.setValue(mr_pct)
            self.mr_detail_lbl.setText(f"Rank {player.mastery_rank}")
            self.mr_xp_needed.setText(f"XP needed to next: {plan_mr['xp_needed']:,}")
        except Exception:
            self.mr_circle.setValue(int(player.mastery_rank / 30 * 100))
            self.mr_detail_lbl.setText(f"Rank {player.mastery_rank}")
            self.mr_xp_needed.setText("XP needed: —")

        # Owned frames inventory count
        from src.core.collection_engine import WARFRAME_ROSTER
        total_frames = len(WARFRAME_ROSTER)
        owned_frames = len(player.owned_warframes)
        self.owned_frames_lbl.setText(f"Owned: {owned_frames} / {total_frames} Warframes")

        # Weekly stand / goals
        try:
            from src.core.weekly_planner import WeeklyPlanner
            wp = WeeklyPlanner()
            weeklies = wp.get_weekly_state(player)
            total_w = len(weeklies.get("goals", []))
            done_w = sum(1 for g in weeklies.get("goals", []) if g.get("completed"))
            self.weekly_label.setText(f"{done_w}/{total_w} weekly goals met")
            self.weekly_progress_bar.setValue(int(done_w / total_w * 100) if total_w else 0)
        except Exception:
            total_w, done_w = 5, 2
            self.weekly_label.setText("2/5 weekly goals met")
            self.weekly_progress_bar.setValue(40)

        # Tactical Vault Resources summary
        from src.core.resource_engine import ResourceEngine
        re = ResourceEngine()
        owned_res = re.load_owned_resources()
        self.resource_summary_lbl.setText(
            f"Credits: {owned_res.get('Credits', 0):,}  |  Endo: {owned_res.get('Endo', 0):,}  |  Forma: {owned_res.get('Forma', 0)}"
        )

        # Live World State Refresh (Sortie, Nightwave, Fissures, baro trader)
        self._refresh_world_state()

        # Advisor Warnings & Alerts List
        warnings = []
        if not player.steel_path_unlocked and stage == "late_game":
            warnings.append("⚠ Steel Path is locked: complete remaining Star Chart nodes.")
        if total_w and done_w < total_w:
            warnings.append(f"⚠ Weekly standing limits: {total_w - done_w} syndicate milestones remaining.")
            
        from src.core.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        missing_mods = [m["name"] for m in kb.mods if m["name"].lower() not in {x.lower() for x in player.owned_mods}]
        if missing_mods:
            warnings.append(f"⚠ Missing {len(missing_mods)} recommended mods (e.g. {missing_mods[0]})")
            
        from src.core.economy_engine import EconomyEngine
        ee = EconomyEngine()
        bots = ee.get_bottleneck_resources(top_n=2)
        for b in bots:
            warnings.append(f"⚠ Missing {b['missing']:,} {b['resource']} for crafting builds.")
            
        for i, lbl in enumerate(self.warning_labels):
            if i < len(warnings):
                lbl.setText(warnings[i])
                lbl.setVisible(True)
            else:
                lbl.setText("")
                lbl.setVisible(False)

        # below the fold economy & SP details
        econ_items = []
        all_bots = ee.get_bottleneck_resources(top_n=4)
        for b in all_bots:
            econ_items.append(f"⚠ {b['resource']}: need {b['missing']:,} ({b['farm_hours']}h)")
        for i, lbl in enumerate(self.econ_labels):
            lbl.setText(econ_items[i] if i < len(econ_items) else "—")

        self.sp_desc_lbl.setText("✓ Steel Path Unlocked" if player.steel_path_unlocked else "✗ Steel Path Locked")
        self.arbitration_desc.setText("Arbitrations Unlocked" if player.arbitrations_unlocked else "Clear Star Chart to unlock Arbitrations")

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
            self.fissure_desc_lbl.setText(fissure_text)

            alert = state.get("alerts", [{}])[0] if state.get("alerts") else {}
            alert_text = alert.get("mission", {}).get("reward", {}).get("asString", "None") if alert else "None"
            self.alerts_desc_lbl.setText(f"Active Event Reward: {alert_text}" if alert_text != "None" else "No urgent alerts detected.")

            sortie = state.get("sortie", {})
            sortie_text = f"{sortie.get('boss', '?')} ({sortie.get('faction', '?')}) — {sortie.get('variants', [{}])[0].get('missionType', '?') if sortie.get('variants') else '?'}" if sortie else "Unavailable"
            self.sortie_desc_lbl.setText(sortie_text)

            nightwave = state.get("nightwave", {})
            nw_text = "Unavailable"
            if nightwave:
                challenges = nightwave.get("activeChallenges", [])
                if challenges:
                    nw_text = f"{challenges[0].get('title', 'Challenge')}: {challenges[0].get('desc', 'Task')}"
                else:
                    nw_text = f"Season {nightwave.get('season', '?')} Phase {nightwave.get('phase', '?')}"
            self.nw_desc_lbl.setText(nw_text)

            baro = state.get("voidTrader", {})
            baro_text = "Baro Ki'Teer: visiting " + baro.get("location", "Unknown") if baro.get("active") else "Baro Ki'Teer: Not visiting"
            self.baro_desc.setText(baro_text)

        except Exception:
            self.fissure_desc_lbl.setText("Fissures: Offline")
            self.sortie_desc_lbl.setText("Sortie: Offline")
            self.nw_desc_lbl.setText("Nightwave: Offline")
            self.alerts_desc_lbl.setText("No urgent alerts detected.")
            self.baro_desc.setText("Void Trader: Offline")

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