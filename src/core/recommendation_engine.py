from __future__ import annotations
from src.models.player import Player
from src.models.recommendation import Recommendation
from src.core.knowledge_base import KnowledgeBase
from src.core.quest_graph import QuestGraph
from src.core.progression_engine import ProgressionEngine
from src.core.arcane_database import ARCANES
from src.core.weapon_database import WEAPONS

kb = KnowledgeBase()
graph = QuestGraph()
progression = ProgressionEngine()

class RecommendationEngine:
    """Generates prioritized recommendations for a player profile."""

    def generate_recommendations(self, player: Player) -> list[Recommendation]:
        """Produce a sorted list of recommendations for the given player."""
        recommendations: list[Recommendation] = []
        completed = set(player.completed_quests)
        owned_mods = {mod.lower() for mod in player.owned_mods}
        owned_arcanes = {arcane.lower() for arcane in player.owned_arcanes}
        owned_weapons = {weapon.lower() for weapon in player.owned_weapons}
        stage = progression.determine_stage(player)
        next_quest = progression.get_next_story_quest(player)
        if next_quest != 'Story Complete':
            recommendations.append(Recommendation(action=f'Complete {next_quest}', reason='Next story progression milestone', power_gain=100.0, account_progress=100.0, time_efficiency=90.0, category='STORY'))
        if stage == 'early_game':
            recommendations.append(Recommendation(action='Clear Star Chart', reason='Unlock major systems', power_gain=80.0, account_progress=95.0, time_efficiency=85.0, category='PROGRESSION'))
        elif stage == 'mid_game':
            recommendations.append(Recommendation(action='Prepare For The New War', reason='Major story milestone', power_gain=90.0, account_progress=95.0, time_efficiency=80.0, category='STORY'))
        elif stage == 'late_game':
            recommendations.append(Recommendation(action='Farm Arbitrations', reason='Unlock Galvanized Mods', power_gain=95.0, account_progress=90.0, time_efficiency=80.0, category='ENDGAME'))
            if not player.steel_path_unlocked:
                recommendations.append(Recommendation(action='Unlock Steel Path', reason='Access endgame content', power_gain=100.0, account_progress=100.0, time_efficiency=60.0, category='ENDGAME'))
        elif stage == 'end_game':
            recommendations.append(Recommendation(action='Optimize Endgame Builds', reason='Maximize account power', power_gain=90.0, account_progress=70.0, time_efficiency=95.0, category='ENDGAME'))
        for mod in kb.mods:
            if mod['name'].lower() not in owned_mods:
                recommendations.append(Recommendation(action=f"Acquire {mod['name']}", reason=f"Farm from {mod['source']}", power_gain=float(mod['importance']), account_progress=80.0, time_efficiency=70.0, category='MOD'))
        for arc in ARCANES:
            name = arc['name']
            if name.lower() not in owned_arcanes:
                recommendations.append(Recommendation(action=f'Acquire {name}', reason=f"Farm from {arc.get('acquisition')}", power_gain=float(arc.get('importance', 80)), account_progress=80.0, time_efficiency=75.0, category='ARCANE'))
        for w in WEAPONS:
            if w['name'].lower() not in owned_weapons:
                recommendations.append(Recommendation(action=f"Acquire {w['name']}", reason=f"{w.get('acquisition')}", power_gain=float(w.get('meta_rating', 70)), account_progress=70.0, time_efficiency=75.0, category='WEAPON'))
        unique: dict[str, Recommendation] = {}
        for rec in recommendations:
            unique[rec.action] = rec
        recommendations = list(unique.values())
        recommendations.sort(key=lambda r: r.calculate_score(), reverse=True)
        return recommendations
