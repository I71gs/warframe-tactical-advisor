from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QGroupBox, QTextBrowser
from PySide6.QtCore import Qt
from src.core.player_loader import PlayerLoader
from src.core.encyclopedia_engine import EncyclopediaEngine

from src.core.app_context import AppContext

class EncyclopediaTab(QWidget):
    """GUI tab providing a local Warframe Codex search tool with visual information cards."""

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        self.engine = self.context.build_service.encyclopedia
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_items())
        
        # Main Layout
        self.main_layout = QHBoxLayout()
        
        # Left Panel: Search & Select List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.header = QLabel("Local Warframe Codex & Database")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc; margin-bottom: 5px;")
        left_layout.addWidget(self.header)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search weapons, mods, arcanes, warframes...")
        self.search_input.textChanged.connect(self.load_items)
        left_layout.addWidget(self.search_input)
        
        self.item_list = QListWidget()
        self.item_list.currentTextChanged.connect(self.show_details)
        left_layout.addWidget(self.item_list)
        
        self.main_layout.addWidget(left_widget, 1)
        
        # Right Panel: Details Page
        self.details_box = QGroupBox("Codex Entry Details")
        self.details_layout = QVBoxLayout(self.details_box)
        
        self.details_browser = QTextBrowser()
        self.details_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #0f1724;
                border: 1px solid rgba(255, 255, 255, 0.05);
                color: #e6eef6;
                padding: 10px;
                font-size: 12px;
            }
        """)
        self.details_layout.addWidget(self.details_browser)
        
        self.main_layout.addWidget(self.details_box, 2)
        
        self.setLayout(self.main_layout)
        self.load_items()

    def load_items(self) -> None:
        self.item_list.clear()
        query = self.search_input.text()
        results = self.engine.search(query)
        
        for r in results:
            text = f"[{r['category']}] {r['name']}"
            item = QListWidgetItem(text)
            self.item_list.addItem(item)
            
        if self.item_list.count() > 0:
            self.item_list.setCurrentRow(0)

    def show_details(self, item_text: str) -> None:
        if not item_text:
            self.details_browser.clear()
            return
            
        # Parse name from string (e.g. "[WEAPON] Phenmor" -> "Phenmor")
        try:
            name = item_text.split("] ")[1].strip()
        except IndexError:
            name = item_text.strip()
            
        player = PlayerLoader().load_player()
        details = self.engine.get_details(name, player)
        if not details:
            self.details_browser.clear()
            return
            
        status_html = "<span style='color: #22c55e; font-weight: bold;'>✔ OWNED</span>" if details["owned"] else "<span style='color: #ef4444; font-weight: bold;'>✗ MISSING</span>"
        
        html_content = f"""
            <h2 style='color: #00a3cc; margin-top: 0;'>{details['name']}</h2>
            <hr style='border: 1px solid rgba(255,255,255,0.05);'>
            <p><b>Category:</b> {details['category']}</p>
            <p><b>Account Status:</b> {status_html}</p>
            <p><b>Acquisition Location:</b><br>{details['acquisition']}</p>
            <p><b>Synergies:</b><br>{details['synergies']}</p>
            <p><b>Recommended Build Focus:</b><br>{details['builds']}</p>
            <p><b>Dependency Chain:</b><br>{details['dependencies']}</p>
        """
        self.details_browser.setHtml(html_content)
