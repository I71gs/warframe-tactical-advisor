from __future__ import annotations
from src.core.quest_graph import QuestGraph
from src.models.player import Player

graph = QuestGraph()

class ProgressionEngine:
    """Provides progression stage detection and completion metrics."""

    def determine_stage(self, player: Player) -> str:
        """Determine the player's current progression stage."""
        completed = set(player.completed_quests)
        if 'The Second Dream' not in completed:
            return 'early_game'
        if 'The New War' not in completed:
            return 'mid_game'
        if not player.steel_path_unlocked:
            return 'late_game'
        return 'end_game'

    def get_primary_goal(self, player: Player) -> str:
        """Return the main progression goal for the current stage."""
        stage = self.determine_stage(player)
        goals = {
            'early_game': 'Complete Main Story Quests',
            'mid_game': 'Reach The New War',
            'late_game': 'Unlock Steel Path',
            'end_game': 'Optimize Builds',
        }
        return goals[stage]

    def get_next_story_quest(self, player: Player) -> str:
        """Return the next unlocked story quest to complete."""
        completed = set(player.completed_quests)
        for quest in graph.dependencies:
            if quest not in completed and graph.is_unlocked(quest, completed):
                return quest
        return 'Story Complete'

    def get_story_completion_percentage(self, player: Player) -> float:
        """Return story quest completion progress as a percentage."""
        total = len(graph.dependencies)
        completed = len([q for q in player.completed_quests if q in graph.dependencies])
        return round(completed / total * 100, 1)

    def get_mod_completion_percentage(self, player: Player) -> float:
        """Return progression completion score based on key mods owned."""
        important_mods = ['galvanized chamber', 'galvanized aptitude', 'serration', 'split chamber']
        owned = {mod.lower() for mod in player.owned_mods}
        count = sum(1 for mod in important_mods if mod in owned)
        return round(count / len(important_mods) * 100, 1)

    def get_arcane_completion_percentage(self, player: Player) -> float:
        """Return arcane preparedness as a percentage."""
        important_arcanes = ['primary merciless']
        owned = {arcane.lower() for arcane in player.owned_arcanes}
        count = sum(1 for arcane in important_arcanes if arcane in owned)
        return round(count / len(important_arcanes) * 100, 1)

    def get_weapon_completion_percentage(self, player: Player) -> float:
        """Return weapon preparedness as a percentage."""
        important_weapons = ['Phenmor', 'Laetum', 'Felarx', 'Torid', 'Nataruk', 'Burston Incarnon', 'Latron Incarnon', 'Kuva Bramma', 'Kuva Nukor']
        owned = {weapon.lower() for weapon in player.owned_weapons}
        count = sum(1 for weapon in important_weapons if weapon.lower() in owned)
        return round(count / len(important_weapons) * 100, 1)

    def get_readiness_score(self, player: Player) -> float:
        """Return an aggregate readiness score from multiple preparedness metrics."""
        story = self.get_story_completion_percentage(player)
        mods = self.get_mod_completion_percentage(player)
        arcanes = self.get_arcane_completion_percentage(player)
        weapons = self.get_weapon_completion_percentage(player)
        return round(story * 0.4 + mods * 0.2 + arcanes * 0.2 + weapons * 0.2, 1)
