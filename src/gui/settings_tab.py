from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QMessageBox, QComboBox, QFileDialog
from src.core.profile_manager import ProfileManager
from src.core.settings_manager import SettingsManager
from src.core.report_engine import ReportEngine

class WikiSyncWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def run(self) -> None:
        try:
            from tools.sync_wiki import sync_all_wiki
            results = sync_all_wiki()
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class SettingsTab(QWidget):
    """GUI tab managing application settings and multi-account switches."""

    def __init__(self, main_window: Any = None) -> None:
        """Initialize the class."""
        super().__init__()
        self.main_window = main_window
        self.settings_manager = SettingsManager()
        self.report_engine = ReportEngine()
        self.layout = QVBoxLayout()
        
        self.header = QLabel("Application Settings")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #caa3ff; margin-bottom: 10px;")
        self.layout.addWidget(self.header)
        
        # Profile Switcher Row
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Active Account Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["Default Account", "Alt Account"])
        profile_layout.addWidget(self.profile_combo)
        self.layout.addLayout(profile_layout)
        
        self.dark_mode = QCheckBox('Dark Mode')
        self.auto_refresh = QCheckBox('Auto Refresh')
        self.remember_size = QCheckBox('Remember Window Size')
        self.remember_tab = QCheckBox('Remember Last Open Tab')
        
        self.layout.addWidget(self.dark_mode)
        self.layout.addWidget(self.auto_refresh)
        self.layout.addWidget(self.remember_size)
        self.layout.addWidget(self.remember_tab)
        
        # Wiki Settings Row
        wiki_layout = QHBoxLayout()
        wiki_layout.addWidget(QLabel("Default Warframe Wiki:"))
        self.wiki_combo = QComboBox()
        self.wiki_combo.addItems(["Wiki.gg", "Fandom.com"])
        wiki_layout.addWidget(self.wiki_combo)
        self.layout.addLayout(wiki_layout)
        
        self.sync_wiki_btn = QPushButton('Sync Database with Wiki')
        self.layout.addWidget(self.sync_wiki_btn)

        self.backup_button = QPushButton('Backup Data')
        self.save_btn = QPushButton('Save Settings')
        
        self.layout.addWidget(self.backup_button)
        self.layout.addWidget(self.save_btn)
        
        # Report Export Buttons
        export_header = QLabel("Export Progression Reports")
        export_header.setStyleSheet("font-size: 14px; font-weight: bold; color: #caa3ff; margin-top: 15px; margin-bottom: 5px;")
        self.layout.addWidget(export_header)
        
        export_layout = QHBoxLayout()
        self.export_json_btn = QPushButton("Export JSON")
        self.export_csv_btn = QPushButton("Export CSV")
        self.export_txt_btn = QPushButton("Export TXT")
        
        export_layout.addWidget(self.export_json_btn)
        export_layout.addWidget(self.export_csv_btn)
        export_layout.addWidget(self.export_txt_btn)
        self.layout.addLayout(export_layout)
        
        self.layout.addStretch()
        
        self.setLayout(self.layout)
        self.load()
        
        self.save_btn.clicked.connect(self.save)
        self.backup_button.clicked.connect(self.backup_data)
        self.sync_wiki_btn.clicked.connect(self.sync_wiki_data)
        self.export_json_btn.clicked.connect(self.export_json)
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.export_txt_btn.clicked.connect(self.export_txt)

    def load(self) -> Any:
        """Load settings values into widgets."""
        self.settings_manager.load()
        self.dark_mode.setChecked(self.settings_manager.get('dark_mode', True))
        self.auto_refresh.setChecked(self.settings_manager.get('auto_refresh', True))
        self.remember_size.setChecked(self.settings_manager.get('remember_size', True))
        self.remember_tab.setChecked(self.settings_manager.get('remember_tab', True))
        
        profile = self.settings_manager.get('current_profile', 'default')
        if profile == 'alt':
            self.profile_combo.setCurrentText("Alt Account")
        else:
            self.profile_combo.setCurrentText("Default Account")
            
        use_wiki_gg = self.settings_manager.get('use_wiki_gg', True)
        if use_wiki_gg:
            self.wiki_combo.setCurrentText("Wiki.gg")
        else:
            self.wiki_combo.setCurrentText("Fandom.com")

    def save(self) -> Any:
        """Update and save settings to disk."""
        profile_val = 'alt' if self.profile_combo.currentText() == "Alt Account" else 'default'
        use_wiki_gg_val = self.wiki_combo.currentText() == "Wiki.gg"
        
        old_profile = self.settings_manager.get('current_profile', 'default')
        profile_changed = (old_profile != profile_val)
        
        self.settings_manager.update(
            dark_mode=bool(self.dark_mode.isChecked()), 
            auto_refresh=bool(self.auto_refresh.isChecked()), 
            remember_size=bool(self.remember_size.isChecked()), 
            remember_tab=bool(self.remember_tab.isChecked()),
            current_profile=profile_val,
            use_wiki_gg=use_wiki_gg_val
        )
        if not self.settings_manager.save():
            QMessageBox.critical(self, 'Error', 'Failed to save settings.')
            return
            
        if profile_changed and self.main_window and hasattr(self.main_window, 'context'):
            self.main_window.context.event_bus.publish("ACCOUNT_SWITCHED", {"profile": profile_val})
            
        if self.main_window and hasattr(self.main_window, 'apply_settings'):
            self.main_window.apply_settings()
            self.main_window.show_status('Settings saved')
            
        if self.main_window and hasattr(self.main_window, 'refresh_everything'):
            self.main_window.refresh_everything()
            
        QMessageBox.information(self, 'Saved', 'Settings saved successfully.')

    def backup_data(self) -> Any:
        """Trigger an on-demand database backup."""
        manager = ProfileManager()
        try:
            destination = manager.backup_profile()
            QMessageBox.information(self, 'Backup Complete', f'Backup saved to: {destination}')
            if self.main_window and hasattr(self.main_window, 'show_status'):
                self.main_window.show_status('Backup completed')
        except Exception as exc:
            QMessageBox.critical(self, 'Backup Failed', f'Failed to back up data: {exc}')

    def export_json(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Export JSON Report", "report.json", "JSON Files (*.json)")
        if filename:
            try:
                self.report_engine.export_json(filename)
                QMessageBox.information(self, "Success", f"JSON Report exported to: {filename}")
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Failed to export report: {exc}")

    def export_csv(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Export CSV Report", "report.csv", "CSV Files (*.csv)")
        if filename:
            try:
                self.report_engine.export_csv(filename)
                QMessageBox.information(self, "Success", f"CSV Report exported to: {filename}")
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Failed to export report: {exc}")

    def export_txt(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Export Text Report", "report.txt", "Text Files (*.txt)")
        if filename:
            try:
                self.report_engine.export_text(filename)
                QMessageBox.information(self, "Success", f"Text Report exported to: {filename}")
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Failed to export report: {exc}")

    def sync_wiki_data(self) -> None:
        """Starts background synchronization thread."""
        self.sync_wiki_btn.setEnabled(False)
        self.sync_wiki_btn.setText("Syncing with Wiki...")
        if self.main_window and hasattr(self.main_window, 'show_status'):
            self.main_window.show_status('Syncing with Warframe Wiki...')
            
        self.sync_worker = WikiSyncWorker()
        self.sync_worker.finished.connect(self.on_sync_finished)
        self.sync_worker.error.connect(self.on_sync_error)
        self.sync_worker.start()
        
    def on_sync_finished(self, results: dict) -> None:
        self.sync_wiki_btn.setEnabled(True)
        self.sync_wiki_btn.setText("Sync Database with Wiki")
        if self.main_window and hasattr(self.main_window, 'show_status'):
            self.main_window.show_status('Wiki sync complete')
            
        msg = (
            f"Database sync successful!\n\n"
            f"Updated:\n"
            f"- {results.get('weapons', 0)} Weapons\n"
            f"- {results.get('mods', 0)} Mods\n"
            f"- {results.get('arcanes', 0)} Arcanes\n"
            f"- {results.get('warframes', 0)} Warframes\n"
            f"- {results.get('companions', 0)} Companions\n"
            f"- {results.get('quests', 0)} Quests"
        )
        QMessageBox.information(self, "Synchronization Complete", msg)
        
        # Trigger reload of local datastores if needed
        if self.main_window and hasattr(self.main_window, 'refresh_everything'):
            self.main_window.refresh_everything()
        
    def on_sync_error(self, err: str) -> None:
        self.sync_wiki_btn.setEnabled(True)
        self.sync_wiki_btn.setText("Sync Database with Wiki")
        if self.main_window and hasattr(self.main_window, 'show_status'):
            self.main_window.show_status('Wiki sync failed')
        QMessageBox.critical(self, "Sync Failed", f"Error syncing with Wiki:\n{err}")