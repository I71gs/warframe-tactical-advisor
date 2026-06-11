from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton, QMessageBox
from src.core.profile_manager import ProfileManager
from src.core.settings_manager import SettingsManager

class SettingsTab(QWidget):
    """Class SettingsTab documentation."""

    def __init__(self, main_window: Any=None) -> None:
        """Initialize the class."""
        super().__init__()
        self.main_window = main_window
        self.settings_manager = SettingsManager()
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Settings'))
        self.dark_mode = QCheckBox('Dark Mode')
        self.auto_refresh = QCheckBox('Auto Refresh')
        self.remember_size = QCheckBox('Remember Window Size')
        self.remember_tab = QCheckBox('Remember Last Open Tab')
        self.backup_button = QPushButton('Backup Data')
        self.save_btn = QPushButton('Save Settings')
        self.layout.addWidget(self.dark_mode)
        self.layout.addWidget(self.auto_refresh)
        self.layout.addWidget(self.remember_size)
        self.layout.addWidget(self.remember_tab)
        self.layout.addWidget(self.backup_button)
        self.layout.addWidget(self.save_btn)
        self.setLayout(self.layout)
        self.load()
        self.save_btn.clicked.connect(self.save)
        self.backup_button.clicked.connect(self.backup_data)

    def load(self) -> Any:
        """Method load."""
        self.dark_mode.setChecked(self.settings_manager.get('dark_mode', True))
        self.auto_refresh.setChecked(self.settings_manager.get('auto_refresh', True))
        self.remember_size.setChecked(self.settings_manager.get('remember_size', True))
        self.remember_tab.setChecked(self.settings_manager.get('remember_tab', True))

    def save(self) -> Any:
        """Method save."""
        self.settings_manager.update(dark_mode=bool(self.dark_mode.isChecked()), auto_refresh=bool(self.auto_refresh.isChecked()), remember_size=bool(self.remember_size.isChecked()), remember_tab=bool(self.remember_tab.isChecked()))
        if not self.settings_manager.save():
            QMessageBox.critical(self, 'Error', 'Failed to save settings.')
            return
        if self.main_window and hasattr(self.main_window, 'apply_settings'):
            self.main_window.apply_settings()
            self.main_window.show_status('Settings saved')
        QMessageBox.information(self, 'Saved', 'Settings saved successfully.')

    def backup_data(self) -> Any:
        """Method backup_data."""
        manager = ProfileManager()
        try:
            destination = manager.backup_profile()
            QMessageBox.information(self, 'Backup Complete', f'Backup saved to: {destination}')
            if self.main_window and hasattr(self.main_window, 'show_status'):
                self.main_window.show_status('Backup completed')
        except Exception as exc:
            QMessageBox.critical(self, 'Backup Failed', f'Failed to back up data: {exc}')