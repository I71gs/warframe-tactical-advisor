from __future__ import annotations
import json
from datetime import date
from pathlib import Path
from typing import Any
from src.models.player import Player
from src.core.player_loader import PlayerLoader

ROOT = Path(__file__).resolve().parents[2]
DAILY_STATE_PATH = ROOT / 'daily_state.json'

class DailyObjectivesEngine:
    """Generates and persists 3-5 daily checklist objectives tailored to current player needs."""

    def __init__(self, state_path: Path | str | None = None) -> None:
        self.state_path = Path(state_path) if state_path else DAILY_STATE_PATH

    def get_daily_objectives(self, player: Player) -> dict[str, Any]:
        """Load objectives for today or generate new ones if date has rolled over."""
        today_str = str(date.today())
        
        # Try loading existing daily objectives
        if self.state_path.exists():
            try:
                with open(self.state_path, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                    if data.get("date") == today_str and "objectives" in data:
                        return data
            except Exception:
                pass

        # Generate new daily objectives
        objectives = self._generate_objectives(player)
        payload = {
            "date": today_str,
            "objectives": [{"text": obj, "completed": False} for obj in objectives]
        }
        self.save_daily_state(payload)
        return payload

    def save_daily_state(self, state_data: dict[str, Any]) -> None:
        """Persist state data to JSON."""
        try:
            with open(self.state_path, 'w', encoding='utf-8') as fh:
                json.dump(state_data, fh, indent=4)
        except Exception:
            pass

    def _generate_objectives(self, player: Player) -> list[str]:
        objectives = []
        completed_quests = {q.lower() for q in player.completed_quests}
        owned_mods = {m.lower() for m in player.owned_mods}
        owned_arcanes = {a.lower() for a in player.owned_arcanes}
        owned_weapons = {w.lower() for w in player.owned_weapons}

        # 1. Quest milestone objective
        from src.core.progression_engine import ProgressionEngine
        pe = ProgressionEngine()
        next_quest = pe.get_next_story_quest(player)
        if next_quest != "Story Complete":
            objectives.append(f"Progress Story: Complete {next_quest}")

        # 2. Mod milestone objective
        if not player.arbitrations_unlocked:
            objectives.append("Unlock Arbitrations: Complete all Star Chart nodes")
        elif "galvanized chamber" not in owned_mods:
            objectives.append("Farm Arbitrations for Galvanized Chamber mod")
        elif "galvanized aptitude" not in owned_mods:
            objectives.append("Farm Arbitrations for Galvanized Aptitude mod")

        # 3. Arcane milestone objective
        if not player.steel_path_unlocked and player.arbitrations_unlocked:
            objectives.append("Unlock Steel Path: Talk to Teshin at any Relay")
        elif player.steel_path_unlocked and "primary merciless" not in owned_arcanes:
            objectives.append("Farm Steel Path Acolytes for Primary Merciless")

        # 4. Weapon/Endgame target
        if "phenmor" not in owned_weapons and "angels of the zariman" in completed_quests:
            objectives.append("Run Zariman Bounties to acquire Phenmor")
        elif "laetum" not in owned_weapons and "angels of the zariman" in completed_quests:
            objectives.append("Run Zariman Bounties to acquire Laetum")
        elif player.steel_path_unlocked:
            objectives.append("Complete a Daily Steel Path Incursion")

        # Standard filler objectives if player is fully progressed
        if len(objectives) < 3:
            objectives.append("Complete 3 Syndicate Missions for Standing")
        if len(objectives) < 3:
            objectives.append("Run Void Fissures to open 3 Relics")
        if len(objectives) < 3:
            objectives.append("Perform 3 Helminth Invigorations / Feeds")

        # Cap at 5 objectives
        return objectives[:5]
