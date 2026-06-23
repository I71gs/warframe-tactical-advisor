from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QGroupBox, QListWidget, QProgressBar
from PySide6.QtCore import Qt
from src.core.team_synergy_engine import TeamSynergyEngine

class TeamTab(QWidget):
    """GUI tab to evaluate and visualize synergies of full loadouts (Warframe, Primary, Secondary, Melee)."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = TeamSynergyEngine()
        
        # Main layout
        self.main_layout = QHBoxLayout()
        
        # Left Panel - Input Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.header = QLabel("Loadout Synergy Analyzer")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #caa3ff; margin-bottom: 10px;")
        left_layout.addWidget(self.header)
        
        # Inputs Group
        inputs_group = QGroupBox("Select Loadout Components")
        inputs_layout = QVBoxLayout(inputs_group)
        
        inputs_layout.addWidget(QLabel("Warframe:"))
        self.wf_selector = QComboBox()
        self.wf_selector.addItems(["Wisp", "Saryn", "Mesa", "Volt", "Mirage", "Excalibur", "Rhino"])
        self.wf_selector.currentTextChanged.connect(self.calculate_synergy)
        inputs_layout.addWidget(self.wf_selector)
        
        inputs_layout.addWidget(QLabel("Primary Weapon:"))
        self.prim_selector = QComboBox()
        self.prim_selector.addItems(["Phenmor", "Torid", "Felarx", "Kuva Bramma", "Nataruk", "Burston Incarnon"])
        self.prim_selector.currentTextChanged.connect(self.calculate_synergy)
        inputs_layout.addWidget(self.prim_selector)
        
        inputs_layout.addWidget(QLabel("Secondary Weapon:"))
        self.sec_selector = QComboBox()
        self.sec_selector.addItems(["Laetum", "Kuva Nukor", "Lex Prime"])
        self.sec_selector.currentTextChanged.connect(self.calculate_synergy)
        inputs_layout.addWidget(self.sec_selector)
        
        inputs_layout.addWidget(QLabel("Melee Weapon:"))
        self.melee_selector = QComboBox()
        self.melee_selector.addItems(["Praedos", "Glaive Prime", "Skana", "Orthos Prime"])
        self.melee_selector.currentTextChanged.connect(self.calculate_synergy)
        inputs_layout.addWidget(self.melee_selector)
        
        left_layout.addWidget(inputs_group)
        left_layout.addStretch()
        
        self.main_layout.addWidget(left_widget, 1)
        
        # Right Panel - Score & Analysis Details
        right_widget = QGroupBox("Synergy Assessment")
        right_layout = QVBoxLayout(right_widget)
        
        # Large Score Label
        self.score_header = QLabel("Synergy Score: -")
        self.score_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #00a3cc;")
        right_layout.addWidget(self.score_header)
        
        self.score_bar = QProgressBar()
        right_layout.addWidget(self.score_bar)
        
        # Strengths & Weaknesses lists
        right_layout.addWidget(QLabel("<b>Key Strengths:</b>"))
        self.strengths_list = QListWidget()
        self.strengths_list.setStyleSheet("border: none; background: transparent; max-height: 100px;")
        right_layout.addWidget(self.strengths_list)
        
        right_layout.addWidget(QLabel("<b>Potential Weaknesses:</b>"))
        self.weaknesses_list = QListWidget()
        self.weaknesses_list.setStyleSheet("border: none; background: transparent; max-height: 100px;")
        right_layout.addWidget(self.weaknesses_list)
        
        # Rationale Panel
        self.rationale_box = QGroupBox("Synergy Rationale")
        self.rationale_layout = QVBoxLayout(self.rationale_box)
        self.primary_rationale = QLabel("-")
        self.primary_rationale.setWordWrap(True)
        self.secondary_rationale = QLabel("-")
        self.secondary_rationale.setWordWrap(True)
        self.rationale_layout.addWidget(self.primary_rationale)
        self.rationale_layout.addWidget(self.secondary_rationale)
        right_layout.addWidget(self.rationale_box)
        
        self.main_layout.addWidget(right_widget, 2)
        
        self.setLayout(self.main_layout)
        self.calculate_synergy()

    def calculate_synergy(self) -> None:
        wf = self.wf_selector.currentText()
        prim = self.prim_selector.currentText()
        sec = self.sec_selector.currentText()
        mel = self.melee_selector.currentText()
        
        if not all([wf, prim, sec, mel]):
            return
            
        res = self.engine.evaluate_composition(wf, prim, sec, mel)
        
        # Update Score UI
        self.score_header.setText(f"Synergy Score: {res['score']}% ({res['rating']})")
        self.score_bar.setValue(int(res['score']))
        
        # Update Lists
        self.strengths_list.clear()
        for s in res["strengths"]:
            self.strengths_list.addItem(f"• {s}")
            
        self.weaknesses_list.clear()
        for w in res["weaknesses"]:
            self.weaknesses_list.addItem(f"• {w}")
            
        # Update Rationales
        self.primary_rationale.setText(f"<b>Primary ({prim}):</b> {res['primary_rationale']}")
        self.secondary_rationale.setText(f"<b>Secondary ({sec}):</b> {res['secondary_rationale']}")
