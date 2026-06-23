from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtGui import QColor
from src.core.player_loader import PlayerLoader
from src.core.weapon_tier_engine import WeaponTierEngine

class WeaponTiersTab(QWidget):
    """GUI tab showing meta weapons categorized into S/A/B/C tiers, with strengths and weaknesses."""

    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Meta Weapon Tiers'))
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)
        
        self.tier_colors = {
            "S": QColor("#ef4444"),  # Red
            "A": QColor("#22c55e"),  # Green
            "B": QColor("#ffb76b"),  # Orange
            "C": QColor("#9fb6c8")   # Slate
        }
        
        self.load_tiers()

    def load_tiers(self) -> None:
        self.list_widget.clear()
        player = PlayerLoader().load_player()
        engine = WeaponTierEngine()
        tiers = engine.get_weapon_tiers(player)
        
        for tier_name in ["S", "A", "B", "C"]:
            weapons = tiers.get(tier_name, [])
            if not weapons:
                continue
                
            header_item = QListWidgetItem(f"=== {tier_name} TIER WEAPONS ===")
            header_item.setForeground(self.tier_colors[tier_name])
            self.list_widget.addItem(header_item)
            
            for w in weapons:
                owned_symbol = "✓" if w["owned"] else "✗"
                tier_note = ""
                if w["personalized_tier"] != w["base_tier"]:
                    tier_note = f" (Personalized: {w['personalized_tier']} Tier due to missing builds)"
                
                text = (
                    f"  [{owned_symbol}] {w['name']}{tier_note}\n"
                    f"    • Strength: {w['strengths']}\n"
                    f"    • Weakness: {w['weaknesses']}"
                )
                
                item = QListWidgetItem(text)
                if w["owned"]:
                    item.setForeground(QColor("#e6eef6")) # Default bright text
                else:
                    item.setForeground(QColor("#9fb6c8")) # Gray out unowned weapons
                self.list_widget.addItem(item)
            
            self.list_widget.addItem("")
