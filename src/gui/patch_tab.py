from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QGroupBox
from PySide6.QtCore import Qt, QTimer
from src.services.patch_service import PatchService

class PatchTab(QWidget):
    """GUI tab showing latest patch updates and Tenno advisor patch change highlights."""

    def __init__(self) -> None:
        super().__init__()
        self.service = PatchService()

        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(15, 15, 15, 15)

        # Title
        header = QLabel("📢  Patch Notes & System Changelogs")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #caa3ff;")
        lay.addWidget(header)

        # "What's New" Box
        self.new_box = QGroupBox("What's New in this Version")
        self.new_box.setStyleSheet("""
            QGroupBox {
                background: #0d1117; border: 1px solid #caa3ff44;
                border-radius: 6px; font-weight: bold; color: #caa3ff; margin-top: 8px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; }
        """)
        new_lay = QVBoxLayout(self.new_box)
        self.version_lbl = QLabel("Checking version…")
        self.version_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #7fffb3;")
        new_lay.addWidget(self.version_lbl)

        self.notes_area = QTextEdit()
        self.notes_area.setReadOnly(True)
        self.notes_area.setStyleSheet("""
            QTextEdit {
                background: #0d1117; border: none;
                color: #c8d6e5; font-family: Consolas, monospace; font-size: 11px;
            }
        """)
        new_lay.addWidget(self.notes_area)
        lay.addWidget(self.new_box)

        # Action row
        action_row = QHBoxLayout()
        self.mark_btn = QPushButton("Mark Patch as Read")
        self.mark_btn.setStyleSheet("""
            QPushButton {
                background: #0f1a24; border: 1px solid #7fffb3;
                border-radius: 4px; color: #7fffb3; font-weight: bold; padding: 6px 14px;
            }
            QPushButton:hover { background: rgba(127,255,179,0.1); }
        """)
        self.mark_btn.clicked.connect(self.mark_as_read)
        action_row.addWidget(self.mark_btn)
        action_row.addStretch()

        lay.addLayout(action_row)
        self.setLayout(lay)

        QTimer.singleShot(0, self.load_patch_notes)

    def load_patch_notes(self) -> None:
        notes = self.service.fetch_latest_patch_notes()
        last_seen = self.service.get_last_seen_version()
        current = notes.get("version", "10.0.1")

        self.version_lbl.setText(
            f"Latest: Version {current}  |  Last seen: Version {last_seen}"
        )

        lines = [
            f"Title: {notes.get('title', 'System Update')}",
            f"Published: {notes.get('date', '—')}",
            "",
            "Key Changes Summary:",
        ]
        for chg in notes.get("changes", []):
            lines.append(f"  • {chg}")

        if last_seen != current:
            lines.append("\n⚠️  Attention: Game version has changed since your last session!")

        self.notes_area.setPlainText("\n".join(lines))

    def mark_as_read(self) -> None:
        notes = self.service.fetch_latest_patch_notes()
        current = notes.get("version", "10.0.1")
        self.service.set_last_seen_version(current)
        self.load_patch_notes()
