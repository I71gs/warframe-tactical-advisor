from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine

class MilestoneEngine:
    """Classifies player objectives into concrete immediate, short-term, mid-term, and long-term milestones."""

    def get_milestones(self, player: Player) -> dict[str, dict[str, Any]]:
        completed_quests = {q.lower() for q in player.completed_quests}
        pe = ProgressionEngine()

        # Immediate: next quest
        next_quest = pe.get_next_story_quest(player)
        immediate_lbl = f"Quest: {next_quest}" if next_quest != "Story Complete" else "All Main Quests Complete"
        immediate_comp = (next_quest == "Story Complete")
        
        # Short-term: New War completion (or Arbitrations if New War is done)
        short_lbl = "Complete 'The New War'"
        short_desc = "Unlock Zariman nodes and endgame content."
        short_comp = "the new war" in completed_quests
        if short_comp:
            short_lbl = "Unlock Arbitrations"
            short_desc = "Clear all normal Star Chart nodes."
            short_comp = player.arbitrations_unlocked

        # Mid-term: Steel Path unlock (or Helminth / MR14)
        mid_lbl = "Unlock Steel Path"
        mid_desc = "Gain access to SP difficulty and Acolyte farm."
        mid_comp = player.steel_path_unlocked
        if mid_comp:
            mid_lbl = "Reach Mastery Rank 14"
            mid_desc = "Required to craft top-tier Zariman Incarnon weapons."
            mid_comp = player.mastery_rank >= 14

        # Long-term: Endgame weapon and builds optimization
        long_lbl = "Endgame Build Optimization"
        long_desc = "Acquire meta weapons and raise simulated builds to 95%."
        long_comp = (
            player.steel_path_unlocked 
            and player.mastery_rank >= 14 
            and "phenmor" in {w.lower() for w in player.owned_weapons}
            and pe.get_build_score(player) >= 95.0
        )

        return {
            "immediate": {
                "label": immediate_lbl,
                "description": "Your next primary story quest node." if not immediate_comp else "Cinematic story complete.",
                "completed": immediate_comp
            },
            "short_term": {
                "label": short_lbl,
                "description": short_desc,
                "completed": short_comp
            },
            "mid_term": {
                "label": mid_lbl,
                "description": mid_desc,
                "completed": mid_comp
            },
            "long_term": {
                "label": long_lbl,
                "description": long_desc,
                "completed": long_comp
            }
        }
