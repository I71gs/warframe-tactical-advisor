from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QGroupBox, QTextBrowser
from PySide6.QtCore import Qt
from src.core.player_loader import PlayerLoader
from src.core.codex_engine import CodexEngine
from src.core.app_context import AppContext

class CodexTab(QWidget):
    """GUI tab providing a comprehensive local Warframe Codex search tool with visual details cards."""

    def __init__(self, main_window=None) -> None:
        super().__init__()
        self.main_window = main_window
        self.context = AppContext()
        self.engine = CodexEngine()
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_items())
        
        # Main Layout
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Left Panel: Search & Select List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.header = QLabel("Intelligent Warframe Codex")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #bca3ff; margin-bottom: 5px;")
        left_layout.addWidget(self.header)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search weapons, warframes, mods, resources...")
        self.search_input.textChanged.connect(self.load_items)
        left_layout.addWidget(self.search_input)
        
        self.item_list = QListWidget()
        self.item_list.currentTextChanged.connect(self.show_details)
        left_layout.addWidget(self.item_list)
        
        self.main_layout.addWidget(left_widget, 1)
        
        # Right Panel: Details Page
        self.details_box = QGroupBox("Codex Entry Details")
        self.details_layout = QVBoxLayout(self.details_box)
        self.details_layout.setContentsMargins(5, 5, 5, 5)
        
        self.details_browser = QTextBrowser()
        self.details_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #0f1724;
                border: 1px solid rgba(255, 255, 255, 0.05);
                color: #e6eef6;
                padding: 15px;
                font-size: 13px;
                line-height: 1.5;
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
        
        category = details['category']
        html_content = f"""
            <h2 style='color: #00a3cc; margin-top: 0; margin-bottom: 5px;'>{details['name']}</h2>
            <p style='margin-top: 0;'><b>Category:</b> {category} | <b>Status:</b> {status_html}</p>
            <hr style='border: 1px solid rgba(255,255,255,0.05); margin-bottom: 15px;'>
            <p><b>Description:</b><br>{details['details']}</p>
        """
        
        if category == "WEAPON":
            html_content += f"""
                <p><b>Variants:</b><br>{details.get('variants', 'N/A')}</p>
                <p><b>Incarnon Evolutions:</b><br>{details.get('incarnons', 'None')}</p>
                <p><b>Acquisition:</b><br>{details.get('acquisition', 'N/A')}</p>
            """
        elif category == "WARFRAME":
            html_content += f"""
                <p><b>Abilities:</b><br>{details.get('abilities', 'N/A')}</p>
                <p><b>Passive Ability:</b><br>{details.get('passive', 'N/A')}</p>
                <p><b>Helminth Subsume:</b><br>{details.get('helminth', 'N/A')}</p>
                <p><b>Acquisition:</b><br>{details.get('acquisition', 'N/A')}</p>
            """
        elif category == "MOD":
            html_content += f"""
                <p><b>Mod Effects:</b><br>{details.get('effects', 'N/A')}</p>
                <p><b>Target Farming:</b><br>{details.get('farming', 'N/A')}</p>
            """
        elif category == "RESOURCE":
            html_content += f"""
                <p><b>Uses in Crafting:</b><br>{details.get('uses', 'N/A')}</p>
                <p><b>Best Farms:</b><br>{details.get('best_farms', 'N/A')}</p>
            """
        elif category == "FOCUS":
            html_content += f"""
                <p><b>Key Skills/Abilities:</b><br>{details.get('skills', 'N/A')}</p>
                <p><b>Unlock/Upgrade Method:</b><br>{details.get('acquisition', 'N/A')}</p>
            """
        elif category == "RAILJACK":
            html_content += f"""
                <p><b>Default/Available Weapons:</b><br>{details.get('weapons', 'N/A')}</p>
                <p><b>Unlock Quest/Method:</b><br>{details.get('acquisition', 'N/A')}</p>
            """
        elif category == "NECRAMECH":
            html_content += f"""
                <p><b>Abilities:</b><br>{details.get('abilities', 'N/A')}</p>
                <p><b>Farming & Assembly:</b><br>{details.get('acquisition', 'N/A')}</p>
            """
        elif category == "COMPANION":
            html_content += f"""
                <p><b>Unique Precept Mods/Abilities:</b><br>{details.get('abilities', 'N/A')}</p>
                <p><b>Acquisition:</b><br>{details.get('acquisition', 'N/A')}</p>
            """
            
        self.details_browser.setHtml(html_content)
