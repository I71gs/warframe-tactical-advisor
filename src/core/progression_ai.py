from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.personalized_progression_engine import PersonalizedProgressionEngine
from src.core.next_action_engine import NextActionEngine

class ProgressionAI:
    """The central brain orchestrating next actions, personalized targets, and ETAs for player logs."""

    def __init__(self) -> None:
        self.ppe = PersonalizedProgressionEngine()
        self.nae = NextActionEngine()

    def get_session_plan(self, player: Player) -> dict[str, Any]:
        """Calculates a high-priority progression directive based on composite account metrics."""
        personal_focus = self.ppe.analyze_profile(player)
        action = self.nae.determine_next_action(player)
        
        # Combine focus and next action
        today_focus = personal_focus.get("focus", "Farm Arbitrations")
        
        # Clean prefix and summarize focus for compact session display
        if today_focus.startswith("Complete Quest: "):
            today = today_focus.replace("Complete Quest: ", "Complete ")
        elif today_focus.startswith("Reach Mastery Rank "):
            today = today_focus
        else:
            today = today_focus

        why = personal_focus.get("why", "Highest power gain boost for the active account.")
        gain = personal_focus.get("power_gain", "+10%")
        
        # Convert ETA (e.g. "5 hours") to a session-friendly format ("5.0h" or "1.5h")
        eta_str = personal_focus.get("eta", "1.5 hours")
        try:
            val = float(eta_str.split()[0])
            eta = f"{val}h"
        except (IndexError, ValueError):
            eta = "1.5h"
            
        return {
            "today": today,
            "why": why,
            "gain": gain,
            "eta": eta
        }
export_progression_ai = ProgressionAI()
