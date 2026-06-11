from typing import Any
from src.core.player_loader import PlayerLoader

class LoadoutAdvisor:
    """Class LoadoutAdvisor documentation."""

    def analyze_account(self) -> Any:
        """Method analyze_account."""
        player = PlayerLoader().load_player()
        owned = {weapon.lower() for weapon in player.owned_weapons}
        top_tier = ['phenmor', 'laetum', 'felarx', 'torid', 'burston incarnon', 'latron incarnon', 'kuva nukor', 'kuva bramma']
        owned_meta = []
        missing_meta = []
        for weapon in top_tier:
            if weapon in owned:
                owned_meta.append(weapon.title())
            else:
                missing_meta.append(weapon.title())
        return {'owned': owned_meta, 'missing': missing_meta}