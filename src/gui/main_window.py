import sys
from src.gui.progression_tab import ProgressionTab

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget
)

from src.gui.profile_tab import ProfileTab
from src.gui.recommendations_tab import RecommendationsTab

from src.gui.build_advisor_tab import (
    BuildAdvisorTab
)

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Warframe Tactical Advisor")

        self.resize(1000, 700)

        self.progression_tab = ProgressionTab()

        self.build_tab = BuildAdvisorTab()

        # -------------------------
        # Central Tab Widget
        # -------------------------
        self.tabs = QTabWidget()

        # -------------------------
        # Tabs
        # -------------------------
        self.profile_tab = ProfileTab(
            refresh_callback=self.refresh_recommendations
        )

        self.recommendations_tab = RecommendationsTab()

        self.tabs.addTab(
            self.profile_tab,
            "Profile"
        )

        self.tabs.addTab(
            self.recommendations_tab,
            "Recommendations"
        )

        self.tabs.addTab(
            self.progression_tab,
            "Progression"
        )

        self.tabs.addTab(
            self.build_tab,
            "Build Advisor"
        )

        self.setCentralWidget(self.tabs)

    # -------------------------
    # Refresh Hook
    # -------------------------
    def refresh_recommendations(self):

        self.recommendations_tab.load_recommendations()

        self.progression_tab.load_progress()

def main():

    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()