from __future__ import annotations
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QWidget, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt
from src.core.app_context import AppContext

class SetupWizard(QDialog):
    """Interactive multi-step first-run setup wizard."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Warframe Tactical Advisor — Setup Wizard")
        self.setModal(True)
        self.resize(460, 320)
        self.context = AppContext()

        self.layout = QVBoxLayout(self)
        self.stacked = QStackedWidget()

        # Step 1: Welcome
        self.step1 = QWidget()
        s1_lay = QVBoxLayout(self.step1)
        s1_lay.addWidget(QLabel("<h2>Welcome to Warframe Tactical Advisor v11.0</h2>"), 0, Qt.AlignCenter)
        desc = QLabel(
            "This wizard will guide you through setting up your offline profile "
            "database, mastery goals, and optional integration settings."
        )
        desc.setWordWrap(True)
        s1_lay.addWidget(desc)
        s1_lay.addStretch()
        self.stacked.addWidget(self.step1)

        # Step 2: Account details
        self.step2 = QWidget()
        s2_lay = QVBoxLayout(self.step2)
        s2_lay.addWidget(QLabel("<h3>Configure Profile Identity</h3>"))
        s2_lay.addWidget(QLabel("Mastery Rank (0-33):"))
        self.mr_input = QLineEdit("0")
        s2_lay.addWidget(self.mr_input)

        self.sp_check = QCheckBox("Unlocked Steel Path Campaign")
        s2_lay.addWidget(self.sp_check)
        s2_lay.addStretch()
        self.stacked.addWidget(self.step2)

        # Step 3: Finish
        self.step3 = QWidget()
        s3_lay = QVBoxLayout(self.step3)
        s3_lay.addWidget(QLabel("<h3>Setup Complete!</h3>"))
        finish_lbl = QLabel(
            "Your offline profile data structure is ready to be initialized.\n"
            "Click Finish to launch the companion command center."
        )
        finish_lbl.setWordWrap(True)
        s3_lay.addWidget(finish_lbl)
        s3_lay.addStretch()
        self.stacked.addWidget(self.step3)

        self.layout.addWidget(self.stacked)

        # Navigation Bar
        nav_lay = QHBoxLayout()
        self.prev_btn = QPushButton("Back")
        self.prev_btn.clicked.connect(self.prev_step)
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_step)
        nav_lay.addWidget(self.prev_btn)
        nav_lay.addStretch()
        nav_lay.addWidget(self.next_btn)
        self.layout.addLayout(nav_lay)

        self.update_nav()

    def update_nav(self) -> None:
        idx = self.stacked.currentIndex()
        self.prev_btn.setEnabled(idx > 0)
        if idx == self.stacked.count() - 1:
            self.next_btn.setText("Finish")
        else:
            self.next_btn.setText("Next")

    def prev_step(self) -> None:
        idx = self.stacked.currentIndex()
        if idx > 0:
            self.stacked.setCurrentIndex(idx - 1)
            self.update_nav()

    def next_step(self) -> None:
        idx = self.stacked.currentIndex()
        if idx < self.stacked.count() - 1:
            # Validate input for Step 2
            if idx == 1:
                try:
                    mr = int(self.mr_input.text() or 0)
                    if mr < 0 or mr > 33:
                        raise ValueError()
                except ValueError:
                    QMessageBox.warning(self, "Invalid MR", "Mastery Rank must be an integer between 0 and 33.")
                    return
            self.stacked.setCurrentIndex(idx + 1)
            self.update_nav()
        else:
            self.finish_wizard()

    def finish_wizard(self) -> None:
        # Save player details to Database
        try:
            mr = int(self.mr_input.text() or 0)
            self.context.player_service.save_player(
                mastery_rank=mr,
                steel_path_unlocked=self.sp_check.isChecked()
            )
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to save profile setup: {exc}")
