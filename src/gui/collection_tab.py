from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGroupBox, QGridLayout
from PySide6.QtCore import Qt
from src.core.player_loader import PlayerLoader
from src.core.collection_engine import CollectionEngine

from src.core.app_context import AppContext

class CollectionTab(QWidget):
    """GUI tab tracking overall inventory collections and completion percentages."""

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        self.engine = self.context.resource_service.collection_engine
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_collections())
        
        self.layout = QVBoxLayout()
        self.header = QLabel("My Inventory Collection Tracker")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc; margin-bottom: 5px;")
        self.layout.addWidget(self.header)
        
        # Overall Progress Box
        self.overall_box = QGroupBox("Overall Completion Score")
        self.overall_layout = QVBoxLayout(self.overall_box)
        self.overall_label = QLabel("Collection Completeness: 0%")
        self.overall_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #caa3ff;")
        self.overall_bar = QProgressBar()
        self.overall_layout.addWidget(self.overall_label)
        self.overall_layout.addWidget(self.overall_bar)
        self.layout.addWidget(self.overall_box)
        
        # Grid of sub-categories
        grid = QGridLayout()
        
        self.cards = {}
        categories = [
            ("warframes", "Warframes Collection", "#caa3ff"),
            ("weapons", "Meta Weapons Collection", "#ffb76b"),
            ("mods", "Arbitration Mods Collection", "#7fffb3"),
            ("arcanes", "Acolyte Arcanes Collection", "#7fb3ff")
        ]
        
        for idx, (key, title, color) in enumerate(categories):
            card = QGroupBox(title)
            card_layout = QVBoxLayout(card)
            
            lbl_val = QLabel("Owned: -")
            lbl_val.setStyleSheet("font-size: 12px; font-weight: 500;")
            
            bar = QProgressBar()
            bar.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 4px;
                }}
            """)
            
            card_layout.addWidget(lbl_val)
            card_layout.addWidget(bar)
            
            row = idx // 2
            col = idx % 2
            grid.addWidget(card, row, col)
            
            self.cards[key] = {"label": lbl_val, "bar": bar}
            
        self.layout.addLayout(grid)
        self.layout.addStretch()
        self.setLayout(self.layout)
        self.load_collections()

    def load_collections(self) -> None:
        player = PlayerLoader().load_player()
        res = self.engine.get_collection_status(player)
        
        self.overall_label.setText(f"Collection Completeness: {res['overall_pct']}%")
        self.overall_bar.setValue(int(res['overall_pct']))
        
        for key in ["warframes", "weapons", "mods", "arcanes"]:
            data = res[key]
            card_ui = self.cards[key]
            card_ui["label"].setText(f"Owned: {data['owned']} / {data['total']} ({data['pct']}%)")
            card_ui["bar"].setValue(int(data["pct"]))
network_collection = CollectionTab
