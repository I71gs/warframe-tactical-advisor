from typing import Any
from src.core.weapon_database import WEAPONS

class LoadoutEngine:
    """Class LoadoutEngine documentation."""

    def __init__(self) -> None:
        """Initialize the class."""
        self._weapons = {w['name'].lower(): w for w in WEAPONS}

    def recommend_loadout(self, player: Any) -> Any:
        """Method recommend_loadout."""
        owned = {w.lower() for w in player.owned_weapons}
        owned_meta = [self._weapons[w] for w in owned if w in self._weapons]

        def score_weapon(w: Any) -> Any:
            """Method score_weapon."""
            score = w.get('meta_rating', 50)
            if w.get('category') in ('Rifle', 'Bow'):
                score += 3
            if w.get('type') == 'Melee':
                score += 2
            return score
        primaries = [w for w in owned_meta if w.get('type') == 'Primary']
        secondaries = [w for w in owned_meta if w.get('type') == 'Secondary']
        melees = [w for w in owned_meta if w.get('type') == 'Melee']
        primaries.sort(key=score_weapon, reverse=True)
        secondaries.sort(key=score_weapon, reverse=True)
        melees.sort(key=score_weapon, reverse=True)
        best_primary = primaries[0] if primaries else None
        best_secondary = secondaries[0] if secondaries else None
        best_melee = melees[0] if melees else None
        total = 0
        parts = 0
        for part in (best_primary, best_secondary, best_melee):
            if part:
                total += part.get('meta_rating', 50)
                parts += 1
        overall_score = round(total / parts, 1) if parts else 0
        strengths = []
        weaknesses = []
        if best_primary:
            strengths.append(f"Primary: {best_primary['name']} ({best_primary.get('category')})")
        else:
            weaknesses.append('No strong Primary owned')
        if best_secondary:
            strengths.append(f"Secondary: {best_secondary['name']} ({best_secondary.get('category')})")
        else:
            weaknesses.append('No strong Secondary owned')
        if best_melee:
            strengths.append(f"Melee: {best_melee['name']} ({best_melee.get('category')})")
        else:
            weaknesses.append('No strong Melee owned')
        missing_high_meta = [w['name'] for w in WEAPONS if w.get('meta_rating', 0) >= 90 and w['name'].lower() not in owned]
        if missing_high_meta:
            weaknesses.append(f"Missing high-meta weapons: {', '.join(missing_high_meta)}")
        return {'primary': best_primary, 'secondary': best_secondary, 'melee': best_melee, 'overall_score': overall_score, 'strengths': strengths, 'weaknesses': weaknesses}