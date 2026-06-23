from __future__ import annotations
import json
from datetime import date
from pathlib import Path
from typing import Any
from src.models.player import Player

ROOT = Path(__file__).resolve().parents[2]
WEEKLY_STATE_PATH = ROOT / 'weekly_state.json'

class WeeklyPlanner:
    """Manages player weekly target progression, checking metrics dynamically against account status."""

    def __init__(self, state_path: Path | str | None = None) -> None:
        self.state_path = Path(state_path) if state_path else WEEKLY_STATE_PATH

    def get_weekly_state(self, player: Player) -> dict[str, Any]:
        """Load or initialize weekly goals for the current calendar week."""
        year, week, _ = date.today().isocalendar()
        current_week_str = f"{year}-W{week}"

        # Try to load existing weekly state
        saved_state = {}
        if self.state_path.exists():
            try:
                with open(self.state_path, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                    if data.get("week") == current_week_str:
                        saved_state = data
            except Exception:
                pass

        # If week changed or state missing, define targets
        if not saved_state:
            saved_state = {
                "week": current_week_str,
                "goals": self._define_weekly_goals(player)
            }

        # Dynamically verify completion status of targets against player profile
        for goal in saved_state["goals"]:
            goal["completed"] = self._verify_goal_completed(player, goal["text"])

        self.save_weekly_state(saved_state)
        return saved_state

    def save_weekly_state(self, state_data: dict[str, Any]) -> None:
        """Persist state data to JSON."""
        try:
            with open(self.state_path, 'w', encoding='utf-8') as fh:
                json.dump(state_data, fh, indent=4)
        except Exception:
            pass

    def _define_weekly_goals(self, player: Player) -> list[dict[str, Any]]:
        # Define up to 4 targets for the week based on player gaps
        goals = []
        completed_quests = {q.lower() for q in player.completed_quests}
        owned_mods = {m.lower() for m in player.owned_mods}
        owned_arcanes = {a.lower() for a in player.owned_arcanes}
        owned_weapons = {w.lower() for w in player.owned_weapons}

        if "angels of the zariman" not in completed_quests:
            goals.append({"text": "Complete Angels of Zariman quest", "completed": False})
        if "galvanized chamber" not in owned_mods:
            goals.append({"text": "Acquire Galvanized Chamber mod", "completed": False})
        if not player.steel_path_unlocked:
            goals.append({"text": "Unlock Steel Path difficulty", "completed": False})
        if "primary merciless" not in owned_arcanes:
            goals.append({"text": "Obtain Primary Merciless arcane", "completed": False})
        if "phenmor" not in owned_weapons:
            goals.append({"text": "Acquire Phenmor meta rifle", "completed": False})

        # Base fallbacks
        if len(goals) < 3:
            goals.append({"text": "Acquire Laetum meta pistol", "completed": False})
        if len(goals) < 3:
            goals.append({"text": "Clear 5 Star Chart nodes", "completed": False})
            
        return goals[:4]

    def _verify_goal_completed(self, player: Player, goal_text: str) -> bool:
        """Evaluate if the player profile has satisfied the target milestone."""
        text = goal_text.lower()
        completed_quests = {q.lower() for q in player.completed_quests}
        owned_mods = {m.lower() for m in player.owned_mods}
        owned_arcanes = {a.lower() for a in player.owned_arcanes}
        owned_weapons = {w.lower() for w in player.owned_weapons}

        if "angels of zariman" in text:
            return "angels of the zariman" in completed_quests
        if "galvanized chamber" in text:
            return "galvanized chamber" in owned_mods
        if "steel path" in text:
            return player.steel_path_unlocked
        if "primary merciless" in text:
            return "primary merciless" in owned_arcanes
        if "phenmor" in text:
            return "phenmor" in owned_weapons
        if "laetum" in text:
            return "laetum" in owned_weapons
        if "star chart" in text:
            return player.arbitrations_unlocked
            
        return False
