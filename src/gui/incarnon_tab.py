from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QGroupBox
from src.core.player_loader import PlayerLoader
from src.core.incarnon_engine import IncarnonEngine

from src.core.app_context import AppContext

class IncarnonTab(QWidget):
    """GUI tab tracking Incarnon weapon requirements, crafting materials, and active evolutions checkmarks."""

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        self.engine = self.context.resource_service.incarnon_engine
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda data: self.load_incarnon())
        
        self.checkboxes = []
        self.layout = QVBoxLayout()
        
        # Header Row
        header_layout = QHBoxLayout()
        self.header = QLabel("Incarnon Evolutions Planner")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc;")
        header_layout.addWidget(self.header)
        
        header_layout.addStretch()
        
        header_layout.addWidget(QLabel("Select Incarnon Weapon:"))
        self.weapon_selector = QComboBox()
        self.weapon_selector.addItems(self.engine.get_templates())
        self.weapon_selector.currentTextChanged.connect(self.load_incarnon)
        header_layout.addWidget(self.weapon_selector)
        
        self.layout.addLayout(header_layout)
        
        # Details Panel
        self.details_box = QGroupBox("Weapon Prerequisite & Crafting Status")
        self.details_layout = QVBoxLayout(self.details_box)
        
        self.owned_lbl = QLabel()
        self.mr_lbl = QLabel()
        self.source_lbl = QLabel()
        self.resources_lbl = QLabel()
        
        self.details_layout.addWidget(self.owned_lbl)
        self.details_layout.addWidget(self.mr_lbl)
        self.details_layout.addWidget(self.source_lbl)
        self.details_layout.addWidget(self.resources_lbl)
        
        self.layout.addWidget(self.details_box)
        
        # Evolutions Checklist
        self.evol_box = QGroupBox("Evolution Stages Checklist")
        self.evol_layout = QVBoxLayout(self.evol_box)
        self.layout.addWidget(self.evol_box)
        
        self.layout.addStretch()
        self.setLayout(self.layout)
        self.load_incarnon()

    def load_incarnon(self) -> None:
        # Clear evolution checkbox widgets
        self.checkboxes.clear()
        for i in reversed(range(self.evol_layout.count())):
            w = self.evol_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
                
        weapon = self.weapon_selector.currentText()
        if not weapon:
            return
            
        player = PlayerLoader().load_player()
        status = self.engine.get_weapon_status(player, weapon)
        if not status:
            return
            
        # Update details labels
        own_style = "color: #22c55e; font-weight: bold;" if status["owned"] else "color: #ef4444;"
        self.owned_lbl.setText(f"<b>Inventory Status:</b> <span style='{own_style}'>{'Owned' if status['owned'] else 'Missing (Not Owned)'}</span>")
        
        mr_style = "color: #22c55e;" if status["mr_requirement_met"] else "color: #ef4444; font-weight: bold;"
        self.mr_lbl.setText(f"<b>Mastery Requirement:</b> <span style='{mr_style}'>Rank {status['mr_needed']}+ ({'Met' if status['mr_requirement_met'] else 'Locked - Deficit'})</span>")
        
        self.source_lbl.setText(f"<b>Acquisition Blueprint Source:</b> {status['source']}")
        self.resources_lbl.setText(f"<b>Evolving/Crafting Materials:</b> {status['resources']}")
        
        # Populate Evolutions checklist
        for idx, ev in enumerate(status["evolutions"]):
            cb = QCheckBox(ev["text"])
            cb.setChecked(ev["completed"])
            cb.stateChanged.connect(lambda state, index=idx: self.on_evolution_toggled(weapon, index, state))
            self.evol_layout.addWidget(cb)
            self.checkboxes.append(cb)

    def on_evolution_toggled(self, weapon_name: str, index: int, state: int) -> None:
        current_state = self.engine.load_incarnon_state()
        if weapon_name not in current_state:
            current_state[weapon_name] = [False] * len(self.checkboxes)
            
        # Align list size
        while len(current_state[weapon_name]) < len(self.checkboxes):
            current_state[weapon_name].append(False)
            
        current_state[weapon_name][index] = (state == 2) # Qt.Checked is 2
        self.engine.save_incarnon_state(current_state)
