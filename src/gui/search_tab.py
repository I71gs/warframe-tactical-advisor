from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox
from PySide6.QtCore import Qt
from src.core.search_engine import SearchEngine

class SearchTab(QWidget):
    """GUI tab providing global search functionality across all data sources with interactive popups."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = SearchEngine()
        self.results_map = {}
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Global Database Search'))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search weapons, mods, arcanes, quests, goals...')
        self.search_input.textChanged.connect(self.run_search)
        self.layout.addWidget(self.search_input)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.layout.addWidget(self.results_list)
        
        self.setLayout(self.layout)

    def run_search(self) -> None:
        self.results_list.clear()
        self.results_map.clear()
        
        query = self.search_input.text().strip()
        if not query:
            return
            
        results = self.engine.search(query)
        
        if not results:
            self.results_list.addItem("No results found.")
            return
            
        for r in results:
            text = f"[{r['category']}] {r['name']} - {r['details']}"
            item = QListWidgetItem(text)
            self.results_list.addItem(item)
            
            # Map item memory address to full result data
            self.results_map[id(item)] = r

    def on_item_double_clicked(self, item: QListWidgetItem) -> None:
        data = self.results_map.get(id(item))
        if not data:
            return
            
        wiki_info = f"\n\nWiki URL:\n{data['wiki_url']}" if data.get('wiki_url') else ""
        QMessageBox.information(
            self,
            f"{data['category']}: {data['name']}",
            f"Name: {data['name']}\n"
            f"Category: {data['category']}\n"
            f"Details: {data['details']}{wiki_info}"
        )
