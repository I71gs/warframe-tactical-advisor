from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt
from src.core.player_loader import PlayerLoader
from src.core.dependency_graph_engine import DependencyGraphEngine
from src.gui.widgets.graph_visualizer import GraphVisualizer

class GraphTab(QWidget):
    """GUI tab rendering interactive, clickable dependency node maps for progression targets."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = DependencyGraphEngine()
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Header Row
        header_layout = QHBoxLayout()
        self.header = QLabel("Interactive Dependency Visualizer")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc;")
        header_layout.addWidget(self.header)
        
        header_layout.addStretch()
        
        header_layout.addWidget(QLabel("Target Milestone/Weapon:"))
        self.item_selector = QComboBox()
        self.item_selector.addItems([
            "Archon Hunts",
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
        
        # Interactive Graph Canvas
        self.visualizer = GraphVisualizer(self)
        self.layout.addWidget(self.visualizer)
        
        self.setLayout(self.layout)
        self.load_graph()

    def load_graph(self) -> None:
        """Fetch and render item dependency mappings."""
        target = self.item_selector.currentText()
        if not target:
            return
            
        player = PlayerLoader().load_player()
        graph = self.engine.get_graph(target, player)
        
        self.visualizer.build_graph(graph)
