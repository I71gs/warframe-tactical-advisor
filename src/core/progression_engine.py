from __future__ import annotations
from src.core.quest_graph import QuestGraph
from src.models.player import Player

graph = QuestGraph()

class ProgressionEngine:
    """Provides progression stage detection and multi-dimensional completion metrics."""

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

    def get_story_score(self, player: Player) -> float:
        """Return story quest completion score (0-100)."""
        total = len(graph.dependencies)
        completed = len([q for q in player.completed_quests if q in graph.dependencies])
        return round(completed / total * 100, 1)

    def get_mod_score(self, player: Player) -> float:
        """Return mod completion score (0-100)."""
        important_mods = ['galvanized chamber', 'galvanized aptitude', 'serration', 'split chamber']
        owned = {mod.lower() for mod in player.owned_mods}
        count = sum(1 for mod in important_mods if mod in owned)
        return round(count / len(important_mods) * 100, 1)

    def get_arcane_score(self, player: Player) -> float:
        """Return arcane preparedness score (0-100)."""
        important_arcanes = ['primary merciless']
        owned = {arcane.lower() for arcane in player.owned_arcanes}
        count = sum(1 for arcane in important_arcanes if arcane in owned)
        return round(count / len(important_arcanes) * 100, 1)

    def get_weapon_score(self, player: Player) -> float:
        """Return weapon preparedness score (0-100)."""
        important_weapons = ['Phenmor', 'Laetum', 'Felarx', 'Torid', 'Nataruk', 'Burston Incarnon', 'Latron Incarnon', 'Kuva Bramma', 'Kuva Nukor']
        owned = {weapon.lower() for weapon in player.owned_weapons}
        count = sum(1 for weapon in important_weapons if weapon.lower() in owned)
        return round(count / len(important_weapons) * 100, 1)

    def get_mastery_score(self, player: Player) -> float:
        """Return mastery rank score (0-100)."""
        return round(min(player.mastery_rank / 30 * 100, 100.0), 1)

    def get_unlock_score(self, player: Player) -> float:
        """Return unlocks score (0-100) based on Steel Path, Arbitrations, and Helminth."""
        count = 0
        if player.steel_path_unlocked:
            count += 1
        if player.arbitrations_unlocked:
            count += 1
        if player.helminth_unlocked:
            count += 1
        return round(count / 3 * 100, 1)

    def get_build_score(self, player: Player) -> float:
        """Return build optimization score (0-100)."""
        from src.core.build_simulator import BuildSimulator
        sim = BuildSimulator()
        weapons_to_score = ['phenmor', 'torid', 'felarx', 'laetum', 'kuva bramma']
        scores = []
        for w in weapons_to_score:
            res = sim.simulate_build(player, w)
            if res:
                scores.append(res["current_score"])
        return round(sum(scores) / len(scores), 1) if scores else 0.0

    def get_readiness_score(self, player: Player) -> float:
        """Return weighted aggregate readiness score."""
        story = self.get_story_score(player)
        mods = self.get_mod_score(player)
        arcanes = self.get_arcane_score(player)
        weapons = self.get_weapon_score(player)
        mastery = self.get_mastery_score(player)
        unlocks = self.get_unlock_score(player)
        build = self.get_build_score(player)
        
        score = (
            story * 0.25 +
            mods * 0.15 +
            arcanes * 0.15 +
            weapons * 0.15 +
            mastery * 0.10 +
            unlocks * 0.10 +
            build * 0.10
        )
        return round(score, 1)

    # Legacy compatibility aliases
    def get_story_completion_percentage(self, player: Player) -> float:
        return self.get_story_score(player)

    def get_mod_completion_percentage(self, player: Player) -> float:
        return self.get_mod_score(player)

    def get_arcane_completion_percentage(self, player: Player) -> float:
        return self.get_arcane_score(player)

    def get_weapon_completion_percentage(self, player: Player) -> float:
        return self.get_weapon_score(player)

    def record_progress_snapshot(self, player: Player) -> None:
        """Record player's current scores to the progression history cache."""
        from src.core.cache_manager import CacheManager
        from datetime import date
        import time
        cm = CacheManager()
        history = cm.load_cache("history")
        history_data = history.get("data", {})
        
        today_str = str(date.today())
        snapshots = history_data.get("snapshots", [])
        
        # Don't duplicate snapshots for the same day
        if any(s.get("date") == today_str for s in snapshots):
            return
            
        story = self.get_story_score(player)
        mods = self.get_mod_score(player)
        arcanes = self.get_arcane_score(player)
        weapons = self.get_weapon_score(player)
        mastery = self.get_mastery_score(player)
        unlocks = self.get_unlock_score(player)
        builds = self.get_build_score(player)
        readiness = self.get_readiness_score(player)
        
        snapshots.append({
            "timestamp": time.time(),
            "date": today_str,
            "readiness": readiness,
            "story": story,
            "mods": mods,
            "arcanes": arcanes,
            "weapons": weapons,
            "mastery": mastery,
            "unlocks": unlocks,
            "builds": builds
        })
        history_data["snapshots"] = snapshots
        cm.save_cache("history", history_data)
