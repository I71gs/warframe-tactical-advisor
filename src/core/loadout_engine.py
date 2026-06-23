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

        # Calculate Synergy
        from src.core.synergy_engine import SynergyEngine
        se = SynergyEngine()
        syn = se.evaluate_synergy(
            "Wisp",
            best_primary["name"] if best_primary else "",
            best_secondary["name"] if best_secondary else "",
            player.owned_arcanes,
            player.owned_mods
        )

        # Calculate EHP and combat scores for v2.0
        health = 300 + player.mastery_rank * 10
        armor = 200 + (100 if player.steel_path_unlocked else 0)
        shield = 300 + (150 if player.arbitrations_unlocked else 0)
        ehp = int(shield + health * (1 + armor / 300))
        
        owned_mods = {m.lower() for m in player.owned_mods}
        dps_score = overall_score
        crit_score = 50 + (25 if "point strike" in owned_mods else 0) + (20 if "vital sense" in owned_mods else 0)
        status_score = 50 + (30 if "galvanized aptitude" in owned_mods or "galvanized shot" in owned_mods else 0)
        survivability_score = min(100, int((ehp / 1200) * 100))
        overall_rating = int((dps_score + crit_score + status_score + survivability_score) / 4)

        return {
            'primary': best_primary,
            'secondary': best_secondary,
            'melee': best_melee,
            'overall_score': overall_score,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'synergy_rating': syn["rating"],
            'synergy_score': syn["score"],
            'synergy_reasons': syn["reasons"],
            'health': health,
            'armor': armor,
            'shield': shield,
            'ehp': ehp,
            'dps_score': dps_score,
            'crit_score': crit_score,
            'status_score': status_score,
            'survivability_score': survivability_score,
            'overall_rating': overall_rating
        }