from __future__ import annotations
from typing import Any
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QProgressBar, QSpinBox,
    QCheckBox, QGroupBox, QFrame, QWidget
)
from PySide6.QtGui import QFont, QColor

class OnboardingWizard(QDialog):
    """A visually premium goal-based onboarding wizard for first-time tactical advisor setup."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Advisor Tactical Briefing Onboarding")
        self.setFixedSize(560, 420)
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
                border-radius: 4px;
                color: {self.text_color};
                padding: 8px;
                font-size: 12px;
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
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                margin-top: 10px;
                color: {self.accent};
                font-weight: bold;
            }}
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Header Title
        self.title_lbl = QLabel("T A C T I C A L   O N B O A R D I N G")
        self.title_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {self.accent}; letter-spacing: 2px;")
        self.layout.addWidget(self.title_lbl)

        self.pages = QStackedWidget()
        self.layout.addWidget(self.pages)

        self._setup_page_username()
        self._setup_page_loading()
        self._setup_page_review()
        self._setup_page_goals()

        self.pages.setCurrentIndex(0)

        # Temporary internal states
        self.imported_mr = 1
        self.imported_sp = False
        self.selected_path = "New Player"

    # ── Page 1: Enter Username ───────────────────────────────────────────────
    def _setup_page_username(self) -> None:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 10, 0, 0)
        lay.setSpacing(15)

        header = QLabel("Initialize Tactical Interface")
        header.setStyleSheet("font-size: 18px; font-weight: 800; color: #ffffff;")
        lay.addWidget(header)

        desc = QLabel(
            "Enter your Warframe username. We will analyze public metadata profile "
            "records to automatically import your Mastery Rank, completed quest history, "
            "and build readiness scores."
        )
        desc.setStyleSheet(f"color: {self.muted}; font-size: 11px; line-height: 1.4;")
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

        header = QLabel("Analyzing Profile Records")
        header.setStyleSheet("font-size: 18px; font-weight: 800; color: #ffffff;")
        lay.addWidget(header)

        self.loading_status = QLabel("Connecting to Warframe metadata servers...")
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

    # ── Page 3: Review Imported Profile ────────────────────────────────────────
    def _setup_page_review(self) -> None:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 10, 0, 0)
        lay.setSpacing(12)

        header = QLabel("Review Sync Information")
        header.setStyleSheet("font-size: 18px; font-weight: 800; color: #ffffff;")
        lay.addWidget(header)

        desc = QLabel("Validate your imported data profile records below. You can adjust values manually if required.")
        desc.setStyleSheet(f"color: {self.muted}; font-size: 11px;")
        lay.addWidget(desc)

        self.review_box = QGroupBox("Imported Metadata Profile")
        box_lay = QVBoxLayout(self.review_box)
        box_lay.setContentsMargins(10, 15, 10, 10)
        box_lay.setSpacing(10)

        # Mastery Rank Spinner
        mr_row = QHBoxLayout()
        mr_row.addWidget(QLabel("Mastery Rank:"))
        self.mr_spin = QSpinBox()
        self.mr_spin.setRange(0, 34)
        self.mr_spin.setStyleSheet(f"background-color: {self.secondary}; color: {self.text_color}; border-radius: 4px; padding: 4px;")
        mr_row.addWidget(self.mr_spin)
        box_lay.addLayout(mr_row)

        # Steel Path Checkbox
        self.sp_check = QCheckBox("Steel Path Mode Unlocked")
        self.sp_check.setStyleSheet(f"color: {self.text_color};")
        box_lay.addWidget(self.sp_check)

        # Helminth Checkbox
        self.helminth_check = QCheckBox("Helminth System Installed")
        self.helminth_check.setStyleSheet(f"color: {self.text_color};")
        box_lay.addWidget(self.helminth_check)

        lay.addWidget(self.review_box)
        lay.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        next_btn = QPushButton("Next: Select Path")
        next_btn.clicked.connect(lambda: self.pages.setCurrentIndex(3))
        btn_row.addWidget(next_btn)
        lay.addLayout(btn_row)

        self.pages.addWidget(page)

    # ── Page 4: Goal Selection ────────────────────────────────────────────────
    def _setup_page_goals(self) -> None:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 10, 0, 0)
        lay.setSpacing(12)

        header = QLabel("What are you trying to achieve?")
        header.setStyleSheet("font-size: 18px; font-weight: 800; color: #ffffff;")
        lay.addWidget(header)

        desc = QLabel("Select your tactical focus paths to automatically preset advisors configuration settings.")
        desc.setStyleSheet(f"color: {self.muted}; font-size: 11px;")
        lay.addWidget(desc)

        # Path Cards container
        paths_row = QHBoxLayout()

        # Option A
        self.btn_new = QPushButton("New Player\n(MR 0-5)")
        self.btn_new.setCheckable(True)
        self.btn_new.setChecked(True)
        self.btn_new.clicked.connect(lambda: self.select_goal_path("New Player"))

        # Option B
        self.btn_mid = QPushButton("Progressing\n(MR 6-15)")
        self.btn_mid.setCheckable(True)
        self.btn_mid.clicked.connect(lambda: self.select_goal_path("Progressing"))

        # Option C
        self.btn_end = QPushButton("Endgame\n(MR 16+)")
        self.btn_end.setCheckable(True)
        self.btn_end.clicked.connect(lambda: self.select_goal_path("Endgame"))

        for btn in (self.btn_new, self.btn_mid, self.btn_end):
            btn.setFixedHeight(80)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.card_bg};
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    color: {self.text_color};
                    font-weight: bold;
                    font-size: 12px;
                }}
                QPushButton:checked {{
                    border-color: {self.accent};
                    background-color: rgba(0, 163, 204, 0.05);
                    color: {self.accent};
                }}
            """)
            paths_row.addWidget(btn)

        lay.addLayout(paths_row)
        lay.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        finish_btn = QPushButton("Finish Setup & Launch")
        finish_btn.setStyleSheet(f"background-color: {self.accent}; color: #000000; font-weight: bold;")
        finish_btn.clicked.connect(self.finish_onboarding)
        btn_row.addWidget(finish_btn)
        lay.addLayout(btn_row)

        self.pages.addWidget(page)

    # ── Logics & Transitions ──────────────────────────────────────────────────
    def start_import(self) -> None:
        alias = self.username_input.text().strip()
        if not alias:
            alias = "Tenno"
            
        self.pages.setCurrentIndex(1)
        self.loading_progress.setValue(0)

        # Dynamic simulation steps
        self.steps = [
            (20, "Querying public Warframe API database records..."),
            (50, f"Syncing metadata profile for: '{alias}'..."),
            (85, "Analyzing completed story quests & mod tiers catalog..."),
            (100, "Hydration completed successfully!")
        ]
        self.step_idx = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance_import_progress)
        self.timer.start(500)

    def advance_import_progress(self) -> None:
        if self.step_idx < len(self.steps):
            val, msg = self.steps[self.step_idx]
            self.loading_progress.setValue(val)
            self.loading_status.setText(msg)
            self.step_idx += 1
        else:
            self.timer.stop()
            # Calculate simulated default MR based on username length to make it dynamic
            alias = self.username_input.text().strip()
            calc_mr = min(30, max(2, len(alias)))
            self.mr_spin.setValue(calc_mr)
            self.sp_check.setChecked(calc_mr >= 16)
            self.helminth_check.setChecked(calc_mr >= 12)
            
            # Navigate to review page
            self.pages.setCurrentIndex(2)

    def select_goal_path(self, path: str) -> None:
        self.selected_path = path
        self.btn_new.setChecked(path == "New Player")
        self.btn_mid.setChecked(path == "Progressing")
        self.btn_end.setChecked(path == "Endgame")

    def finish_onboarding(self) -> None:
        # Save reviewed profile state in local database
        mr = self.mr_spin.value()
        sp = self.sp_check.isChecked()
        helminth = self.helminth_check.isChecked()

        from src.database.database import DatabaseManager
        db = DatabaseManager()
        # Save profile
        db.cursor.execute("""
            INSERT OR REPLACE INTO players (id, mastery_rank, steel_path_unlocked, arbitrations_unlocked, helminth_unlocked)
            VALUES (1, ?, ?, ?, ?)
        """, (mr, int(sp), int(sp), int(helminth)))
        db.connection.commit()

        # Save goals focus presets to settings
        from src.core.settings_manager import SettingsManager
        settings = SettingsManager()
        settings.update(
            onboarding_completed=True,
            onboarding_path=self.selected_path,
            goal_focus=self.selected_path
        )
        settings.save()

        # Clear Query cache to reload profile immediately
        from src.core.query_cache import QueryCache
        QueryCache().clear()

        self.accept()
