from typing import Any
import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QStatusBar, QMenu, QMessageBox, QListWidget, QHBoxLayout, QWidget

from PySide6.QtGui import QAction, QIcon, QKeySequence, QShortcut
from src.core.settings_manager import SettingsManager
from src.utils.logger import logger
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


class MainWindow(QMainWindow):
    """Class MainWindow documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.setWindowTitle('Warframe Tactical Advisor')
        
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
        self.tabs.addTab(self.dashboard_tab, 'Dashboard')
        self.tabs.addTab(self.profile_tab, 'Profile')
        self.tabs.addTab(self.recommendations_tab, 'Recommendations')
        self.tabs.addTab(self.progression_tab, 'Progression')
        self.tabs.addTab(self.readiness_tab, 'Readiness')
        self.tabs.addTab(self.quest_planner_tab, 'Quest Planner')
        self.tabs.addTab(self.build_tab, 'Build Advisor')
        self.tabs.addTab(self.loadout_tab, 'Loadout Advisor')
        self.tabs.addTab(self.knowledge_tab, 'Knowledge Base')
        self.tabs.addTab(self.statistics_tab, 'Statistics')
        self.tabs.addTab(self.settings_tab, 'Settings')
        self.apply_settings()

        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.setup_menu_bar()
        self.goal_planner_tab = (
            GoalPlannerTab()
        )
        self.tabs.addTab(self.goal_planner_tab, 'Goal Planner')
        
        # New Stage 2 Coach Tabs
        self.gap_tab = GapAnalysisTab()
        self.build_simulator_tab = BuildSimulatorTab()
        self.weapon_tiers_tab = WeaponTiersTab()
        self.tabs.addTab(self.gap_tab, 'Gap Analyzer')
        self.tabs.addTab(self.build_simulator_tab, 'Build Simulator')
        self.tabs.addTab(self.weapon_tiers_tab, 'Weapon Tiers')

        # Phase 3 & 4 Tabs
        self.daily_tab = DailyTab()
        self.weekly_tab = WeeklyTab()
        self.timeline_tab = TimelineTab()
        self.charts_tab = ChartsTab()
        self.search_tab = SearchTab()
        self.tabs.addTab(self.daily_tab, 'Daily Objectives')
        self.tabs.addTab(self.weekly_tab, 'Weekly Planner')
        self.tabs.addTab(self.timeline_tab, '30-Day Timeline')
        self.tabs.addTab(self.charts_tab, 'Progression Charts')
        self.tabs.addTab(self.search_tab, 'Global Search')

        # Stage 3 & 4 new tabs
        self.milestone_tab = MilestoneTab()
        self.dependency_graph_tab = DependencyGraphTab()
        self.graph_tab = GraphTab()
        self.resource_tab = ResourceTab()
        self.farming_routes_tab = FarmingRoutesTab()
        self.team_tab = TeamTab()
        self.achievements_tab = AchievementsTab()
        
        self.tabs.addTab(self.milestone_tab, 'Roadmap Milestones')
        self.tabs.addTab(self.dependency_graph_tab, 'Dependency Graph')
        self.tabs.addTab(self.graph_tab, 'Interactive Graph')
        self.tabs.addTab(self.resource_tab, 'Resource Planner')
        self.tabs.addTab(self.farming_routes_tab, 'Farming Routes')
        self.tabs.addTab(self.team_tab, 'Team Synergy')
        self.tabs.addTab(self.achievements_tab, 'Badges & Achievements')

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

        self.tabs.addTab(self.encyclopedia_tab, 'Encyclopedia')
        self.tabs.addTab(self.codex_tab, 'Codex')
        self.tabs.addTab(self.collection_tab, 'Collection Tracker')
        self.tabs.addTab(self.mastery_tab, 'Mastery Rank Planner')
        self.tabs.addTab(self.relic_tab, 'Relic Planner')
        self.tabs.addTab(self.incarnon_tab, 'Incarnon Evolutions')
        self.tabs.addTab(self.circuit_tab, 'Circuit Forecast')
        self.tabs.addTab(self.duviri_tab, 'Duviri Upgrades')
        self.tabs.addTab(self.companion_tab, 'Companion Synergy')
        self.tabs.addTab(self.economy_tab, 'Economy Deficits')
        self.tabs.addTab(self.session_tab, 'Session Planner')
        self.tabs.addTab(self.benchmark_tab, 'Benchmark Engine')
        self.tabs.addTab(self.replay_tab, 'Progression Replay')
        self.comparison_tab = ComparisonTab()
        self.tabs.addTab(self.comparison_tab, 'Account Comparison')
        self.route_tab = RouteTab()
        self.tabs.addTab(self.route_tab, 'Tactical Routes')
        self.build_library_tab = BuildLibraryTab()
        self.tabs.addTab(self.build_library_tab, 'Build Library')
        self.theme_editor_tab = ThemeEditorTab(self)
        self.tabs.addTab(self.theme_editor_tab, 'Theme Studio')
        self.patch_tab = PatchTab()
        self.tabs.addTab(self.patch_tab, 'Patch Notes')
        self.load_registered_tabs()

        # Setup sidebar layout
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebarNav")
        self.sidebar.setFixedWidth(190)
        
        for idx in range(self.tabs.count()):
            self.sidebar.addItem(self.tabs.tabText(idx))
            
        self.sidebar.currentRowChanged.connect(self.tabs.setCurrentIndex)
        self.tabs.currentChanged.connect(self._sync_tabs_to_sidebar)
        self.tabs.tabBar().hide()
        
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.tabs)
        self.setCentralWidget(container)

    def _sync_tabs_to_sidebar(self, index: int) -> None:
        if hasattr(self, "sidebar"):
            self.sidebar.blockSignals(True)
            self.sidebar.setCurrentRow(index)
            self.sidebar.blockSignals(False)



    def refresh_everything(self) -> None:
        """Refresh all application tabs and data sources."""
        import time
        start_time = time.perf_counter()
        self.profile_tab.load_profile()
        self.recommendations_tab.load_recommendations()
        self.progression_tab.load_progress()
        self.readiness_tab.load_readiness()
        self.quest_planner_tab.load_quests()
        self.dashboard_tab.load_dashboard()
        try:
            self.goal_planner_tab.load_plan()
        except Exception:
            pass
        try:
            self.gap_tab.load_gaps()
        except Exception:
            pass
        try:
            self.build_simulator_tab.run_simulation()
        except Exception:
            pass
        try:
            self.weapon_tiers_tab.load_tiers()
        except Exception:
            pass
        try:
            self.loadout_tab.load_data()
        except Exception:
            pass
        try:
            self.knowledge_tab.refresh_list()
        except Exception:
            pass
        try:
            self.statistics_tab.load_stats()
        except Exception:
            pass
        try:
            self.daily_tab.load_daily()
        except Exception:
            pass
        try:
            self.weekly_tab.load_weekly()
        except Exception:
            pass
        try:
            self.timeline_tab.load_timeline()
        except Exception:
            pass
        try:
            self.charts_tab.render_selected_chart()
        except Exception:
            pass
        try:
            self.milestone_tab.load_milestones()
        except Exception:
            pass
        try:
            self.dependency_graph_tab.load_graph()
        except Exception:
            pass
        try:
            self.graph_tab.load_graph()
        except Exception:
            pass
        try:
            self.resource_tab.load_planner()
        except Exception:
            pass
        try:
            self.farming_routes_tab.load_routes()
        except Exception:
            pass
        try:
            self.team_tab.calculate_synergy()
        except Exception:
            pass
        try:
            self.achievements_tab.load_achievements()
        except Exception:
            pass
        try:
            self.encyclopedia_tab.load_items()
        except Exception:
            pass
        try:
            self.codex_tab.load_items()
        except Exception:
            pass
        try:
            self.collection_tab.load_collections()
        except Exception:
            pass
        try:
            self.mastery_tab.load_planner()
        except Exception:
            pass
        try:
            self.relic_tab.load_relics()
        except Exception:
            pass
        try:
            self.incarnon_tab.load_incarnon()
        except Exception:
            pass
        try:
            self.circuit_tab.load_circuit()
        except Exception:
            pass
        try:
            self.duviri_tab.load_duviri()
        except Exception:
            pass
        try:
            self.companion_tab.load_companions()
        except Exception:
            pass
        try:
            self.economy_tab.load_economy()
        except Exception:
            pass
        try:
            self.session_tab.load_session()
        except Exception:
            pass
        try:
            self.benchmark_tab.load_benchmarks()
        except Exception:
            pass
        try:
            self.replay_tab.load_timeline()
        except Exception:
            pass
        try:
            self.comparison_tab.populate_dropdowns()
        except Exception:
            pass
        try:
            self.route_tab.load_routes()
        except Exception:
            pass
        try:
            self.build_library_tab.refresh_list()
        except Exception:
            pass
        try:
            self.theme_editor_tab.preset_combo.clear()
            self.theme_editor_tab.preset_combo.addItems(self.theme_editor_tab.tm.get_themes())
        except Exception:
            pass
        try:
            self.patch_tab.load_patch_notes()
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
        logger.info('Status: %s', message)

    def apply_settings(self) -> None:
        """Apply persisted user settings to the window and auto-refresh timer."""
        try:
            from src.core.theme_manager import ThemeManager
            from src.core.theme_engine import ThemeEngine
            tm = ThemeManager()
            te = ThemeEngine()
            active_theme = tm.get_active_theme_name()
            colors = tm.get_theme_colors(active_theme)
            stylesheet = te.compile_stylesheet(colors)
            self.setStyleSheet(stylesheet)
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
        else:
            self.resize(1000, 700)
        if self.settings.get('remember_tab', True):
            self.tabs.setCurrentIndex(self.settings.get('last_tab_index', 0))
        if self.settings.get('auto_refresh', True):
            self.refresh_timer.start(180000)
        else:
            self.refresh_timer.stop()

    def on_tab_changed(self, index: int) -> None:
        """Persist the selected tab index in settings and track analytics."""
        if self.settings.get('remember_tab', True):
            self.settings.update(last_tab_index=index)
        try:
            tab_name = self.tabs.tabText(index)
            self.context.analytics_service.track_tab_view(tab_name)
        except Exception:
            pass

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
            self.settings.update(window_size={'width': self.width(), 'height': self.height()})
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
        QShortcut(QKeySequence('Ctrl+P'), self, activated=self.open_command_palette)

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
                    self.tabs.addTab(tab_instance, title)
                    if hasattr(self, "sidebar"):
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
            'Warframe Tactical Advisor\nVersion 11.0.0\nProfessional Companion Platform\n\nBuilt With:\nPython + PySide6\n\nAuthor:\nShubham Salunke'
        )

def main() -> Any:
    """Method main."""
    import sys
    if "--version" in sys.argv or "-v" in sys.argv:
        print("Warframe Tactical Advisor v11.0.0")
        sys.exit(0)


    # Install global exception handler
    from src.utils.error_handler import install_error_handler
    install_error_handler()

    # Initialize AppContext
    from src.core.app_context import AppContext
    context = AppContext()

    app = QApplication(sys.argv)


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