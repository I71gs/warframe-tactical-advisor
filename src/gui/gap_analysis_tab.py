from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QHBoxLayout
from PySide6.QtGui import QColor
from src.core.player_loader import PlayerLoader
from src.core.gap_analyzer import GapAnalyzer

class GapAnalysisTab(QWidget):
    """GUI tab displaying player account gaps grouped by severity and type."""

    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Account Gap Analyzer'))
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)
        
        self.severity_colors = {
            "CRITICAL": QColor("#ef4444"),  # Bright Red
            "HIGH": QColor("#f97316"),      # Orange
            "MEDIUM": QColor("#eab308"),    # Yellow
            "LOW": QColor("#9fb6c8")        # Muted Slate
        }
        
        self.load_gaps()

    def load_gaps(self) -> None:
        self.list_widget.clear()
        player = PlayerLoader().load_player()
        analyzer = GapAnalyzer()
        gaps = analyzer.analyze_gaps(player)
        
        if not gaps:
            self.list_widget.addItem("No account gaps identified! You are fully optimized. ✓")
            return
            
        current_severity = None
        for gap in gaps:
            severity = gap["severity"]
            
            # Print severity header if it changes
            if severity != current_severity:
                current_severity = severity
                header_item = QListWidgetItem(f"=== {current_severity} GAPS ===")
                header_item.setForeground(self.severity_colors.get(current_severity, QColor("#ffffff")))
                self.list_widget.addItem(header_item)
                
            text = f"  [{gap['category']}] {gap['name']} - {gap['details']}"
            item = QListWidgetItem(text)
            # Give a slightly lighter text for details but still color code
            item.setForeground(self.severity_colors.get(severity, QColor("#ffffff")))
            self.list_widget.addItem(item)
