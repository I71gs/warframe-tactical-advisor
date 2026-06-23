from __future__ import annotations
from typing import Any
from src.core.player_loader import PlayerLoader
from src.core.farming_database import FARMING_DATA

class BuildAdvisor:
    """Provides build recommendations and upgrades priority analysis for weapons."""

    def recommend_for_weapon(self, weapon_name: str) -> list[str]:
        weapon_name = weapon_name.strip().lower()
        build_data = {
            'phenmor': ['Galvanized Chamber', 'Galvanized Aptitude', 'Primary Merciless'],
            'torid': ['Galvanized Chamber', 'Primary Merciless'],
            'felarx': ['Primary Merciless', 'Galvanized Chamber'],
            'laetum': ['Secondary Merciless'],
            'nataruk': ['Galvanized Chamber'],
            'burston incarnon': ['Galvanized Chamber', 'Primary Merciless'],
            'latron incarnon': ['Galvanized Chamber', 'Primary Merciless'],
            'lex prime': ['Secondary Merciless'],
            'kuva bramma': ['Galvanized Chamber', 'Primary Merciless']
        }
        
        player = PlayerLoader().load_player()
        owned_mods = {mod.lower() for mod in player.owned_mods}
        owned_arcanes = {arcane.lower() for arcane in player.owned_arcanes}
        
        if weapon_name not in build_data:
            owned = [w.lower() for w in player.owned_weapons]
            suggestions = []
            for weapon in owned:
                if weapon in build_data:
                    suggestions.append(weapon.title())
            if suggestions:
                return ['Unknown weapon.', '', 'Try one of your owned weapons:', *suggestions]
            return ['No build data available for this weapon. Try Phenmor, Torid, or Laetum.']

        results = []
        results.append(f"=== Build Analysis for {weapon_name.title()} ===")
        results.append("")
        
        priority_map = {
            'galvanized chamber': 'CRITICAL (Farming Source: Arbitrations)',
            'galvanized aptitude': 'HIGH (Farming Source: Arbitrations)',
            'primary merciless': 'HIGH (Farming Source: Steel Path)',
            'secondary merciless': 'HIGH (Farming Source: Steel Path)'
        }

        from src.core.dependency_engine import DependencyEngine
        dep_engine = DependencyEngine()

        missing_list = []
        owned_list = []
        
        for item in build_data[weapon_name]:
            item_lower = item.lower()
            is_owned = (item_lower in owned_mods) or (item_lower in owned_arcanes)
            if is_owned:
                owned_list.append(f"  ✓ {item}")
            else:
                priority = priority_map.get(item_lower, "MEDIUM")
                unmet = dep_engine.get_unmet_dependencies(item, player)
                unmet_str = f" [Locked: Needs {', '.join(unmet)}]" if unmet else " [Ready to farm!]"
                missing_list.append(f"  • {item} - Priority: {priority}{unmet_str}")
                
        if owned_list:
            results.append("Owned Build Components:")
            results.extend(owned_list)
            results.append("")
            
        if missing_list:
            results.append("Upgrade / Farming Priorities:")
            results.extend(missing_list)
        else:
            results.append("Build Status: Complete ✓")
            
        return results