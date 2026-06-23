from __future__ import annotations
from typing import Any
from pathlib import Path
import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QMessageBox
from PySide6.QtCore import Qt, QEvent
from src.core.search_engine_v2 import SearchEngineV2
from src.core.report_engine import ReportEngine
from src.core.app_context import AppContext

PALETTE_STYLE = """
QDialog {
    background: #0b1220;
    border: 2px solid #00a3cc;
    border-radius: 8px;
}
QLineEdit {
    background: #0f1724;
    color: #e6eef6;
    font-size: 14px;
    padding: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}
QListWidget {
    background: transparent;
    border: none;
    color: #e6eef6;
}
QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}
QListWidget::item:selected {
    background: #0f1a24;
    color: #00a3cc;
    border-radius: 4px;
}
"""

class CommandPaletteDialog(QDialog):
    """VSCode-style floating command palette dialog."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        self.context = AppContext()
        self.search_engine = SearchEngineV2(self.context)
        self.report_engine = ReportEngine()
        
        self.setStyleSheet(PALETTE_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a command or search query (Ctrl+P)...")
        layout.addWidget(self.search_input)
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        self.resize(500, 350)
        
        self.search_input.textChanged.connect(self.update_list)
        self.list_widget.itemActivated.connect(self.execute_selection)
        self.list_widget.itemClicked.connect(self.execute_selection)
        
        # Default commands
        self.commands = [
            {"label": "Command: Backup Database", "type": "action", "action": self.action_backup},
            {"label": "Command: Open Charts", "type": "action", "action": lambda: self.action_switch_tab("Progression Charts")},
            {"label": "Command: Open Build Simulator", "type": "action", "action": lambda: self.action_switch_tab("Build Simulator")},
            {"label": "Command: Open Encyclopedia", "type": "action", "action": lambda: self.action_switch_tab("Encyclopedia")},
            {"label": "Command: Switch Account to Default", "type": "action", "action": lambda: self.action_switch_account("default")},
            {"label": "Command: Switch Account to Alt", "type": "action", "action": lambda: self.action_switch_account("alt")},
            {"label": "Command: Export Report", "type": "action", "action": self.action_export_report},
        ]
        
        self.update_list()
        
        # Install event filter to handle navigation & selection
        self.search_input.installEventFilter(self)

    def show_palette(self) -> None:
        """Positions and displays the command palette."""
        if self.parent() and hasattr(self.parent(), "geometry"):
            parent_geom = self.parent().geometry()
            x = parent_geom.x() + (parent_geom.width() - self.width()) // 2
            y = parent_geom.y() + 80
            self.move(x, y)
        if 'pytest' not in sys.modules:
            self.exec()
        else:
            self.show()

    def eventFilter(self, obj: Any, event: Any) -> bool:
        if obj is self.search_input and event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Escape:
                self.reject()
                return True
            elif key == Qt.Key_Down:
                current_row = self.list_widget.currentRow()
                next_row = (current_row + 1) % self.list_widget.count() if self.list_widget.count() > 0 else 0
                self.list_widget.setCurrentRow(next_row)
                return True
            elif key == Qt.Key_Up:
                current_row = self.list_widget.currentRow()
                prev_row = (current_row - 1 + self.list_widget.count()) % self.list_widget.count() if self.list_widget.count() > 0 else 0
                self.list_widget.setCurrentRow(prev_row)
                return True
            elif key in (Qt.Key_Return, Qt.Key_Enter):
                self.execute_selection(self.list_widget.currentItem())
                return True
        return super().eventFilter(obj, event)

    def update_list(self) -> None:
        """Update items shown in the list widget based on search query."""
        self.list_widget.clear()
        query = self.search_input.text().strip()
        
        from src.core.plugin_registry import PluginRegistry
        registry = PluginRegistry()

        if not query:
            # Show all default commands
            for cmd in self.commands:
                item = QListWidgetItem(cmd["label"])
                item.setData(Qt.UserRole, cmd)
                self.list_widget.addItem(item)
            # Add plugin commands
            for cmd in registry.commands:
                label = f"Plugin: {cmd['label']}"
                item = QListWidgetItem(label)
                item.setData(Qt.UserRole, {"type": "action", "action": cmd["action"]})
                self.list_widget.addItem(item)
            if self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(0)
            return

        # Show commands that match query
        for cmd in self.commands:
            if query.lower() in cmd["label"].lower():
                item = QListWidgetItem(cmd["label"])
                item.setData(Qt.UserRole, cmd)
                self.list_widget.addItem(item)

        # Show plugin commands that match query
        for cmd in registry.commands:
            label = f"Plugin: {cmd['label']}"
            if query.lower() in label.lower():
                item = QListWidgetItem(label)
                item.setData(Qt.UserRole, {"type": "action", "action": cmd["action"]})
                self.list_widget.addItem(item)

        # Query the search engine for games items/tasks/plugins/etc.
        search_results = self.search_engine.search(query)
        for res in search_results:
            label = f"[{res['category']}] {res['name']} - {res['details']}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, {"type": "search_result", "data": res})
            self.list_widget.addItem(item)
            
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def execute_selection(self, item: QListWidgetItem | None) -> None:
        """Trigger action associated with selected command palette entry."""
        if not item:
            return
        cmd = item.data(Qt.UserRole)
        if not cmd:
            return
            
        self.accept()
        
        if cmd["type"] == "action":
            cmd["action"]()
        elif cmd["type"] == "search_result":
            res = cmd["data"]
            self.action_show_search_result(res)

    def action_backup(self) -> None:
        try:
            path = self.context.player_service.backup_profile()
            self.context.event_bus.publish("NOTIFICATION", {
                "message": f"Backup created successfully: {Path(path).name}",
                "level": "success"
            })
        except Exception as exc:
            self.context.event_bus.publish("NOTIFICATION", {
                "message": f"Backup failed: {exc}",
                "level": "error"
            })

    def action_switch_tab(self, tab_name: str) -> None:
        parent = self.parent()
        if parent and hasattr(parent, "tabs"):
            for idx in range(parent.tabs.count()):
                if parent.tabs.tabText(idx).lower() == tab_name.lower():
                    parent.tabs.setCurrentIndex(idx)
                    break

    def action_switch_account(self, profile_name: str) -> None:
        try:
            self.context.player_service.switch_profile(profile_name)
        except Exception as exc:
            self.context.event_bus.publish("NOTIFICATION", {
                "message": f"Account switch failed: {exc}",
                "level": "error"
            })

    def action_export_report(self) -> None:
        # Avoid file dialogues during test run
        if 'pytest' in sys.modules:
            return
        from PySide6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self.parent(), "Export Report", "report.json", "JSON Files (*.json);;CSV Files (*.csv);;Text Files (*.txt)"
        )
        if filename:
            try:
                if filename.endswith(".json"):
                    self.report_engine.export_json(filename)
                elif filename.endswith(".csv"):
                    self.report_engine.export_csv(filename)
                else:
                    self.report_engine.export_text(filename)
                self.context.event_bus.publish("NOTIFICATION", {
                    "message": f"Report exported: {Path(filename).name}",
                    "level": "success"
                })
            except Exception as exc:
                self.context.event_bus.publish("NOTIFICATION", {
                    "message": f"Report export failed: {exc}",
                    "level": "error"
                })

    def action_show_search_result(self, res: dict) -> None:
        if 'pytest' in sys.modules:
            return
        wiki_info = f"\n\nWiki URL:\n{res['wiki_url']}" if res.get('wiki_url') else ""
        QMessageBox.information(
            self.parent(),
            f"{res['category']}: {res['name']}",
            f"Name: {res['name']}\n"
            f"Category: {res['category']}\n"
            f"Details: {res['details']}{wiki_info}"
        )
