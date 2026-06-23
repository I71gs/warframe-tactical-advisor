from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine

class SessionOptimizer:
    """Calculates most efficient sequence of tasks and expected hourly rates based on session time limits."""

    def __init__(self) -> None:
        self.pe = ProgressionEngine()

    def optimize_session(self, player: Player, duration_minutes: int) -> dict[str, Any]:
        """Calculates optimal sequence of missions, expected rewards, and power rates."""
        stage = self.pe.determine_stage(player)
        
        # Define candidate activities with duration, rewards, and rate factors
        activities = [
            {
                "id": "story",
                "name": "Story Quest: Next Quest Node",
                "location": "Quest Codex",
                "duration": 45,
                "reward": "Nataruk Bow, Umbral Mods",
                "stages": ["early_game", "mid_game"],
                "power_gain_ph": 15.0,
                "resource_ph": "Low"
            },
            {
                "id": "star_chart",
                "name": "Star Chart: Nodes Clearance",
                "location": "Star Chart",
                "duration": 30,
                "reward": "Junction unlocks, SP access prep",
                "stages": ["early_game", "mid_game", "late_game"],
                "power_gain_ph": 8.0,
                "resource_ph": "20k Credits, 1.2k Endo"
            },
            {
                "id": "index",
                "name": "Credit Farm: The Index",
                "location": "Neptune Index",
                "duration": 15,
                "reward": "Credits (250,000)",
                "stages": ["early_game", "mid_game", "late_game", "end_game"],
                "power_gain_ph": 3.0,
                "resource_ph": "1,000,000 Credits"
            },
            {
                "id": "arbitrations",
                "name": "Arbitration: Survival/Defense",
                "location": "Active Arbitration",
                "duration": 30,
                "reward": "Vitus Essence, Galvanized Mods",
                "stages": ["late_game", "end_game"],
                "power_gain_ph": 25.0,
                "resource_ph": "12 Vitus Essence, 4k Endo"
            },
            {
                "id": "incursion",
                "name": "Steel Path Incursion",
                "location": "SP Incursion Alert",
                "duration": 15,
                "reward": "5x Steel Essence, Acolyte Arcanes",
                "stages": ["end_game"],
                "power_gain_ph": 30.0,
                "resource_ph": "20 Steel Essence, 2 Primary Merciless"
            },
            {
                "id": "zariman",
                "name": "Zariman Bounty Run",
                "location": "Zariman Chrysalith",
                "duration": 20,
                "reward": "Voidplumes, Lanthorn",
                "stages": ["late_game", "end_game"],
                "power_gain_ph": 18.0,
                "resource_ph": "6 Voidplumes, 2 Entrati Lanthorns"
            },
            {
                "id": "fissure",
                "name": "Void Fissure Capture",
                "location": "Void Fissures",
                "duration": 10,
                "reward": "Prime Blueprints, Void Traces",
                "stages": ["early_game", "mid_game", "late_game", "end_game"],
                "power_gain_ph": 5.0,
                "resource_ph": "6 Prime Parts, 80 Void Traces"
            }
        ]

        # Filter candidates matching player's current stage
        candidates = [a for a in activities if stage in a["stages"]]
        
        # Sort candidates so the highest power_gain_ph comes first
        candidates.sort(key=lambda x: x["power_gain_ph"], reverse=True)
        
        selected_sequence = []
        time_remaining = duration_minutes
        
        # Select items fitting in remaining duration
        for cand in candidates:
            while time_remaining >= cand["duration"]:
                selected_sequence.append({
                    "activity": cand["name"],
                    "location": cand["location"],
                    "duration": cand["duration"],
                    "reward": cand["reward"]
                })
                time_remaining -= cand["duration"]
                
        # If no candidates fit the remaining time, fill with the shortest matching activity (e.g. fissure)
        if not selected_sequence and candidates:
            shortest = min(candidates, key=lambda x: x["duration"])
            selected_sequence.append({
                "activity": shortest["name"],
                "location": shortest["location"],
                "duration": duration_minutes, # scale to fit
                "reward": shortest["reward"]
            })
            
        # Calculate rates
        total_power = sum(s.get("power_gain_ph", 0) for s in candidates if any(sel["activity"] == s["name"] for sel in selected_sequence))
        avg_power = round(total_power / len(selected_sequence), 1) if selected_sequence else 0.0
        
        resources_list = [s.get("resource_ph") for s in candidates if any(sel["activity"] == s["name"] for sel in selected_sequence)]
        resources_str = ", ".join(r for r in resources_list if r and r != "Low") or "Basic Credits & Endo"

        return {
            "duration": duration_minutes,
            "sequence": selected_sequence,
            "power_gain_per_hour": f"+{avg_power}%/hr estimation",
            "resource_gain_per_hour": resources_str
        }
