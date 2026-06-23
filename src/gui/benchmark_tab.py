from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QProgressBar
from PySide6.QtCore import Qt
from src.core.player_loader import PlayerLoader
from src.core.benchmark_engine import BenchmarkEngine
from src.core.app_context import AppContext

class BenchmarkTab(QWidget):
    """GUI tab comparing player's metrics against target progression benchmarks."""

    def __init__(self, main_window=None) -> None:
        super().__init__()
        self.main_window = main_window
        self.context = AppContext()
        self.engine = BenchmarkEngine()
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_benchmarks())
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Header Row
        header_layout = QHBoxLayout()
        self.header = QLabel("Account Progress Benchmarks")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffb76b;")
        header_layout.addWidget(self.header)
        header_layout.addStretch()
        
        header_layout.addWidget(QLabel("Compare Against Level:"))
        self.benchmark_selector = QComboBox()
        self.benchmark_selector.addItems([
            "MR10 (Midgame Gateway)",
            "MR20 (Late Game Challenger)",
            "Legendary (Endgame Veteran)",
            "Endgame Specialist (Absolute Meta)"
        ])
        self.benchmark_selector.currentTextChanged.connect(self.load_benchmarks)
        header_layout.addWidget(self.benchmark_selector)
        
        self.layout.addLayout(header_layout)
        
        # Progress displays
        self.bars: dict[str, QProgressBar] = {}
        self.labels: dict[str, QLabel] = {}
        
        for key in ["weapons", "mods", "arcanes", "builds", "progression"]:
            row_layout = QVBoxLayout()
            row_layout.setSpacing(5)
            
            lbl_info = QHBoxLayout()
            name_lbl = QLabel(key.capitalize() + " Progress:")
            name_lbl.setStyleSheet("font-weight: bold; font-size: 12px;")
            val_lbl = QLabel("0 / 0")
            val_lbl.setAlignment(Qt.AlignRight)
            lbl_info.addWidget(name_lbl)
            lbl_info.addWidget(val_lbl)
            
            pbar = QProgressBar()
            pbar.setValue(0)
            pbar.setFixedHeight(20)
            
            row_layout.addLayout(lbl_info)
            row_layout.addWidget(pbar)
            row_layout.addSpacing(10)
            self.layout.addLayout(row_layout)
            
            self.bars[key] = pbar
            self.labels[key] = val_lbl
            
        self.layout.addStretch()
        self.setLayout(self.layout)
        self.load_benchmarks()

    def load_benchmarks(self) -> None:
        target = self.benchmark_selector.currentText()
        if not target:
            return
            
        player = PlayerLoader().load_player()
        evaluation = self.engine.evaluate_player(player)
        
        target_eval = evaluation.get(target)
        if not target_eval:
            return
            
        metrics = target_eval["metrics"]
        for key, pbar in self.bars.items():
            metric = metrics.get(key)
            if metric:
                pbar.setValue(metric["pct"])
                self.labels[key].setText(f"{metric['current']} / {metric['target']}")
