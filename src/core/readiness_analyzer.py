from __future__ import annotations
from typing import List
from src.models.player import Player

class ReadinessAnalyzer:
    """Checks readiness and unlock requirements for advanced content."""

    def check_steel_path(self, player: Player) -> list[str]:
        """Return missing requirements for Steel Path readiness."""
        missing: list[str] = []
        if player.mastery_rank < 10:
            missing.append('Mastery Rank 10+')
        if 'galvanized chamber' not in {mod.lower() for mod in player.owned_mods}:
            missing.append('Galvanized Chamber')
        if 'primary merciless' not in {arcane.lower() for arcane in player.owned_arcanes}:
            missing.append('Primary Merciless')
        return missing

    def check_new_war(self, player: Player) -> list[str]:
        """Return missing requirements for The New War story arc."""
        required_quests = ['The War Within', 'The Sacrifice']
        completed = {quest.lower() for quest in player.completed_quests}
        return [quest for quest in required_quests if quest.lower() not in completed]

    def check_archon_hunts(self, player: Player) -> list[str]:
        """Return missing requirements for Archon Hunts readiness."""
        missing: list[str] = []
        if player.mastery_rank < 12:
            missing.append('Mastery Rank 12+')
        if 'primary merciless' not in {arcane.lower() for arcane in player.owned_arcanes}:
            missing.append('Primary Merciless')
        if 'the new war' not in {quest.lower() for quest in player.completed_quests}:
            missing.append('The New War')
        return missing

    def check_arbitrations(self, player: Player) -> list[str]:
        """Return missing requirements for arbitration access."""
        missing: list[str] = []
        if not player.arbitrations_unlocked:
            missing.append('Arbitrations unlocked')
        if player.mastery_rank < 10:
            missing.append('Mastery Rank 10+')
        if 'galvanized chamber' not in {m.lower() for m in player.owned_mods}:
            missing.append('Galvanized Chamber (recommended)')
        return missing

    def check_netracells(self, player: Player) -> list[str]:
        """Return missing requirements for Necramech and Netracells."""
        missing: list[str] = []
        if 'the new war' not in {q.lower() for q in player.completed_quests}:
            missing.append('The New War')
        if player.mastery_rank < 8:
            missing.append('Mastery Rank 8+')
        return missing

    def check_deep_archimedea(self, player: Player) -> list[str]:
        """Return missing requirements for Deep Archimedea content."""
        missing: list[str] = []
        if player.mastery_rank < 14:
            missing.append('Mastery Rank 14+')
        if 'the old blood' not in {q.lower() for q in player.completed_quests}:
            missing.append('Relevant story quests')
        return missing

    def check_eidolons(self, player: Player) -> list[str]:
        """Return missing requirements for Eidolon hunting readiness."""
        missing: list[str] = []
        if player.mastery_rank < 16:
            missing.append('Mastery Rank 16+')
        if 'primary merciless' not in {a.lower() for a in player.owned_arcanes}:
            missing.append('Primary Merciless (useful)')
        return missing

    def check_profit_taker(self, player: Player) -> list[str]:
        """Return missing requirements for Profit-Taker readiness."""
        missing: list[str] = []
        if player.mastery_rank < 12:
            missing.append('Mastery Rank 12+')
        owned = {w.lower() for w in player.owned_weapons}
        if not any(x in owned for x in ('kuva bramma', 'kuva nukor')):
            missing.append('High-damage projectile weapon (e.g., Kuva Bramma)')
        return missing
