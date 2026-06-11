from typing import Any
import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QStatusBar, QMenu, QMessageBox
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

class MainWindow(QMainWindow):
    """Class MainWindow documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.setWindowTitle('Warframe Tactical Advisor')
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
        self.profile_tab = ProfileTab(refresh_callback=self.refresh_everything, status_callback=self.show_status)
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
        self.setCentralWidget(self.tabs)
        self.apply_settings()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.setup_menu_bar()

    def refresh_everything(self) -> None:
        """Refresh all application tabs and data sources."""
        self.profile_tab.load_profile()
        self.recommendations_tab.load_recommendations()
        self.progression_tab.load_progress()
        self.readiness_tab.load_readiness()
        self.quest_planner_tab.load_quests()
        self.dashboard_tab.load_dashboard()
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
        """Persist the selected tab index in settings."""
        if self.settings.get('remember_tab', True):
            self.settings.update(last_tab_index=index)

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
        super().closeEvent(event)

    def setup_shortcuts(self) -> None:
        """Bind global keyboard shortcuts."""
        QShortcut(QKeySequence('Ctrl+S'), self, activated=self.profile_tab.save_profile)
        QShortcut(QKeySequence('Ctrl+R'), self, activated=self.refresh_everything)
        QShortcut(QKeySequence('Ctrl+E'), self, activated=self.profile_tab.export_profile)
        QShortcut(QKeySequence('Ctrl+I'), self, activated=self.profile_tab.import_profile)
        QShortcut(QKeySequence('Ctrl+F'), self, activated=lambda: self.profile_tab.quest_input.setFocus())

    def setup_menu_bar(self) -> None:
        """Create the application menu bar."""
        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def show_about_dialog(self) -> None:
        """Display the application's about dialog."""
        QMessageBox.about(
            self,
            'About',
            'Warframe Tactical Advisor\nVersion 1.0\nOffline Edition\n\nBuilt With:\nPython + PySide6\n\nAuthor:\nShubham Salunke'
        )

def main() -> Any:
    """Method main."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.setup_shortcuts()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()