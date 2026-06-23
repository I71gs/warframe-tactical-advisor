from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QComboBox, QHBoxLayout
from PySide6.QtGui import QColor
from src.core.player_loader import PlayerLoader
from src.core.build_simulator import BuildSimulator

class BuildSimulatorTab(QWidget):
    """GUI tab allowing players to search a weapon and simulate build configurations."""

    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Build Simulator'))
        
        self.weapon_selector = QComboBox()
        self.simulator = BuildSimulator()
        self.weapon_selector.addItems(sorted(list(self.simulator.build_templates.keys())))
        
        self.layout.addWidget(self.weapon_selector)
        
        # Details Panel
        self.details_label = QLabel()
        self.details_label.setStyleSheet("padding: 8px; background: rgba(0, 163, 204, 0.05); border: 1px solid rgba(255,255,255,0.06); border-radius: 4px;")
        self.layout.addWidget(self.details_label)
        
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)
        
        self.weapon_selector.currentTextChanged.connect(self.run_simulation)
        self.run_simulation()

    def run_simulation(self) -> None:
        self.list_widget.clear()
        weapon = self.weapon_selector.currentText()
        if not weapon:
            return
            
        player = PlayerLoader().load_player()
        result = self.simulator.simulate_build(player, weapon)
        
        if not result:
            self.details_label.setText("No build data available for this weapon.")
            return
            
        details_text = (
            f"<b>Weapon:</b> {result['weapon']}<br>"
            f"<b>Current Build Score:</b> {result['current_score']} / 100<br>"
            f"<b>Potential Build Score:</b> {result['potential_score']} / 100<br>"
            f"<b>Estimated Damage Gain:</b> <span style='color: #22c55e;'>{result['gain']}</span>"
        )
        self.details_label.setText(details_text)
        
        self.list_widget.addItem("=== Component Check ===")
        for comp in result["components"]:
            if comp["owned"]:
                item = QListWidgetItem(f"  ✔ {comp['name']}")
                item.setForeground(QColor("#22c55e")) # Green
            else:
                item = QListWidgetItem(f"  ✖ {comp['name']}")
                item.setForeground(QColor("#ef4444")) # Red
            self.list_widget.addItem(item)
            
        if result["missing"]:
            self.list_widget.addItem("")
            self.list_widget.addItem("=== Missing Upgrades ===")
            for item_name in result["missing"]:
                missing_item = QListWidgetItem(f"  • {item_name}")
                missing_item.setForeground(QColor("#ffb76b")) # Orange
                self.list_widget.addItem(missing_item)
