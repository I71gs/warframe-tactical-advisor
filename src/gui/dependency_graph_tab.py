from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from src.core.player_loader import PlayerLoader
from src.core.dependency_graph_engine import DependencyGraphEngine

class DependencyGraphTab(QWidget):
    """GUI tab providing a hierarchical view of prerequisite paths for meta items, color-coded by unlock state."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = DependencyGraphEngine()
        
        self.layout = QVBoxLayout()
        
        # Header Row
        header_layout = QHBoxLayout()
        self.header = QLabel("Item Dependency Graph")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc;")
        header_layout.addWidget(self.header)
        
        header_layout.addStretch()
        
        header_layout.addWidget(QLabel("Select Target Item:"))
        self.item_selector = QComboBox()
        self.item_selector.addItems([
            "Phenmor",
            "Laetum",
            "Felarx",
            "Galvanized Chamber",
            "Galvanized Aptitude",
            "Primary Merciless",
            "Secondary Merciless",
            "Kuva Bramma",
            "Kuva Nukor",
            "Latron Incarnon",
            "Burston Incarnon",
            "Steel Path",
            "Arbitrations"
        ])
        self.item_selector.currentTextChanged.connect(self.load_graph)
        header_layout.addWidget(self.item_selector)
        
        self.layout.addLayout(header_layout)
        
        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Dependency Hierarchy", "Status"])
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #0f1724;
                border: 1px solid rgba(255, 255, 255, 0.05);
                color: #e6eef6;
            }
            QHeaderView::section {
                background-color: #0b1220;
                color: #caa3ff;
                padding: 4px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                font-weight: bold;
            }
        """)
        self.layout.addWidget(self.tree)
        
        self.setLayout(self.layout)
        self.load_graph()

    def load_graph(self) -> None:
        self.tree.clear()
        
        target = self.item_selector.currentText()
        if not target:
            return
            
        player = PlayerLoader().load_player()
        graph = self.engine.get_graph(target, player)
        
        self._populate_tree_item(self.tree, graph)
        self.tree.expandAll()
        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)

    def _populate_tree_item(self, parent_widget: QTreeWidget | QTreeWidgetItem, node: dict) -> QTreeWidgetItem:
        # Create Tree Item
        name = node["name"]
        status = node["status"]
        
        # Format status string
        if status == "unlocked":
            status_text = "✔ Completed / Owned"
            color = QColor("#22c55e") # Green
        elif status == "available":
            status_text = "➔ Available to Unlock"
            color = QColor("#ffb76b") # Orange
        else:
            status_text = "🔒 Locked by Prereq"
            color = QColor("#ef4444") # Red
            
        item = QTreeWidgetItem()
        item.setText(0, name)
        item.setText(1, status_text)
        
        # Apply coloring and font weights
        item.setForeground(0, color)
        item.setForeground(1, color)
        
        bold_font = QFont()
        bold_font.setBold(True)
        item.setFont(0, bold_font)
        
        # Add to parent
        if isinstance(parent_widget, QTreeWidget):
            parent_widget.addTopLevelItem(item)
        else:
            parent_widget.addChild(item)
            
        # Recurse children
        for child in node.get("children", []):
            self._populate_tree_item(item, child)
            
        return item
