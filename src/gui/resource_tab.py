from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QSpinBox, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from src.core.resource_engine import ResourceEngine

class ResourceTab(QWidget):
    """GUI tab providing a split layout to track crafting resources and deficits against target milestones."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = ResourceEngine()
        
        # Main layout
        self.main_layout = QHBoxLayout()
        
        # Left Panel - Target Select and Gaps Table
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        header_layout = QHBoxLayout()
        self.header = QLabel("Milestone Resource Planner")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc;")
        header_layout.addWidget(self.header)
        
        header_layout.addStretch()
        
        header_layout.addWidget(QLabel("Target Goal:"))
        self.target_selector = QComboBox()
        self.target_selector.addItems(list(self.engine.get_recipes().keys()))
        self.target_selector.currentTextChanged.connect(self.load_planner)
        header_layout.addWidget(self.target_selector)
        
        left_layout.addLayout(header_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Resource", "Required", "Owned", "Missing"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0f1724;
                border: 1px solid rgba(255, 255, 255, 0.05);
                gridline-color: rgba(255, 255, 255, 0.05);
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
        left_layout.addWidget(self.table)
        
        self.main_layout.addWidget(left_widget, 2)
        
        # Right Panel - Adjust inventory amounts
        self.right_panel = QGroupBox("My Resource Inventory")
        self.right_layout = QVBoxLayout(self.right_panel)
        
        self.spinboxes = {}
        resources_list = ["Voidplumes", "Entrati Lanthorn", "Thrax Plasm", "Credits", "Endo", "Forma"]
        
        for res in resources_list:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 4, 0, 4)
            
            lbl = QLabel(res)
            lbl.setStyleSheet("font-weight: 500;")
            row_layout.addWidget(lbl)
            
            row_layout.addStretch()
            
            sb = QSpinBox()
            sb.setRange(0, 9999999)
            sb.setFixedWidth(120)
            sb.setStyleSheet("background-color: #0f1724; color: #e6eef6; padding: 4px;")
            row_layout.addWidget(sb)
            self.spinboxes[res] = sb
            
            self.right_layout.addWidget(row_widget)
            
        self.save_btn = QPushButton("Save Inventory & Update")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f1a24;
                border: 1px solid #00a3cc;
                border-radius: 4px;
                color: #00a3cc;
                font-weight: bold;
                padding: 8px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: rgba(0, 163, 204, 0.1);
            }
        """)
        self.save_btn.clicked.connect(self.save_inventory)
        self.right_layout.addWidget(self.save_btn)
        self.right_layout.addStretch()
        
        self.main_layout.addWidget(self.right_panel, 1)
        
        self.setLayout(self.main_layout)
        self.load_planner()

    def load_planner(self) -> None:
        # 1. Update spinboxes from current owned resource quantities
        owned = self.engine.load_owned_resources()
        for res, sb in self.spinboxes.items():
            sb.setValue(owned.get(res, 0))
            
        # 2. Populate Target Table comparison
        target = self.target_selector.currentText()
        if not target:
            return
            
        plan = self.engine.get_plan(target)
        self.table.setRowCount(len(plan))
        
        bold_font = QFont()
        bold_font.setBold(True)
        
        for row, item in enumerate(plan):
            res_name = item["resource"]
            req = item["required"]
            own = item["owned"]
            missing = item["missing"]
            
            # Resource Name
            self.table.setItem(row, 0, QTableWidgetItem(res_name))
            
            # Required
            self.table.setItem(row, 1, QTableWidgetItem(str(req)))
            
            # Owned
            self.table.setItem(row, 2, QTableWidgetItem(str(own)))
            
            # Missing
            missing_item = QTableWidgetItem(str(missing))
            if missing > 0:
                missing_item.setForeground(QColor("#ef4444")) # Red
                missing_item.setFont(bold_font)
            else:
                missing_item.setForeground(QColor("#22c55e")) # Green
                missing_item.setText("✓ Ready")
                
            self.table.setItem(row, 3, missing_item)

    def save_inventory(self) -> None:
        owned_update = {}
        for res, sb in self.spinboxes.items():
            owned_update[res] = sb.value()
            
        self.engine.save_owned_resources(owned_update)
        self.load_planner()
