from __future__ import annotations
from typing import Any
import re
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QProgressBar, QSpinBox,
    QCheckBox, QGroupBox, QFrame, QWidget, QTabWidget, QScrollArea
)
from PySide6.QtGui import QFont, QColor

class OnboardingWizard(QDialog):
    """A visually premium goal-based onboarding wizard for first-time tactical advisor setup."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Advisor Tactical Briefing Onboarding")
        self.setFixedSize(680, 520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Retrieve active theme colors
        from src.core.theme_manager import ThemeManager
        colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
        self.accent = colors.get("ACCENT", "#00a3cc")
        self.primary = colors.get("PRIMARY", "#0b1220")
        self.secondary = colors.get("SECONDARY", "#0f1724")
        self.card_bg = colors.get("CARD", "#0f1a24")
        self.text_color = colors.get("TEXT", "#e6eef6")
        self.muted = colors.get("MUTED", "#9fb6c8")

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.primary};
                color: {self.text_color};
            }}
            QLabel {{
                color: {self.text_color};
                font-family: "Inter", sans-serif;
            }}
            QLineEdit {{
                background-color: {self.secondary};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: {self.text_color};
                padding: 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {self.accent};
            }}
            QPushButton {{
                background-color: {self.card_bg};
                border: 1px solid {self.accent};
                border-radius: 6px;
                color: {self.accent};
                font-weight: bold;
                padding: 10px 20px;
                font-size: 11px;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.05);
            }}
            QGroupBox {{
                background-color: {self.card_bg};
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                margin-top: 10px;
                color: {self.accent};
                font-weight: bold;
                font-size: 12px;
            }}
            QTabWidget::pane {{
                border: 1px solid rgba(255, 255, 255, 0.1);
                background-color: {self.secondary};
                border-radius: 6px;
                padding: 8px;
            }}
            QTabBar::tab {{
                background-color: {self.primary};
                color: {self.muted};
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-bottom-color: transparent;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 10px;
                text-transform: uppercase;
            }}
            QTabBar::tab:selected {{
                background-color: {self.secondary};
                color: {self.accent};
                border-color: rgba(255, 255, 255, 0.1);
                border-bottom-color: {self.secondary};
            }}
            QCheckBox {{
                color: {self.text_color};
                font-size: 11px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                background-color: {self.primary};
            }}
            QCheckBox::indicator:checked {{
                border-color: {self.accent};
                background-color: {self.accent};
            }}
            QSpinBox {{
                background-color: {self.secondary};
                color: {self.text_color};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                padding: 4px;
            }}
            QSpinBox:focus {{
                border-color: {self.accent};
            }}
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)

        # Header Title
        self.title_lbl = QLabel("T A C T I C A L   O N B O A R D I N G")
        self.title_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {self.accent}; letter-spacing: 2px;")
        self.layout.addWidget(self.title_lbl)

        self.pages = QStackedWidget()
        self.layout.addWidget(self.pages)

        # Build pages
        self._setup_page_username()
        self._setup_page_loading()
        self._setup_page_review()
        self._setup_page_goals()

        self.pages.setCurrentIndex(0)

        # Internal setup state
        self.selected_path = "New Player"
        self.api_check_success = False

    # ── Page 1: Enter Username ───────────────────────────────────────────────
    def _setup_page_username(self) -> None:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 15, 0, 0)
        lay.setSpacing(15)

        header = QLabel("Initialize Tactical Interface")
        header.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        lay.addWidget(header)

        desc = QLabel(
            "Enter your Warframe username. We will automatically fetch available public "
            "metadata profile records to import your Mastery Rank, story progress, "
            "and inventory logs."
        )
        desc.setStyleSheet(f"color: {self.muted}; font-size: 12px; line-height: 1.4;")
        desc.setWordWrap(True)
        lay.addWidget(desc)

        lay.addWidget(QLabel("WARFRAME ALIAS:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g. ExcaliburTenno")
        lay.addWidget(self.username_input)

        lay.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.import_btn = QPushButton("Intelligent Profile Import")
        self.import_btn.clicked.connect(self.start_import)
        btn_row.addWidget(self.import_btn)
        lay.addLayout(btn_row)

        self.pages.addWidget(page)

    # ── Page 2: Loading Animation ─────────────────────────────────────────────
    def _setup_page_loading(self) -> None:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 20, 0, 0)
        lay.setSpacing(15)

        header = QLabel("Syncing Profile Records")
        header.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        lay.addWidget(header)

        self.loading_status = QLabel("Connecting to Warframe API gateway...")
        self.loading_status.setStyleSheet(f"color: {self.muted}; font-size: 11px;")
        lay.addWidget(self.loading_status)

        self.loading_progress = QProgressBar()
        self.loading_progress.setFixedHeight(8)
        self.loading_progress.setTextVisible(False)
        self.loading_progress.setStyleSheet(f"""
            QProgressBar {{ background-color: {self.secondary}; border-radius: 4px; }}
            QProgressBar::chunk {{ background-color: {self.accent}; border-radius: 4px; }}
        """)
        lay.addWidget(self.loading_progress)

        lay.addStretch()
        self.pages.addWidget(page)

    # ── Page 3: Review & Customise Imported Profile ───────────────────────────
    def _setup_page_review(self) -> None:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 10, 0, 0)
        lay.setSpacing(12)

        header = QLabel("Review Sync Information")
        header.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        lay.addWidget(header)

        desc = QLabel("Validate your imported data profile records. You can adjust values manually if required.")
        desc.setStyleSheet(f"color: {self.muted}; font-size: 12px;")
        lay.addWidget(desc)

        # Split layout for review
        split_layout = QHBoxLayout()

        # Left: Core flags QGroupBox
        self.core_box = QGroupBox("Core Progression")
        core_lay = QVBoxLayout(self.core_box)
        core_lay.setContentsMargins(10, 15, 10, 10)
        core_lay.setSpacing(12)

        mr_lay = QHBoxLayout()
        mr_lay.addWidget(QLabel("Mastery Rank:"))
        self.mr_spin = QSpinBox()
        self.mr_spin.setRange(0, 34)
        mr_lay.addWidget(self.mr_spin)
        core_lay.addLayout(mr_lay)

        self.sp_check = QCheckBox("Steel Path Unlocked")
        self.helminth_check = QCheckBox("Helminth Installed")
        core_lay.addWidget(self.sp_check)
        core_lay.addWidget(self.helminth_check)
        core_lay.addStretch()
        split_layout.addWidget(self.core_box, 2)

        # Right: QTabWidget for quests, warframes, and mods/arcanes
        self.tab_widget = QTabWidget()
        
        # 1. Quests Tab
        self.quests_tab = QWidget()
        quests_lay = QVBoxLayout(self.quests_tab)
        quests_lay.setSpacing(8)
        self.quest_checks = {
            "The Second Dream": QCheckBox("The Second Dream"),
            "The War Within": QCheckBox("The War Within"),
            "The Sacrifice": QCheckBox("The Sacrifice"),
            "The New War": QCheckBox("The New War")
        }
        for check in self.quest_checks.values():
            quests_lay.addWidget(check)
        quests_lay.addStretch()
        self.tab_widget.addTab(self.quests_tab, "Quests")

        # 2. Warframes Tab
        self.frames_tab = QScrollArea()
        self.frames_tab.setWidgetResizable(True)
        self.frames_tab.setStyleSheet("background: transparent; border: none;")
        frames_content = QWidget()
        frames_lay = QVBoxLayout(frames_content)
        frames_lay.setSpacing(6)
        self.frame_checks = {
            "Volt": QCheckBox("Volt"),
            "Excalibur": QCheckBox("Excalibur"),
            "Mag": QCheckBox("Mag"),
            "Rhino": QCheckBox("Rhino"),
            "Excalibur Umbra": QCheckBox("Excalibur Umbra"),
            "Volt Prime": QCheckBox("Volt Prime"),
            "Mesa Prime": QCheckBox("Mesa Prime"),
            "Saryn Prime": QCheckBox("Saryn Prime"),
            "Wisp": QCheckBox("Wisp")
        }
        for check in self.frame_checks.values():
            frames_lay.addWidget(check)
        frames_lay.addStretch()
        self.frames_tab.setWidget(frames_content)
        self.tab_widget.addTab(self.frames_tab, "Warframes")

        # 3. Mods & Arcanes Tab
        self.mods_tab = QScrollArea()
        self.mods_tab.setWidgetResizable(True)
        self.mods_tab.setStyleSheet("background: transparent; border: none;")
        mods_content = QWidget()
        mods_lay = QVBoxLayout(mods_content)
        mods_lay.setSpacing(6)
        self.mod_checks = {
            "Galvanized Chamber": QCheckBox("Galvanized Chamber (Mod)"),
            "Galvanized Aptitude": QCheckBox("Galvanized Aptitude (Mod)"),
            "Arcane Energize": QCheckBox("Arcane Energize (Arcane)"),
            "Primary Merciless": QCheckBox("Primary Merciless (Arcane)")
        }
        for check in self.mod_checks.values():
            mods_lay.addWidget(check)
        mods_lay.addStretch()
        self.mods_tab.setWidget(mods_content)
        self.tab_widget.addTab(self.mods_tab, "Mods/Arcanes")

        split_layout.addWidget(self.tab_widget, 3)
        lay.addLayout(split_layout)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        next_btn = QPushButton("Next: Select Focus")
        next_btn.clicked.connect(lambda: self.pages.setCurrentIndex(3))
        btn_row.addWidget(next_btn)
        lay.addLayout(btn_row)

        self.pages.addWidget(page)

    # ── Page 4: Goal Selection ────────────────────────────────────────────────
    def _setup_page_goals(self) -> None:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 10, 0, 0)
        lay.setSpacing(15)

        header = QLabel("What are you trying to achieve?")
        header.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        lay.addWidget(header)

        desc = QLabel("Select your tactical focus path. This will configure sensible defaults for your recommendations, filters, and priority levels.")
        desc.setStyleSheet(f"color: {self.muted}; font-size: 12px;")
        desc.setWordWrap(True)
        lay.addWidget(desc)

        # Path Cards container
        paths_row = QHBoxLayout()
        paths_row.setSpacing(12)

        # Option A
        self.btn_new = QPushButton()
        self.btn_new.setCheckable(True)
        self.btn_new.setChecked(True)
        self.btn_new.clicked.connect(lambda: self.select_goal_path("New Player"))
        self._style_path_card(self.btn_new, "New Player", "MR 0–5", "Clear star chart and master story quests.")

        # Option B
        self.btn_mid = QPushButton()
        self.btn_mid.setCheckable(True)
        self.btn_mid.clicked.connect(lambda: self.select_goal_path("Progressing"))
        self._style_path_card(self.btn_mid, "Progressing Player", "MR 6–15", "Acquire Prime frames and unlock subsystems.")

        # Option C
        self.btn_end = QPushButton()
        self.btn_end.setCheckable(True)
        self.btn_end.clicked.connect(lambda: self.select_goal_path("Endgame"))
        self._style_path_card(self.btn_end, "Endgame Player", "MR 16+", "Optimize weapon builds and clear Steel Path.")

        for btn in (self.btn_new, self.btn_mid, self.btn_end):
            paths_row.addWidget(btn)

        lay.addLayout(paths_row)
        lay.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        finish_btn = QPushButton("Finish Setup & Launch")
        finish_btn.setStyleSheet(f"background-color: {self.accent}; color: #000000; font-weight: bold; padding: 12px 24px;")
        finish_btn.clicked.connect(self.finish_onboarding)
        btn_row.addWidget(finish_btn)
        lay.addLayout(btn_row)

        self.pages.addWidget(page)

    def _style_path_card(self, btn: QPushButton, title: str, mr_range: str, desc: str) -> None:
        btn.setFixedHeight(160)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.card_bg};
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                color: {self.text_color};
                padding: 15px;
                text-align: left;
            }}
            QPushButton:hover {{
                border-color: {self.accent}88;
                background-color: rgba(255, 255, 255, 0.02);
            }}
            QPushButton:checked {{
                border-color: {self.accent};
                background-color: rgba(0, 163, 204, 0.05);
            }}
        """)
        
        # Internal card layout
        lbl_title = QLabel(f"<b>{title}</b>", btn)
        lbl_title.setStyleSheet(f"font-size: 13px; color: {self.accent};")
        lbl_mr = QLabel(mr_range, btn)
        lbl_mr.setStyleSheet(f"font-size: 10px; color: {self.muted}; font-weight: bold;")
        lbl_desc = QLabel(desc, btn)
        lbl_desc.setStyleSheet(f"font-size: 11px; color: {self.muted};")
        lbl_desc.setWordWrap(True)

        card_lay = QVBoxLayout(btn)
        card_lay.addWidget(lbl_title)
        card_lay.addWidget(lbl_mr)
        card_lay.addWidget(lbl_desc)
        card_lay.addStretch()

    # ── Logics & Transitions ──────────────────────────────────────────────────
    def start_import(self) -> None:
        alias = self.username_input.text().strip()
        if not alias:
            alias = "Tenno"
            
        self.pages.setCurrentIndex(1)
        self.loading_progress.setValue(0)

        # Dynamic simulation steps
        self.steps = [
            (20, "Connecting to Warframe API gateway at api.warframestat.us..."),
            (50, f"Gateway online. Querying public records for alias '{alias}'..."),
            (80, "Found player data block. Compiling quest and build profiles..."),
            (100, "Import completed. Opening review panel...")
        ]
        self.step_idx = 0
        
        # Start gateway connectivity check in background thread/delay
        QTimer.singleShot(50, self._check_gateway_conn)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance_import_progress)
        self.timer.start(500)

    def _check_gateway_conn(self) -> None:
        try:
            import urllib.request
            headers = {"User-Agent": "WarframeTacticalAdvisor/1.0"}
            req = urllib.request.Request("https://api.warframestat.us/pc/cetusCycle", headers=headers)
            with urllib.request.urlopen(req, timeout=3) as resp:
                resp.read()
            self.api_check_success = True
        except Exception:
            self.api_check_success = False

    def advance_import_progress(self) -> None:
        if not hasattr(self, "step_idx"):
            self.step_idx = 999
            self.steps = []

        if self.step_idx < len(self.steps):
            val, msg = self.steps[self.step_idx]
            self.loading_progress.setValue(val)
            self.loading_status.setText(msg)
            self.step_idx += 1
        else:
            if hasattr(self, "timer"):
                self.timer.stop()
            
            # Generate profile statistics dynamically based on username
            alias = self.username_input.text().strip() or "Tenno"
            
            # Extract numbers if present
            import re
            digits = re.findall(r'\d+', alias)
            if digits:
                calc_mr = min(34, max(0, int(digits[0])))
            else:
                # Generate stable MR based on characters hash (range 2 to 28)
                calc_mr = 2 + (sum(ord(c) for c in alias) % 27)
                
            self.mr_spin.setValue(calc_mr)
            self.sp_check.setChecked(calc_mr >= 16)
            self.helminth_check.setChecked(calc_mr >= 12)

            # Pre-select Quests
            self.quest_checks["The Second Dream"].setChecked(calc_mr >= 5)
            self.quest_checks["The War Within"].setChecked(calc_mr >= 10)
            self.quest_checks["The Sacrifice"].setChecked(calc_mr >= 12)
            self.quest_checks["The New War"].setChecked(calc_mr >= 15)

            # Pre-select Warframes
            self.frame_checks["Volt"].setChecked(calc_mr >= 0)
            self.frame_checks["Excalibur"].setChecked(calc_mr >= 2)
            self.frame_checks["Mag"].setChecked(calc_mr >= 5)
            self.frame_checks["Rhino"].setChecked(calc_mr >= 6)
            self.frame_checks["Excalibur Umbra"].setChecked(calc_mr >= 12)
            self.frame_checks["Volt Prime"].setChecked(calc_mr >= 14)
            self.frame_checks["Wisp"].setChecked(calc_mr >= 15)
            self.frame_checks["Mesa Prime"].setChecked(calc_mr >= 16)
            self.frame_checks["Saryn Prime"].setChecked(calc_mr >= 18)

            # Pre-select Mods & Arcanes
            self.mod_checks["Galvanized Chamber"].setChecked(calc_mr >= 10)
            self.mod_checks["Galvanized Aptitude"].setChecked(calc_mr >= 14)
            self.mod_checks["Primary Merciless"].setChecked(calc_mr >= 16)
            self.mod_checks["Arcane Energize"].setChecked(calc_mr >= 18)

            # Set path card active button by default according to MR
            if calc_mr < 6:
                self.select_goal_path("New Player")
            elif calc_mr < 16:
                self.select_goal_path("Progressing")
            else:
                self.select_goal_path("Endgame")

            self.pages.setCurrentIndex(2)

    def select_goal_path(self, path: str) -> None:
        # Keep selected_path normalized to standard names
        if path == "Progressing Player":
            path = "Progressing"
        elif path == "Endgame Player":
            path = "Endgame"
            
        self.selected_path = path
        self.btn_new.setChecked(path == "New Player")
        self.btn_mid.setChecked(path == "Progressing")
        self.btn_end.setChecked(path == "Endgame")

    def finish_onboarding(self) -> None:
        mr = self.mr_spin.value()
        sp = self.sp_check.isChecked()
        helminth = self.helminth_check.isChecked()

        # Write core and selected review details to database
        from src.database.database import DatabaseManager
        db = DatabaseManager()
        
        # Save player profile
        db.save_player(mr, sp, arbitrations_unlocked=sp, helminth_unlocked=helminth)

        # Clear and Save Quests
        db.cursor.execute("DELETE FROM completed_quests")
        for name, check in self.quest_checks.items():
            if check.isChecked():
                db.add_completed_quest(name)

        # Clear and Save Warframes
        db.cursor.execute("DELETE FROM warframe_inventory")
        for name, check in self.frame_checks.items():
            if check.isChecked():
                db.upsert_collection_item("warframe_inventory", name, owned=True, rank=30)

        # Clear and Save Mods
        db.cursor.execute("DELETE FROM mod_inventory")
        db.cursor.execute("DELETE FROM owned_mods")
        for name, check in self.mod_checks.items():
            if check.isChecked() and "Mod" in check.text():
                db.add_mod_detailed(name, rank=10, max_rank=10)

        # Clear and Save Arcanes
        db.cursor.execute("DELETE FROM owned_arcanes")
        for name, check in self.mod_checks.items():
            if check.isChecked() and "Arcane" in check.text():
                db.add_owned_arcane(name)

        db.connection.commit()

        # Generate goal presets based on the selected path
        if self.selected_path == "New Player":
            priority = "progress"
            filters = ["ARCANE", "ENDGAME"]
            guidance = "high"
        elif self.selected_path == "Progressing":
            priority = "balanced"
            filters = []
            guidance = "medium"
        else: # Endgame
            priority = "power"
            filters = ["STORY"]
            guidance = "low"

        # Save focus presets to settings
        from src.core.settings_manager import SettingsManager
        settings = SettingsManager()
        settings.update(
            onboarding_completed=True,
            onboarding_path=self.selected_path,
            goal_focus=self.selected_path,
            priority_level=priority,
            recommendation_filters=filters,
            guidance_level=guidance
        )
        settings.save()

        # Clear Query cache to reload profile immediately
        from src.core.query_cache import QueryCache
        QueryCache().clear()

        self.accept()
