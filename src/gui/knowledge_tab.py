from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget, QLabel
from src.core.knowledge_base import KnowledgeBase
from src.core.weapon_database import WEAPONS
from src.core.arcane_database import ARCANES

class KnowledgeTab(QWidget):
    """Class KnowledgeTab documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Knowledge Base'))
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search weapons, mods, arcanes...')
        self.search.textChanged.connect(self.on_search)
        self.list_widget = QListWidget()
        self.layout.addWidget(self.search)
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)
        self.kb = KnowledgeBase()
        self.items = []
        for w in WEAPONS:
            self.items.append({'type': 'weapon', 'name': w['name'], 'source': w.get('acquisition'), 'category': w.get('category')})
        for a in ARCANES:
            self.items.append({'type': 'arcane', 'name': a['name'], 'source': a.get('acquisition'), 'category': a.get('type')})
        for m in self.kb.mods:
            self.items.append({'type': 'mod', 'name': m.get('name'), 'source': m.get('source'), 'category': m.get('category')})
        self.refresh_list()

    def refresh_list(self) -> Any:
        """Method refresh_list."""
        self.list_widget.clear()
        for it in self.items:
            self.list_widget.addItem(f"[{it['type'].upper()}] {it['name']} - Source: {it.get('source', 'unknown')}")

    def on_search(self, text: Any) -> Any:
        """Method on_search."""
        q = text.lower()
        self.list_widget.clear()
        for it in self.items:
            if q in it['name'].lower() or q in (it.get('source') or '').lower():
                self.list_widget.addItem(f"[{it['type'].upper()}] {it['name']} - Source: {it.get('source', 'unknown')}")