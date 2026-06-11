from typing import Any
from src.core.player_loader import PlayerLoader
from src.core.farming_database import FARMING_DATA

class BuildAdvisor:
    """Class BuildAdvisor documentation."""

    def recommend_for_weapon(self, weapon_name: Any) -> Any:
        """Method recommend_for_weapon."""
        weapon_name = weapon_name.lower()
        build_data = {'phenmor': ['Galvanized Chamber', 'Galvanized Aptitude', 'Primary Merciless'], 'torid': ['Galvanized Chamber', 'Primary Merciless'], 'felarx': ['Primary Merciless', 'Galvanized Chamber'], 'laetum': ['Secondary Merciless'], 'nataruk': ['Galvanized Chamber'], 'burston incarnon': ['Galvanized Chamber', 'Primary Merciless'], 'latron incarnon': ['Galvanized Chamber', 'Primary Merciless'], 'lex prime': ['Secondary Merciless'], 'kuva bramma': ['Galvanized Chamber', 'Primary Merciless']}
        player = PlayerLoader().load_player()
        owned_mods = {mod.lower() for mod in player.owned_mods}
        owned_arcanes = {arcane.lower() for arcane in player.owned_arcanes}
        recommendations = []
        if weapon_name not in build_data:
            owned = [w.lower() for w in player.owned_weapons]
            suggestions = []
            for weapon in owned:
                if weapon in build_data:
                    suggestions.append(weapon.title())
            if suggestions:
                return ['Unknown weapon.', '', 'Try one of:', *suggestions]
            return ['No build data available']
        for item in build_data[weapon_name]:
            item_lower = item.lower()
            if item_lower not in owned_mods and item_lower not in owned_arcanes:
                farm_info = FARMING_DATA.get(item_lower, {'source': 'Unknown', 'estimated_time': 'Unknown'})
                recommendations.append(f"{item}\nSource: {farm_info['source']}\nTime: {farm_info['estimated_time']}")
        if not recommendations:
            recommendations.append('Build Complete ✓')
        return recommendations