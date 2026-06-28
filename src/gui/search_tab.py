from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMessageBox, QPushButton, QGroupBox, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from src.core.search_engine_v3 import SearchEngineV3
from src.database.database import DatabaseManager

class SearchTab(QWidget):
    """GUI tab providing global search with fuzzy suggestions, history tracker, and favorites bookmarks."""

    def __init__(self) -> None:
        super().__init__()
        from src.core.app_context import AppContext
        self.engine = SearchEngineV3(AppContext())
        self.db = DatabaseManager()
        self.results_map = {}

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header = QLabel("🔍  Global Database Search")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #caa3ff; margin-bottom: 5px;")
        self.layout.addWidget(header)

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search weapons, mods, arcanes, quests, goals, relics…")
        self.search_input.setStyleSheet("font-size: 12px; padding: 6px;")
        self.search_input.textChanged.connect(self.run_search)
        self.layout.addWidget(self.search_input)

        # Splitter to show history and bookmarks side-by-side or results
        splitter = QSplitter(Qt.Horizontal)

        # Left Column: Search Results
        results_box = QGroupBox("Search Results")
        results_lay = QVBoxLayout(results_box)
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        results_lay.addWidget(self.results_list)

        # Quick action row for bookmarks
        btn_row = QHBoxLayout()
        self.bookmark_btn = QPushButton("★ Bookmark Selected")
        self.bookmark_btn.setStyleSheet("""
            QPushButton {
                background: #0f1a24; border: 1px solid #ffd56b;
                border-radius: 4px; color: #ffd56b; font-weight: bold; padding: 6px 12px;
            }
            QPushButton:hover { background: rgba(255,213,107,0.1); }
        """)
        self.bookmark_btn.clicked.connect(self.toggle_bookmark)
        btn_row.addWidget(self.bookmark_btn)
        
        self.clear_hist_btn = QPushButton("🗑 Clear History")
        self.clear_hist_btn.setStyleSheet("""
            QPushButton {
                background: #0f1a24; border: 1px solid #ff9fd4;
                border-radius: 4px; color: #ff9fd4; font-weight: bold; padding: 6px 12px;
            }
            QPushButton:hover { background: rgba(255,159,212,0.1); }
        """)
        self.clear_hist_btn.clicked.connect(self.clear_history)
        btn_row.addWidget(self.clear_hist_btn)
        results_lay.addLayout(btn_row)
        splitter.addWidget(results_box)

        # Right Column: History & Bookmarks panels
        right_panel = QWidget()
        right_lay = QVBoxLayout(right_panel)
        right_lay.setContentsMargins(0, 0, 0, 0)

        # Bookmarks list
        bookmarks_group = QGroupBox("Favorites & Bookmarks")
        bookmarks_lay = QVBoxLayout(bookmarks_group)
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.itemDoubleClicked.connect(self.on_bookmark_double_clicked)
        bookmarks_lay.addWidget(self.bookmarks_list)
        right_lay.addWidget(bookmarks_group, 1)

        # History list
        history_group = QGroupBox("Search History")
        history_lay = QVBoxLayout(history_group)
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_clicked)
        history_lay.addWidget(self.history_list)
        right_lay.addWidget(history_group, 1)

        splitter.addWidget(right_panel)
        self.layout.addWidget(splitter)

        self.setLayout(self.layout)
        QTimer.singleShot(0, self.load_history_and_bookmarks)

    def load_history_and_bookmarks(self) -> None:
        # History
        self.history_list.clear()
        hist = self.db.get_search_history(limit=15)
        for h in hist:
            self.history_list.addItem(h)

        # Bookmarks
        self.bookmarks_list.clear()
        bookmarks = self.engine.get_bookmarks()
        for b in sorted(list(bookmarks)):
            self.bookmarks_list.addItem(b.title())

    def run_search(self) -> None:
        self.results_list.clear()
        self.results_map.clear()
        
        query = self.search_input.text().strip()
        if not query:
            self.load_history_and_bookmarks()
            return
            
        results = self.engine.search(query)
        
        if not results:
            self.results_list.addItem("No results found.")
            return
            
        for r in results:
            star = "★ " if r.get("bookmarked") else "☆ "
            text = f"{star}[{r['category']}] {r['name']} - {r['details']}"
            item = QListWidgetItem(text)
            self.results_list.addItem(item)
            self.results_map[id(item)] = r

    def on_item_double_clicked(self, item: QListWidgetItem) -> None:
        data = self.results_map.get(id(item))
        if not data:
            return
        self._show_details(data)

    def on_bookmark_double_clicked(self, item: QListWidgetItem) -> None:
        name = item.text().lower()
        res = self.engine.search(name)
        if res:
            self._show_details(res[0])

    def on_history_clicked(self, item: QListWidgetItem) -> None:
        self.search_input.setText(item.text())

    def toggle_bookmark(self) -> None:
        item = self.results_list.currentItem()
        if not item:
            return
        data = self.results_map.get(id(item))
        if not data:
            return
        
        name = data["name"]
        bookmarks = self.engine.get_bookmarks()
        if name.lower() in bookmarks:
            self.engine.remove_bookmark(name)
            QMessageBox.information(self, "Bookmark Removed", f"Removed '{name}' from favorites.")
        else:
            self.engine.add_bookmark(name)
            QMessageBox.information(self, "Bookmark Added", f"Added '{name}' to favorites.")

        self.run_search()
        self.load_history_and_bookmarks()

    def clear_history(self) -> None:
        self.db.clear_search_history()
        self.load_history_and_bookmarks()
        QMessageBox.information(self, "History Cleared", "Search history cleared.")

    def _show_details(self, data: dict) -> None:
        wiki_info = f"\n\nWiki URL:\n{data['wiki_url']}" if data.get('wiki_url') else ""
        QMessageBox.information(
            self,
            f"{data['category']}: {data['name']}",
            f"Name: {data['name']}\n"
            f"Category: {data['category']}\n"
            f"Details: {data['details']}{wiki_info}"
        )
