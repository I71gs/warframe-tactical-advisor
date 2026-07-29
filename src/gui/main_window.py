from typing import Any
import sys
from pathlib import Path
from PySide6.QtCore import QTimer, Qt, Property, QEasingCurve, QPropertyAnimation, QParallelAnimationGroup, QSequentialAnimationGroup
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QStatusBar, QMenu, QMessageBox,
    QHBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QGraphicsOpacityEffect, QFrame
)
from PySide6.QtGui import QAction, QIcon, QKeySequence, QShortcut, QFont, QColor
from src.core.settings_manager import SettingsManager
from src.utils.logger import logger
from src.gui.widgets.custom_charts import AnimatedButton

class PageTransitionContainer(QWidget):
    """Wrapper that smoothly fades and slides up new pages upon initial rendering."""

    def __init__(self, child_widget: QWidget, parent: Any = None) -> None:
        super().__init__(parent)
        self.child = child_widget
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0, 8, 0, 0)
        self.lay.addWidget(child_widget)
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        
        self._top_margin = 8.0
        
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(160)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        
        self.margin_anim = QPropertyAnimation(self, b"topMargin")
        self.margin_anim.setDuration(160)
        self.margin_anim.setEasingCurve(QEasingCurve.OutQuad)
        self.margin_anim.setStartValue(8.0)
        self.margin_anim.setEndValue(0.0)
        
        self.group = QParallelAnimationGroup()
        self.group.addAnimation(self.opacity_anim)
        self.group.addAnimation(self.margin_anim)

    def get_top_margin(self) -> float:
        return self._top_margin

    def set_top_margin(self, val: float) -> None:
        self._top_margin = val
        self.lay.setContentsMargins(0, int(val), 0, 0)

    topMargin = Property(float, get_top_margin, set_top_margin)

    def trigger_transition(self) -> None:
        if "pytest" in sys.modules:
            self.opacity_effect.setOpacity(1.0)
            self.set_top_margin(0.0)
        else:
            self.group.start()


class NavPill(QWidget):
    """Visual selection pill overlay styled to slide between tree navigation items."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(202, 163, 255, 0.12); border-left: 3px solid #caa3ff; border-radius: 4px;")
        self.hide()

from src.gui.profile_tab import ProfileTab
from src.gui.recommendations_tab import RecommendationsTab
from src.gui.progression_tab import ProgressionTab
from src.gui.build_advisor_tab import BuildAdvisorTab
from src.gui.quest_planner_tab import QuestPlannerTab
from src.gui.readiness_tab import ReadinessTab
from src.gui.dashboard_tab import DashboardTab
from src.gui.loadout_tab import LoadoutTab
from src.gui.knowledge_tab import KnowledgeTab
from src.gui.statistics_tab import StatisticsTab
from src.gui.settings_tab import SettingsTab
from src.gui.style import SHEET
from src.gui.goal_planner_tab import (
    GoalPlannerTab
)
from src.gui.gap_analysis_tab import GapAnalysisTab
from src.gui.build_simulator_tab import BuildSimulatorTab
from src.gui.weapon_tiers_tab import WeaponTiersTab
from src.gui.daily_tab import DailyTab
from src.gui.weekly_tab import WeeklyTab
from src.gui.search_tab import SearchTab
from src.gui.timeline_tab import TimelineTab
from src.gui.charts_tab import ChartsTab
from src.gui.milestone_tab import MilestoneTab
from src.gui.dependency_graph_tab import DependencyGraphTab
from src.gui.graph_tab import GraphTab
from src.gui.resource_tab import ResourceTab
from src.gui.farming_routes_tab import FarmingRoutesTab
from src.gui.team_tab import TeamTab
from src.gui.achievements_tab import AchievementsTab
from src.gui.encyclopedia_tab import EncyclopediaTab
from src.gui.collection_tab import CollectionTab
from src.gui.mastery_tab import MasteryTab
from src.gui.relic_tab import RelicTab
from src.gui.incarnon_tab import IncarnonTab
from src.gui.circuit_tab import CircuitTab
from src.gui.duviri_tab import DuviriTab
from src.gui.companion_tab import CompanionTab
from src.gui.economy_tab import EconomyTab
from src.gui.session_tab import SessionTab
from src.gui.codex_tab import CodexTab
from src.gui.benchmark_tab import BenchmarkTab
from src.gui.replay_tab import ReplayTab
from src.gui.window_manager import WindowManager
from src.gui.comparison_tab import ComparisonTab
from src.gui.route_tab import RouteTab
from src.gui.build_library_tab import BuildLibraryTab
from src.gui.theme_editor_tab import ThemeEditorTab
from src.gui.patch_tab import PatchTab
from src.gui.overlay import OverlayWindow


class MainWindow(QMainWindow):
    """Class MainWindow documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.setWindowTitle('Warframe Tactical Advisor')
        self.setMinimumSize(900, 600)
        
        # Initialize AppContext and subscribe to UI events
        from src.core.app_context import AppContext
        self.context = AppContext()
        self.context.event_bus.subscribe("STATUS_MESSAGE", lambda data: self.show_status(data.get("message", "")))
        self.context.event_bus.subscribe("NOTIFICATION", self.show_toast_notification)
        self.context.event_bus.subscribe("PLUGINS_LOADED", lambda data: self.load_registered_tabs())

        
        # Invalidate cache when profile updates or switch accounts occur
        from src.core.query_cache import QueryCache
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: QueryCache().clear())
        self.context.event_bus.subscribe("ACCOUNT_SWITCHED", lambda data: QueryCache().clear())


        self.window_manager = WindowManager(self)

        self.settings = SettingsManager()
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_everything)
        try:
            root = Path(__file__).resolve().parents[2]
            icon_path = root / 'assets' / 'icon.ico'
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception as exc:
            logger.warning('Failed to set application icon: %s', exc)

        # Initialize tab cache and defer data loading until tab selection/visit
        self._loaded_tabs_this_session = set()
        
        tab_classes = [
            ProfileTab, RecommendationsTab, ProgressionTab, BuildAdvisorTab,
            QuestPlannerTab, ReadinessTab, LoadoutTab, KnowledgeTab, StatisticsTab,
            DashboardTab, SettingsTab, GoalPlannerTab, GapAnalysisTab, BuildSimulatorTab,
            WeaponTiersTab, DailyTab, WeeklyTab, SearchTab, TimelineTab, ChartsTab,
            MilestoneTab, DependencyGraphTab, GraphTab, ResourceTab, FarmingRoutesTab,
            TeamTab, AchievementsTab, EncyclopediaTab, CollectionTab, MasteryTab,
            RelicTab, IncarnonTab, CircuitTab, DuviriTab, CompanionTab, EconomyTab,
            SessionTab, CodexTab, BenchmarkTab, ReplayTab, ComparisonTab, RouteTab,
            BuildLibraryTab, ThemeEditorTab, PatchTab
        ]
        
        def wrap_tab_class_methods(cls):
            methods_to_wrap = [
                "load_profile", "load_recommendations", "load_progress",
                "load_readiness", "load_quests", "load_plan", "load_gaps", "run_simulation",
                "load_tiers", "load_data", "refresh_list", "load_stats", "load_daily",
                "load_weekly", "load_timeline", "render_selected_chart", "load_milestones",
                "load_graph", "load_planner", "load_routes", "load_teams", "load_achievements",
                "load_encyclopedia", "load_codex", "load_collections", "load_mastery",
                "load_relics", "load_incarnon", "load_circuit", "load_duviri",
                "load_companions", "load_economy", "load_session", "load_benchmarks",
                "populate_dropdowns", "refresh", "load", "load_patch_notes"
            ]
            for method_name in methods_to_wrap:
                if hasattr(cls, method_name):
                    original = getattr(cls, method_name)
                    if callable(original) and not hasattr(original, "_is_wrapped"):
                        def make_wrapper(orig_method, name):
                            def wrapper(self, *args, **kwargs):
                                if getattr(sys, "_defer_tab_loading", False) and "pytest" not in sys.modules:
                                    logger.info("Deferred load method %s for %s", name, self.__class__.__name__)
                                    return None
                                return orig_method(self, *args, **kwargs)
                            wrapper._is_wrapped = True
                            return wrapper
                        setattr(cls, method_name, make_wrapper(original, method_name))

        for cls in tab_classes:
            wrap_tab_class_methods(cls)

        sys._defer_tab_loading = True
        self.tabs = QTabWidget()
        self.profile_tab = ProfileTab()
        self.recommendations_tab = RecommendationsTab()
        self.progression_tab = ProgressionTab()
        self.build_tab = BuildAdvisorTab()
        self.quest_planner_tab = QuestPlannerTab()
        self.readiness_tab = ReadinessTab()
        self.loadout_tab = LoadoutTab()
        self.knowledge_tab = KnowledgeTab()
        self.statistics_tab = StatisticsTab()
        self.dashboard_tab = DashboardTab()
        self.settings_tab = SettingsTab(self)
        
        self._animated_tabs_this_session = set()
        
        self.add_animated_tab(self.dashboard_tab, 'Dashboard')
        self.add_animated_tab(self.profile_tab, 'Profile')
        self.add_animated_tab(self.recommendations_tab, 'Recommendations')
        self.add_animated_tab(self.progression_tab, 'Progression')
        self.add_animated_tab(self.readiness_tab, 'Readiness')
        self.add_animated_tab(self.quest_planner_tab, 'Quest Planner')
        self.add_animated_tab(self.build_tab, 'Build Advisor')
        self.add_animated_tab(self.loadout_tab, 'Loadout Advisor')
        self.add_animated_tab(self.knowledge_tab, 'Knowledge Base')
        self.add_animated_tab(self.statistics_tab, 'Statistics')
        self.add_animated_tab(self.settings_tab, 'Settings')
        self.apply_settings()

        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.setup_menu_bar()
        self.goal_planner_tab = (
            GoalPlannerTab()
        )
        self.add_animated_tab(self.goal_planner_tab, 'Goal Planner')
        
        # New Stage 2 Coach Tabs
        self.gap_tab = GapAnalysisTab()
        self.build_simulator_tab = BuildSimulatorTab()
        self.weapon_tiers_tab = WeaponTiersTab()
        self.add_animated_tab(self.gap_tab, 'Gap Analyzer')
        self.add_animated_tab(self.build_simulator_tab, 'Build Simulator')
        self.add_animated_tab(self.weapon_tiers_tab, 'Weapon Tiers')

        # Phase 3 & 4 Tabs
        self.daily_tab = DailyTab()
        self.weekly_tab = WeeklyTab()
        self.timeline_tab = TimelineTab()
        self.charts_tab = ChartsTab()
        self.search_tab = SearchTab()
        self.add_animated_tab(self.daily_tab, 'Daily Objectives')
        self.add_animated_tab(self.weekly_tab, 'Weekly Planner')
        self.add_animated_tab(self.timeline_tab, '30-Day Timeline')
        self.add_animated_tab(self.charts_tab, 'Progression Charts')
        self.add_animated_tab(self.search_tab, 'Global Search')

        # Stage 3 & 4 new tabs
        self.milestone_tab = MilestoneTab()
        self.dependency_graph_tab = DependencyGraphTab()
        self.graph_tab = GraphTab()
        self.resource_tab = ResourceTab()
        self.farming_routes_tab = FarmingRoutesTab()
        self.team_tab = TeamTab()
        self.achievements_tab = AchievementsTab()
        
        self.add_animated_tab(self.milestone_tab, 'Roadmap Milestones')
        self.add_animated_tab(self.dependency_graph_tab, 'Dependency Graph')
        self.add_animated_tab(self.graph_tab, 'Interactive Graph')
        self.add_animated_tab(self.resource_tab, 'Resource Planner')
        self.add_animated_tab(self.farming_routes_tab, 'Farming Routes')
        self.add_animated_tab(self.team_tab, 'Team Synergy')
        self.add_animated_tab(self.achievements_tab, 'Badges & Achievements')

        # Stage 6 - 20 Tabs (v3.0 Progression)
        self.encyclopedia_tab = EncyclopediaTab()
        self.collection_tab = CollectionTab()
        self.mastery_tab = MasteryTab()
        self.relic_tab = RelicTab()
        self.incarnon_tab = IncarnonTab()
        self.circuit_tab = CircuitTab()
        self.duviri_tab = DuviriTab()
        self.companion_tab = CompanionTab()
        self.economy_tab = EconomyTab()
        self.session_tab = SessionTab()
        self.codex_tab = CodexTab()
        self.benchmark_tab = BenchmarkTab()
        self.replay_tab = ReplayTab(self)

        self.add_animated_tab(self.encyclopedia_tab, 'Encyclopedia')
        self.add_animated_tab(self.codex_tab, 'Codex')
        self.add_animated_tab(self.collection_tab, 'Collection Tracker')
        self.add_animated_tab(self.mastery_tab, 'Mastery Rank Planner')
        self.add_animated_tab(self.relic_tab, 'Relic Planner')
        self.add_animated_tab(self.incarnon_tab, 'Incarnon Evolutions')
        self.add_animated_tab(self.circuit_tab, 'Circuit Forecast')
        self.add_animated_tab(self.duviri_tab, 'Duviri Upgrades')
        self.add_animated_tab(self.companion_tab, 'Companion Synergy')
        self.add_animated_tab(self.economy_tab, 'Economy Deficits')
        self.add_animated_tab(self.session_tab, 'Session Planner')
        self.add_animated_tab(self.benchmark_tab, 'Benchmark Engine')
        self.add_animated_tab(self.replay_tab, 'Progression Replay')
        self.comparison_tab = ComparisonTab()
        self.add_animated_tab(self.comparison_tab, 'Account Comparison')
        self.route_tab = RouteTab()
        self.add_animated_tab(self.route_tab, 'Tactical Routes')
        self.build_library_tab = BuildLibraryTab()
        self.add_animated_tab(self.build_library_tab, 'Build Library')
        self.theme_editor_tab = ThemeEditorTab(self)
        self.add_animated_tab(self.theme_editor_tab, 'Theme Studio')
        self.patch_tab = PatchTab()
        self.add_animated_tab(self.patch_tab, 'Patch Notes')
        self.load_registered_tabs()
        sys._defer_tab_loading = False

        # Setup hierarchical sidebar layout using QTreeWidget for enterprise-grade category nesting
        self.sidebar = QTreeWidget()
        self.sidebar.setObjectName("sidebarNav")
        self.sidebar.setFixedWidth(240)
        self.sidebar.setHeaderHidden(True)
        self.sidebar.setIndentation(12)
        self.sidebar.setAnimated(True)
        
        self.sidebar_pill = NavPill(self.sidebar.viewport())
        self.sidebar_pill_opacity = QGraphicsOpacityEffect(self.sidebar_pill)
        self.sidebar_pill.setGraphicsEffect(self.sidebar_pill_opacity)
        self.sidebar_pill_opacity.setOpacity(0.0)

        # Bottom navigation list for Settings and About
        self.bottom_sidebar = QTreeWidget()
        self.bottom_sidebar.setObjectName("bottomSidebarNav")
        self.bottom_sidebar.setFixedWidth(240)
        self.bottom_sidebar.setHeaderHidden(True)
        self.bottom_sidebar.setIndentation(12)
        self.bottom_sidebar.setAnimated(True)
        self.bottom_sidebar.setFixedHeight(72) # Fits Settings and About perfectly
        
        self.bottom_pill = NavPill(self.bottom_sidebar.viewport())
        self.bottom_pill_opacity = QGraphicsOpacityEffect(self.bottom_pill)
        self.bottom_pill.setGraphicsEffect(self.bottom_pill_opacity)
        self.bottom_pill_opacity.setOpacity(0.0)

        # Retrieve active theme ACCENT color for category labels
        from src.core.theme_manager import ThemeManager
        theme_colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
        acc = theme_colors.get("ACCENT", "#00a3cc")
        
        from src.core.design_system import get_icon, FONT_H3, FONT_BODY

        # Search bar button at the top
        self.search_btn = AnimatedButton("  Search Command Palette     [Ctrl+K]")
        self.search_btn.setIcon(get_icon("search", size=16, color=theme_colors.get("MUTED", "#8e85a6")))
        self.search_btn.setObjectName("sidebarSearchBtn")
        self.search_btn.setFixedWidth(220)
        self.search_btn.clicked.connect(self.open_command_palette)

        # Navigation structure mapping tab titles to categories with Tabler SVG icons
        categories = {
            "Your Journey": ("compass", [
                'Dashboard', 'Profile', 'Recommendations', 'Progression', 'Readiness',
                'Quest Planner', 'Progression Charts', 'Roadmap Milestones', 'Session Planner',
                'Progression Replay', 'Statistics'
            ]),
            "Arsenal": ("sword", [
                'Build Advisor', 'Loadout Advisor', 'Build Simulator', 'Build Library',
                'Weapon Tiers', 'Mastery Rank Planner', 'Incarnon Evolutions', 'Companion Synergy'
            ]),
            "Grind": ("pick", [
                'Daily Objectives', 'Weekly Planner', '30-Day Timeline', 'Farming Routes',
                'Relic Planner', 'Collection Tracker', 'Resource Planner', 'Economy Deficits',
                'Circuit Forecast', 'Duviri Upgrades', 'Tactical Routes', 'Team Synergy',
                'Badges & Achievements'
            ]),
            "Reference": ("book", [
                'Encyclopedia', 'Codex', 'Knowledge Base', 'Global Search',
                'Interactive Graph', 'Dependency Graph', 'Account Comparison', 'Benchmark Engine',
                'Theme Studio', 'Patch Notes'
            ])
        }

        # Track categorized tabs and category items for dynamic repainting
        categorized_tabs = set()
        self.item_to_tab_index = {}
        self.tab_index_to_item = {}
        self.category_items = []

        # Populate defined categories
        for cat_name, (icon_name, tab_list) in categories.items():
            cat_item = QTreeWidgetItem(self.sidebar)
            cat_item.setText(0, cat_name)
            cat_item.setIcon(0, get_icon(icon_name, size=20, color=acc))
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsSelectable) # Make category non-selectable
            cat_item.setFont(0, QFont("Inter", 10, QFont.Bold))
            cat_item.setForeground(0, QColor(acc))
            self.category_items.append(cat_item)
            
            has_children = False
            for tab_text in tab_list:
                idx = -1
                for i in range(self.tabs.count()):
                    if self.tabs.tabText(i) == tab_text:
                        idx = i
                        break
                if idx != -1:
                    child_item = QTreeWidgetItem(cat_item)
                    child_item.setText(0, tab_text)
                    child_item.setFont(0, QFont("Inter", 9))
                    child_item.setData(0, Qt.UserRole, idx)
                    self.item_to_tab_index[child_item] = idx
                    self.tab_index_to_item[idx] = child_item
                    categorized_tabs.add(idx)
                    has_children = True

            # Expand categories by default
            if has_children:
                self.sidebar.expandItem(cat_item)

        # Catch-all category for any remaining or plugin-loaded tabs
        cat_uncategorized = None
        for idx in range(self.tabs.count()):
            # Settings will be placed in the bottom tree specifically, don't put in Extensions
            if self.tabs.tabText(idx) == "Settings":
                continue
            if idx not in categorized_tabs:
                if cat_uncategorized is None:
                    cat_uncategorized = QTreeWidgetItem(self.sidebar)
                    cat_uncategorized.setText(0, "Extensions")
                    cat_uncategorized.setIcon(0, get_icon("plug", size=20, color=acc))
                    cat_uncategorized.setFlags(cat_uncategorized.flags() & ~Qt.ItemIsSelectable)
                    cat_uncategorized.setFont(0, QFont("Inter", 10, QFont.Bold))
                    cat_uncategorized.setForeground(0, QColor(acc))
                    self.sidebar.expandItem(cat_uncategorized)
                    self.category_items.append(cat_uncategorized)
                
                tab_text = self.tabs.tabText(idx)
                child_item = QTreeWidgetItem(cat_uncategorized)
                child_item.setText(0, tab_text)
                child_item.setFont(0, QFont("Inter", 9))
                child_item.setData(0, Qt.UserRole, idx)
                self.item_to_tab_index[child_item] = idx
                self.tab_index_to_item[idx] = child_item
                categorized_tabs.add(idx)

        # Populate bottom sidebar with Settings and About
        settings_idx = -1
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "Settings":
                settings_idx = i
                break
        
        if settings_idx != -1:
            settings_item = QTreeWidgetItem(self.bottom_sidebar)
            settings_item.setText(0, "Settings")
            settings_item.setIcon(0, get_icon("settings", size=20, color=acc))
            settings_item.setFont(0, QFont("Inter", 10, QFont.Bold))
            settings_item.setData(0, Qt.UserRole, settings_idx)
            self.item_to_tab_index[settings_item] = settings_idx
            self.tab_index_to_item[settings_idx] = settings_item
            categorized_tabs.add(settings_idx)
            
        about_item = QTreeWidgetItem(self.bottom_sidebar)
        about_item.setText(0, "About Advisor")
        about_item.setFont(0, QFont("Inter", 10, QFont.Bold))
        about_item.setIcon(0, get_icon("info", size=20, color=acc))

        def on_sidebar_selection_changed():
            selected = self.sidebar.selectedItems()
            if selected:
                self.bottom_sidebar.blockSignals(True)
                self.bottom_sidebar.clearSelection()
                self.bottom_sidebar.blockSignals(False)
                item = selected[0]
                self._animate_pill_to_item(self.sidebar, self.sidebar_pill, self.sidebar_pill_opacity, item)
                self._animate_pill_to_item(self.bottom_sidebar, self.bottom_pill, self.bottom_pill_opacity, None)
                idx = item.data(0, Qt.UserRole)
                if idx is not None:
                    self.tabs.setCurrentIndex(idx)
            else:
                self._animate_pill_to_item(self.sidebar, self.sidebar_pill, self.sidebar_pill_opacity, None)

        def on_bottom_sidebar_selection_changed():
            selected = self.bottom_sidebar.selectedItems()
            if selected:
                self.sidebar.blockSignals(True)
                self.sidebar.clearSelection()
                self.sidebar.blockSignals(False)
                item = selected[0]
                self._animate_pill_to_item(self.bottom_sidebar, self.bottom_pill, self.bottom_pill_opacity, item)
                self._animate_pill_to_item(self.sidebar, self.sidebar_pill, self.sidebar_pill_opacity, None)
                idx = item.data(0, Qt.UserRole)
                if idx is not None:
                    self.tabs.setCurrentIndex(idx)
                elif item.text(0) == "About Advisor":
                    self.show_about_dialog()
                    self.bottom_sidebar.clearSelection()
                    self._sync_tabs_to_sidebar(self.tabs.currentIndex())
            else:
                self._animate_pill_to_item(self.bottom_sidebar, self.bottom_pill, self.bottom_pill_opacity, None)

        self.sidebar.itemSelectionChanged.connect(on_sidebar_selection_changed)
        self.bottom_sidebar.itemSelectionChanged.connect(on_bottom_sidebar_selection_changed)
        self.sidebar.verticalScrollBar().valueChanged.connect(self._sync_pill_instantly)
        self.tabs.currentChanged.connect(self._sync_tabs_to_sidebar)
        self.tabs.tabBar().hide()
        
        # Sidebar layout panel grouping top search, sidebar lists, separator and settings
        nav_panel = QWidget()
        nav_panel.setObjectName("sidebarNavPanel")
        nav_panel.setFixedWidth(240)
        nav_panel_layout = QVBoxLayout(nav_panel)
        nav_panel_layout.setContentsMargins(0, 0, 0, 0)
        nav_panel_layout.setSpacing(0)
        
        nav_panel_layout.addWidget(self.search_btn, 0, Qt.AlignCenter)
        nav_panel_layout.addWidget(self.sidebar, 1)
        
        separator = QFrame()
        separator.setObjectName("sidebarSeparator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        nav_panel_layout.addWidget(separator)
        
        nav_panel_layout.addWidget(self.bottom_sidebar, 0)
        
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(nav_panel)
        layout.addWidget(self.tabs)
        self.setCentralWidget(container)

    def _sync_tabs_to_sidebar(self, index: int) -> None:
        if index in self.tab_index_to_item:
            item = self.tab_index_to_item[index]
            if hasattr(self, "sidebar"):
                self.sidebar.blockSignals(True)
                self.sidebar.clearSelection()
                if item.treeWidget() == self.sidebar:
                    self.sidebar.setCurrentItem(item)
                    self._animate_pill_to_item(self.sidebar, self.sidebar_pill, self.sidebar_pill_opacity, item)
                    self._animate_pill_to_item(self.bottom_sidebar, self.bottom_pill, self.bottom_pill_opacity, None)
                self.sidebar.blockSignals(False)
            if hasattr(self, "bottom_sidebar"):
                self.bottom_sidebar.blockSignals(True)
                self.bottom_sidebar.clearSelection()
                if item.treeWidget() == self.bottom_sidebar:
                    self.bottom_sidebar.setCurrentItem(item)
                    self._animate_pill_to_item(self.bottom_sidebar, self.bottom_pill, self.bottom_pill_opacity, item)
                    self._animate_pill_to_item(self.sidebar, self.sidebar_pill, self.sidebar_pill_opacity, None)
                self.bottom_sidebar.blockSignals(False)

    def showEvent(self, event: Any) -> None:
        super().showEvent(event)
        if not hasattr(self, "_onboarding_checked"):
            self._onboarding_checked = True
            from PySide6.QtCore import QTimer
            QTimer.singleShot(100, self.check_onboarding)

    def check_onboarding(self) -> None:
        if not self.settings.get('onboarding_completed', False):
            from src.gui.widgets.onboarding_wizard import OnboardingWizard
            from PySide6.QtWidgets import QDialog
            wizard = OnboardingWizard(self)
            if wizard.exec() == QDialog.Accepted:
                self.refresh_everything()
                self.tabs.setCurrentIndex(0)
                self._sync_tabs_to_sidebar(0)
                self.dashboard_tab.show_onboarding_tooltips()





    def refresh_everything(self) -> None:
        """Refresh only the active tab and clear the loaded cache for the others."""
        import time
        start_time = time.perf_counter()
        
        # Clear the cache of loaded tabs so they reload when next visited
        self._loaded_tabs_this_session.clear()
        
        # Find the active tab index and trigger its load
        active_idx = self.tabs.currentIndex()
        self._loaded_tabs_this_session.add(active_idx)
        
        container = self.tabs.widget(active_idx)
        tab_widget = container
        if isinstance(container, PageTransitionContainer):
            tab_widget = container.child
            
        self.lazy_load_tab_widget(tab_widget)
        
        # Also always refresh the theme editor combo box helper if active
        try:
            if hasattr(self, "theme_editor_tab"):
                self.theme_editor_tab.preset_combo.clear()
                self.theme_editor_tab.preset_combo.addItems(self.theme_editor_tab.tm.get_themes())
        except Exception:
            pass

        # Record latency in profiler
        try:
            from src.core.profiler import Profiler
            refresh_duration_ms = (time.perf_counter() - start_time) * 1000
            Profiler.record_refresh_duration(refresh_duration_ms)
        except Exception:
            pass

    def show_status(self, message: str, timeout: int = 5000) -> None:
        """Display a message in the status bar."""
        try:
            sb = self.statusBar()
            if not sb:
                sb = QStatusBar()
                self.setStatusBar(sb)
            sb.showMessage(message, timeout)
        except Exception as exc:
            logger.warning('Unable to show status bar message: %s', exc)
            print(message)
    def add_animated_tab(self, tab_instance: QWidget, title: str) -> int:
        container = PageTransitionContainer(tab_instance, self)
        return self.tabs.addTab(container, title)

    def _sync_pill_instantly(self) -> None:
        selected = self.sidebar.selectedItems()
        if selected and hasattr(self, "sidebar_pill"):
            item = selected[0]
            rect = self.sidebar.visualItemRect(item)
            if not rect.isEmpty():
                rect.setX(4)
                rect.setWidth(self.sidebar.viewport().width() - 8)
                self.sidebar_pill.setGeometry(rect)

    def _animate_pill_to_item(self, sidebar: QTreeWidget, pill: QWidget, opacity_effect: QGraphicsOpacityEffect, item: QTreeWidgetItem) -> None:
        import sys
        if not item or item.text(0) in ("Your Journey", "Arsenal", "Grind", "Reference", "Extensions"):
            if "pytest" in sys.modules:
                opacity_effect.setOpacity(0.0)
                pill.hide()
            else:
                anim = QPropertyAnimation(opacity_effect, b"opacity")
                anim.setDuration(120)
                anim.setStartValue(opacity_effect.opacity())
                anim.setEndValue(0.0)
                anim.start()
            return
            
        rect = sidebar.visualItemRect(item)
        if rect.isEmpty():
            return
            
        rect.setX(4)
        rect.setWidth(sidebar.viewport().width() - 8)
        
        if "pytest" in sys.modules:
            pill.setGeometry(rect)
            opacity_effect.setOpacity(1.0)
            pill.show()
            return
            
        if opacity_effect.opacity() == 0.0 or not pill.isVisible():
            pill.setGeometry(rect)
            pill.show()
            anim = QPropertyAnimation(opacity_effect, b"opacity")
            anim.setDuration(120)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.start()
        else:
            geom_anim = QPropertyAnimation(pill, b"geometry")
            geom_anim.setDuration(150)
            geom_anim.setEasingCurve(QEasingCurve.OutQuad)
            geom_anim.setStartValue(pill.geometry())
            geom_anim.setEndValue(rect)
            
            op_anim = QPropertyAnimation(opacity_effect, b"opacity")
            op_anim.setDuration(150)
            op_anim.setStartValue(opacity_effect.opacity())
            op_anim.setEndValue(1.0)
            
            if sidebar == self.sidebar:
                self._sidebar_anim_group = QParallelAnimationGroup()
                self._sidebar_anim_group.addAnimation(geom_anim)
                self._sidebar_anim_group.addAnimation(op_anim)
                self._sidebar_anim_group.start()
            else:
                self._bottom_anim_group = QParallelAnimationGroup()
                self._bottom_anim_group.addAnimation(geom_anim)
                self._bottom_anim_group.addAnimation(op_anim)
                self._bottom_anim_group.start()

    def apply_settings(self) -> None:
        """Apply persisted user settings to the window and auto-refresh timer."""
        try:
            from src.core.theme_manager import ThemeManager
            from src.core.theme_engine import ThemeEngine
            tm = ThemeManager()
            te = ThemeEngine()
            active_theme = tm.get_active_theme_name()
            colors = tm.get_theme_colors(active_theme)
            stylesheet = te.compile_stylesheet(colors, active_theme)
            self.setStyleSheet(stylesheet)
            
            # Dynamic category item color updates based on active theme
            if hasattr(self, "sidebar") and hasattr(self, "category_items"):
                acc = colors.get("ACCENT", "#00a3cc")
                for item in self.category_items:
                    item.setForeground(0, QColor(acc))
        except Exception as exc:
            logger.warning('Failed to apply dynamic stylesheet, falling back: %s', exc)
            if self.settings.get('dark_mode', True):
                try:
                    self.setStyleSheet(SHEET)
                except Exception:
                    pass
            else:
                self.setStyleSheet('')
        if self.settings.get('remember_size', True):
            size = self.settings.get('window_size', {})
            width = size.get('width', 1000)
            height = size.get('height', 700)
            self.resize(width, height)
            if 'x' in size and 'y' in size:
                self.move(size['x'], size['y'])
        else:
            self.resize(1000, 700)
        if self.settings.get('remember_tab', True):
            self.tabs.setCurrentIndex(self.settings.get('last_tab_index', 0))
        if self.settings.get('auto_refresh', True):
            self.refresh_timer.start(180000)
        else:
            self.refresh_timer.stop()

    def lazy_load_tab_widget(self, tab_widget: QWidget) -> None:
        methods = [
            "load_dashboard", "load_profile", "load_recommendations", "load_progress",
            "load_readiness", "load_quests", "load_plan", "load_gaps", "run_simulation",
            "load_tiers", "load_data", "refresh_list", "load_stats", "load_daily",
            "load_weekly", "load_timeline", "render_selected_chart", "load_milestones",
            "load_graph", "load_planner", "load_routes", "load_teams", "load_achievements",
            "load_encyclopedia", "load_codex", "load_collections", "load_mastery",
            "load_relics", "load_incarnon", "load_circuit", "load_duviri",
            "load_companions", "load_economy", "load_session", "load_benchmarks",
            "populate_dropdowns", "load_patch_notes"
        ]
        for method_name in methods:
            if hasattr(tab_widget, method_name):
                method = getattr(tab_widget, method_name)
                if callable(method):
                    try:
                        logger.info("Lazy loading tab widget %s using method %s", tab_widget.__class__.__name__, method_name)
                        method()
                        return
                    except Exception as e:
                        logger.exception("Failed to lazy load tab widget %s with method %s: %s", tab_widget.__class__.__name__, method_name, e)
                        
        for fallback in ["refresh", "load", "refresh_data"]:
            if hasattr(tab_widget, fallback):
                method = getattr(tab_widget, fallback)
                if callable(method):
                    try:
                        method()
                        return
                    except Exception:
                        pass

    def on_tab_changed(self, index: int) -> None:
        """Persist the selected tab index in settings and track analytics."""
        if self.settings.get('remember_tab', True):
            self.settings.update(last_tab_index=index)
        try:
            tab_name = self.tabs.tabText(index)
            self.context.analytics_service.track_tab_view(tab_name)
        except Exception:
            pass
            
        try:
            container = self.tabs.widget(index)
            tab_widget = container
            if isinstance(container, PageTransitionContainer):
                if index not in self._animated_tabs_this_session:
                    self._animated_tabs_this_session.add(index)
                    container.trigger_transition()
                else:
                    container.opacity_effect.setOpacity(1.0)
                    container.set_top_margin(0.0)
                tab_widget = container.child
                
            if index not in self._loaded_tabs_this_session:
                self._loaded_tabs_this_session.add(index)
                self.lazy_load_tab_widget(tab_widget)
        except Exception as e:
            logger.error("Failed to load/transition tab: %s", e)

    def backup_data(self) -> None:
        """Create an on-demand backup of the player database."""
        try:
            from src.core.profile_manager import ProfileManager
            backup_path = ProfileManager().backup_profile()
            self.show_status(f'Backup created: {backup_path.name}')
        except Exception as exc:
            self.show_status('Backup failed')
            logger.exception('Backup failed: %s', exc)

    def closeEvent(self, event: Any) -> None:
        """Save window settings before closing."""
        if self.settings.get('remember_size', True):
            pos = self.pos()
            self.settings.update(window_size={
                'width': self.width(),
                'height': self.height(),
                'x': pos.x(),
                'y': pos.y()
            })
        self.settings.save()
        try:
            from src.core.player_loader import PlayerLoader
            from src.core.snapshot_repository import SnapshotRepository
            player = PlayerLoader().load_player()
            SnapshotRepository().save_snapshot(player)
        except Exception as exc:
            logger.error("Failed to auto-save daily snapshot on close: %s", exc)
        super().closeEvent(event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        from src.database.database import DatabaseManager
        db = DatabaseManager()
        if db.get_player() is None:
            from src.gui.widgets.setup_wizard import SetupWizard
            import sys
            if 'pytest' not in sys.modules:
                wizard = SetupWizard(self)
                wizard.exec()
                self.refresh_everything()

    def setup_shortcuts(self) -> None:

        """Bind global keyboard shortcuts."""
        QShortcut(QKeySequence('Ctrl+S'), self, activated=self.profile_tab.save_profile)
        QShortcut(QKeySequence('Ctrl+R'), self, activated=self.refresh_everything)
        QShortcut(QKeySequence('Ctrl+E'), self, activated=self.profile_tab.export_profile)
        QShortcut(QKeySequence('Ctrl+I'), self, activated=self.profile_tab.import_profile)
        QShortcut(QKeySequence('Ctrl+F'), self, activated=lambda: self.profile_tab.quest_input.setFocus())
        QShortcut(QKeySequence('Ctrl+K'), self, activated=self.open_command_palette)
        QShortcut(QKeySequence('Ctrl+P'), self, activated=self.open_command_palette)
        QShortcut(QKeySequence('Ctrl+O'), self, activated=self.toggle_overlay_mode)

    def toggle_overlay_mode(self) -> None:
        """Hide the main window and show the frameless overlay HUD."""
        if not hasattr(self, "overlay_win") or self.overlay_win is None:
            self.overlay_win = OverlayWindow(self)
        
        self.overlay_win.refresh_data()
        self.overlay_win.apply_theme()
        
        # Position the overlay in the top-right corner of the parent's geometry
        geom = self.geometry()
        x = geom.x() + geom.width() - self.overlay_win.width() - 20
        y = geom.y() + 40
        self.overlay_win.move(max(0, x), max(0, y))
        
        self.hide()
        self.overlay_win.show()
        self.overlay_win.raise_()
        self.overlay_win.activateWindow()

    def open_command_palette(self) -> None:
        """Instantiate and show the VSCode-style command palette dialog."""
        from src.gui.widgets.command_palette_dialog import CommandPaletteDialog
        palette = CommandPaletteDialog(self)
        palette.show_palette()

    def show_toast_notification(self, data: dict) -> None:
        """Instantiate and show a floating toast notification."""
        message = data.get("message", "")
        level = data.get("level", "info")
        from src.gui.widgets.notification_widget import NotificationWidget
        toast = NotificationWidget(message, level, self)
        toast.show_toast()


    def load_registered_tabs(self) -> None:
        """Dynamically add custom GUI tabs registered by plugins."""
        from src.core.plugin_registry import PluginRegistry
        registry = PluginRegistry()
        for tab_info in registry.tabs:
            tab_class = tab_info["class"]
            title = tab_info["title"]
            
            # Check if tab title is already added to self.tabs
            already_added = False
            for idx in range(self.tabs.count()):
                if self.tabs.tabText(idx) == title:
                    already_added = True
                    break
                    
            if not already_added:
                try:
                    tab_instance = tab_class()
                    idx = self.add_animated_tab(tab_instance, title)
                    if hasattr(self, "sidebar"):
                        if isinstance(self.sidebar, QTreeWidget):
                            # Find the "Extensions" category item
                            cat_uncategorized = None
                            for i in range(self.sidebar.topLevelItemCount()):
                                item = self.sidebar.topLevelItem(i)
                                if item.text(0) == "Extensions":
                                    cat_uncategorized = item
                                    break
                            if cat_uncategorized is None:
                                from src.core.theme_manager import ThemeManager
                                from src.core.design_system import get_icon
                                colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
                                acc = colors.get("ACCENT", "#00a3cc")
                                cat_uncategorized = QTreeWidgetItem(self.sidebar)
                                cat_uncategorized.setText(0, "Extensions")
                                cat_uncategorized.setIcon(0, get_icon("plug", size=20, color=acc))
                                cat_uncategorized.setFlags(cat_uncategorized.flags() & ~Qt.ItemIsSelectable)
                                cat_uncategorized.setFont(0, QFont("Inter", 10, QFont.Bold))
                                cat_uncategorized.setForeground(0, QColor(acc))
                                self.sidebar.expandItem(cat_uncategorized)
                                if hasattr(self, "category_items"):
                                    self.category_items.append(cat_uncategorized)
                            
                            child_item = QTreeWidgetItem(cat_uncategorized)
                            child_item.setText(0, title)
                            child_item.setFont(0, QFont("Inter", 9))
                            child_item.setData(0, Qt.UserRole, idx)
                            self.item_to_tab_index[child_item] = idx
                            self.tab_index_to_item[idx] = child_item
                        else:
                            self.sidebar.addItem(title)
                    logger.info("Dynamically registered tab '%s' added.", title)

                except Exception as exc:
                    logger.error("Failed to add dynamically registered tab '%s': %s", title, exc)

    def setup_menu_bar(self) -> None:
        """Create the application menu bar."""
        menu_bar = self.menuBar()
        
        # Windows menu for detached sub-windows
        windows_menu = menu_bar.addMenu('Windows')
        
        dash_action = QAction('Detached Dashboard', self)
        dash_action.triggered.connect(lambda: self.window_manager.open_window("Dashboard", DashboardTab))
        windows_menu.addAction(dash_action)
        
        codex_action = QAction('Detached Codex', self)
        codex_action.triggered.connect(lambda: self.window_manager.open_window("Codex", CodexTab))
        windows_menu.addAction(codex_action)
        
        charts_action = QAction('Detached Charts', self)
        charts_action.triggered.connect(lambda: self.window_manager.open_window("Progression Charts", ChartsTab))
        windows_menu.addAction(charts_action)
        
        graph_action = QAction('Detached Interactive Graph', self)
        graph_action.triggered.connect(lambda: self.window_manager.open_window("Interactive Graph", GraphTab))
        windows_menu.addAction(graph_action)

        perf_action = QAction('Performance Telemetry', self)
        perf_action.triggered.connect(self.open_performance_dashboard)
        windows_menu.addAction(perf_action)

        overlay_action = QAction('Overlay Mode (Ctrl+O)', self)
        overlay_action.triggered.connect(self.toggle_overlay_mode)
        windows_menu.addAction(overlay_action)

        help_menu = menu_bar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def open_performance_dashboard(self) -> None:
        """Instantiate and show the performance dashboard overlay."""
        from src.gui.performance_dashboard import PerformanceDashboard
        db = PerformanceDashboard(self)
        db.exec()

    def show_about_dialog(self) -> None:
        """Display the application's about dialog."""
        QMessageBox.about(
            self,
            'About',
            'Warframe Tactical Advisor\nVersion 1.0.0\nProfessional Companion Platform\n\nBuilt With:\nPython + PySide6\n\nAuthor:\nShubham Salunke'
        )

def main() -> Any:
    """Method main."""
    import sys
    if "--version" in sys.argv or "-v" in sys.argv:
        print("Warframe Tactical Advisor v1.0.0")
        sys.exit(0)


    # Install global exception handler
    from src.utils.error_handler import install_error_handler
    install_error_handler()

    # Initialize AppContext
    from src.core.app_context import AppContext
    context = AppContext()

    from PySide6.QtCore import Qt
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)

    from src.core.design_system import init_fonts
    init_fonts()


    # Load plugins via background worker in QThreadPool
    from PySide6.QtCore import QThreadPool
    from src.core.workers.plugin_worker import PluginWorker
    QThreadPool.globalInstance().start(PluginWorker())

    window = MainWindow()
    window.show()
    window.setup_shortcuts()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()