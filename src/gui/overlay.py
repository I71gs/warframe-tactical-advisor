from __future__ import annotations
import sys
from typing import Any
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton,
    QStackedWidget, QFrame, QScrollArea
)
from PySide6.QtGui import QColor, QFont
from src.core.app_context import AppContext
from src.core.player_loader import PlayerLoader
from src.core.theme_manager import ThemeManager

class OverlayWindow(QWidget):
    """Frameless, stays-on-top, semi-transparent HUD overlay for in-game use."""

    def __init__(self, main_window: Any) -> None:
        super().__init__()
        self.main_window = main_window
        self.context = AppContext()
        
        # Window attributes for overlay HUD
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(360, 480)
        
        self.drag_position = QPoint()
        self.active_tab = 0
        
        self.setup_ui()
        self.apply_theme()
        self.refresh_data()

    def setup_ui(self) -> None:
        # Main container with border and rounded corners
        self.container = QFrame(self)
        self.container.setObjectName("overlayContainer")
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.setSpacing(10)
        
        # Title bar (Draggable area)
        title_bar = QHBoxLayout()
        self.title_lbl = QLabel("WARFRAME HUD ADVISOR")
        self.title_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.title_lbl.setStyleSheet("letter-spacing: 1px;")
        
        self.restore_btn = QPushButton("Restore")
        self.restore_btn.setToolTip("Back to main window")
        self.restore_btn.clicked.connect(self.restore_main_window)
        self.restore_btn.setFixedWidth(65)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.clicked.connect(self.close_overlay)
        self.close_btn.setFixedWidth(28)
        
        title_bar.addWidget(self.title_lbl)
        title_bar.addStretch()
        title_bar.addWidget(self.restore_btn)
        title_bar.addWidget(self.close_btn)
        container_layout.addLayout(title_bar)
        
        # Segmented Control / Tabs
        tabs_layout = QHBoxLayout()
        tabs_layout.setSpacing(4)
        self.tab_btn_goals = QPushButton("Goals")
        self.tab_btn_dailies = QPushButton("Dailies")
        self.tab_btn_world = QPushButton("World")
        
        self.tab_btn_goals.clicked.connect(lambda: self.switch_tab(0))
        self.tab_btn_dailies.clicked.connect(lambda: self.switch_tab(1))
        self.tab_btn_world.clicked.connect(lambda: self.switch_tab(2))
        
        tabs_layout.addWidget(self.tab_btn_goals)
        tabs_layout.addWidget(self.tab_btn_dailies)
        tabs_layout.addWidget(self.tab_btn_world)
        container_layout.addLayout(tabs_layout)
        
        # Stacked contents
        self.stacked = QStackedWidget()
        container_layout.addWidget(self.stacked)
        
        # 1. Goals Page
        self.goals_scroll = QScrollArea()
        self.goals_scroll.setWidgetResizable(True)
        self.goals_scroll.setStyleSheet("background: transparent; border: none;")
        self.goals_content = QWidget()
        self.goals_layout = QVBoxLayout(self.goals_content)
        self.goals_layout.setSpacing(6)
        self.goals_layout.setContentsMargins(0, 0, 0, 0)
        self.goals_scroll.setWidget(self.goals_content)
        self.stacked.addWidget(self.goals_scroll)
        
        # 2. Dailies Page
        self.dailies_scroll = QScrollArea()
        self.dailies_scroll.setWidgetResizable(True)
        self.dailies_scroll.setStyleSheet("background: transparent; border: none;")
        self.dailies_content = QWidget()
        self.dailies_layout = QVBoxLayout(self.dailies_content)
        self.dailies_layout.setSpacing(6)
        self.dailies_layout.setContentsMargins(0, 0, 0, 0)
        self.dailies_scroll.setWidget(self.dailies_content)
        self.stacked.addWidget(self.dailies_scroll)
        
        # 3. World State Page
        self.world_scroll = QScrollArea()
        self.world_scroll.setWidgetResizable(True)
        self.world_scroll.setStyleSheet("background: transparent; border: none;")
        self.world_content = QWidget()
        self.world_layout = QVBoxLayout(self.world_content)
        self.world_layout.setSpacing(8)
        self.world_layout.setContentsMargins(0, 0, 0, 0)
        self.world_scroll.setWidget(self.world_content)
        self.stacked.addWidget(self.world_scroll)
        
        # Set outer layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.container)
        self.setLayout(outer_layout)
        
        self.switch_tab(0)

    def apply_theme(self) -> None:
        tm = ThemeManager()
        colors = tm.get_theme_colors(tm.get_active_theme_name())
        prim = colors.get("PRIMARY", "#0c0919")
        sec = colors.get("SECONDARY", "#130f26")
        acc = colors.get("ACCENT", "#bb86fc")
        txt = colors.get("TEXT", "#eae6f8")
        card = colors.get("CARD", "#1f183a")
        
        self.container.setStyleSheet(f"""
            QFrame#overlayContainer {{
                background-color: rgba({self._hex_to_rgb(sec)}, 0.90);
                border: 2px solid {acc};
                border-radius: 12px;
            }}
            QLabel {{
                color: {txt};
                background: transparent;
            }}
            QCheckBox {{
                color: {txt};
                background: transparent;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid {acc};
                border-radius: 3px;
                background-color: {prim};
            }}
            QCheckBox::indicator:checked {{
                background-color: {acc};
            }}
            QPushButton {{
                background-color: {card};
                border: 1px solid rgba(255, 255, 255, 0.08);
                color: {txt};
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                border-color: {acc};
                background-color: rgba(255, 255, 255, 0.05);
            }}
        """)
        
        # Title color
        self.title_lbl.setStyleSheet(f"color: {acc}; font-weight: bold;")
        self.update_tab_button_styles(acc, card)

    def _hex_to_rgb(self, hex_str: str) -> str:
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 3:
            hex_str = ''.join([c*2 for c in hex_str])
        try:
            return f"{int(hex_str[0:2], 16)}, {int(hex_str[2:4], 16)}, {int(hex_str[4:6], 16)}"
        except Exception:
            return "11, 18, 32"

    def update_tab_button_styles(self, active_color: str, inactive_color: str) -> None:
        buttons = [self.tab_btn_goals, self.tab_btn_dailies, self.tab_btn_world]
        for i, btn in enumerate(buttons):
            if i == self.active_tab:
                btn.setStyleSheet(f"background-color: {active_color}; color: #000000; font-weight: bold; border: none;")
            else:
                btn.setStyleSheet(f"background-color: {inactive_color}; color: #ffffff; border: 1px solid rgba(255, 255, 255, 0.08);")

    def switch_tab(self, index: int) -> None:
        self.active_tab = index
        self.stacked.setCurrentIndex(index)
        tm = ThemeManager()
        colors = tm.get_theme_colors(tm.get_active_theme_name())
        acc = colors.get("ACCENT", "#bb86fc")
        card = colors.get("CARD", "#1f183a")
        self.update_tab_button_styles(acc, card)

    def refresh_data(self) -> None:
        # Load player context
        player = PlayerLoader().load_player()
        
        # 1. Populate Goals Tab
        self.clear_layout(self.goals_layout)
        
        # Story Quest
        from src.core.progression_engine import ProgressionEngine
        pe = ProgressionEngine()
        next_quest = pe.get_next_story_quest(player)
        if next_quest and next_quest != "Story Complete":
            quest_lbl = QLabel(f"<b>🎯 Current Quest Goal:</b><br>{next_quest}")
            quest_lbl.setWordWrap(True)
            self.goals_layout.addWidget(quest_lbl)
            
            sep = QFrame()
            sep.setFrameShape(QFrame.HLine)
            sep.setStyleSheet("color: rgba(255, 255, 255, 0.1); max-height: 1px;")
            self.goals_layout.addWidget(sep)

        # Top Recommendations
        from src.core.recommendation_engine import RecommendationEngine
        recs = RecommendationEngine().generate_recommendations(player)
        self.goals_layout.addWidget(QLabel("<b>💡 Recommendations Checklist:</b>"))
        
        for rec in recs[:5]:
            cb = QCheckBox(rec.action)
            cb.setToolTip(rec.reason)
            self.goals_layout.addWidget(cb)
        self.goals_layout.addStretch()
        
        # 2. Populate Dailies Tab
        self.clear_layout(self.dailies_layout)
        from src.core.daily_objectives_engine import DailyObjectivesEngine
        doe = DailyObjectivesEngine()
        dailies = doe.get_daily_objectives(player)
        
        self.dailies_layout.addWidget(QLabel("<b>⚡ Daily Objectives:</b>"))
        for obj in dailies.get("objectives", [])[:8]:
            cb = QCheckBox(obj.get("name", "Unknown Task"))
            cb.setChecked(obj.get("completed", False))
            self.dailies_layout.addWidget(cb)
        self.dailies_layout.addStretch()

        # 3. Populate World State Tab
        self.clear_layout(self.world_layout)
        try:
            state = self.context.world_state_service.get_world_state()
            
            # Cycles
            cetus = state.get("cetus", {})
            cetus_status = "☀️ Day" if cetus.get("isDay") else "🌙 Night"
            self.world_layout.addWidget(QLabel(f"🌎 <b>Cetus:</b> {cetus_status} ({cetus.get('timeLeft', 'N/A')} left)"))
            
            vallis = state.get("vallis", {})
            vallis_status = "🔥 Warm" if vallis.get("isWarm") else "❄️ Cold"
            self.world_layout.addWidget(QLabel(f"❄️ <b>Vallis:</b> {vallis_status} ({vallis.get('timeLeft', 'N/A')} left)"))
            
            zariman = state.get("zariman", {})
            self.world_layout.addWidget(QLabel(f"🌀 <b>Zariman State:</b> {zariman.get('state', 'Unknown').capitalize()}"))
            
            # Alerts
            alerts = state.get("alerts", [])
            if alerts:
                self.world_layout.addWidget(QLabel("<b>🚨 Live Alerts:</b>"))
                for a in alerts[:3]:
                    rew = a.get("reward", "Reward")
                    node = a.get("mission", {}).get("node", "Node")
                    self.world_layout.addWidget(QLabel(f"• {node}: {rew}"))
            
            # Fissures
            fissures = state.get("fissures", [])
            if fissures:
                self.world_layout.addWidget(QLabel("<b>🔥 Active Fissures:</b>"))
                for f in fissures[:3]:
                    self.world_layout.addWidget(QLabel(f"• {f.get('tier')} {f.get('missionType')} ({f.get('node')})"))
        except Exception as e:
            self.world_layout.addWidget(QLabel(f"World State unavailable: {e}"))
        self.world_layout.addStretch()

    def clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # Dragging implementation
    def mousePressEvent(self, event: Any) -> None:
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: Any) -> None:
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def keyPressEvent(self, event: Any) -> None:
        # Close on Escape or Ctrl+O
        if event.key() == Qt.Key_Escape:
            self.close_overlay()
        elif event.key() == Qt.Key_O and event.modifiers() == Qt.ControlModifier:
            self.close_overlay()
        else:
            super().keyPressEvent(event)

    def restore_main_window(self) -> None:
        self.hide()
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()

    def close_overlay(self) -> None:
        self.hide()
        # Ensure main window is restored if closed via overlay
        if self.main_window:
            self.main_window.show()
