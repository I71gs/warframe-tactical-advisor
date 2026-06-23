from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from src.models.player import Player

ROOT = Path(__file__).resolve().parents[2]
INCARNON_STATE_PATH = ROOT / 'incarnon_state.json'

INCARNON_TEMPLATES = {
    "Phenmor": {
        "mr_req": 14,
        "source": "Zariman (Cavalero)",
        "resources": "5 Voidplume Pinion, 5 Entrati Lanthorn",
        "evolutions": ["Evolution I: Incarnon Form", "Evolution II: Rapid Wrath", "Evolution III: Ready Retaliation", "Evolution IV: Survivor's Edge", "Evolution V: Devastating Attrition"]
    },
    "Laetum": {
        "mr_req": 14,
        "source": "Zariman (Cavalero)",
        "resources": "10 Voidplume Quill, 8 Entrati Lanthorn",
        "evolutions": ["Evolution I: Incarnon Form", "Evolution II: Reaper's Plenty", "Evolution III: Capricious Aegis", "Evolution IV: Marksman's Focus", "Evolution V: Overwhelming Attrition"]
    },
    "Felarx": {
        "mr_req": 14,
        "source": "Zariman (Cavalero)",
        "resources": "5 Voidplume Pinion, 5 Entrati Lanthorn",
        "evolutions": ["Evolution I: Incarnon Form", "Evolution II: Kinetic Baffle", "Evolution III: Dual Mode", "Evolution IV: Wracking Force", "Evolution V: Devastating Attrition"]
    },
    "Torid": {
        "mr_req": 4,
        "source": "Steel Path Circuit Rotation",
        "resources": "20 Pathos Clamps, 60 Tasoma Extract",
        "evolutions": ["Evolution I: Incarnon Form", "Evolution II: Final Fusillade", "Evolution III: Swift Deliverance", "Evolution IV: Commodore's Fortune"]
    },
    "Burston Incarnon": {
        "mr_req": 12,
        "source": "Steel Path Circuit Rotation",
        "resources": "20 Pathos Clamps, 80 Kovik",
        "evolutions": ["Evolution I: Incarnon Form", "Evolution II: Kinetic Baffle", "Evolution III: Ready Retaliation", "Evolution IV: Commodore's Fortune"]
    },
    "Latron Incarnon": {
        "mr_req": 12,
        "source": "Steel Path Circuit Rotation",
        "resources": "20 Pathos Clamps, 70 Rune Marrow",
        "evolutions": ["Evolution I: Incarnon Form", "Evolution II: Kinetic Baffle", "Evolution III: Swift Deliverance", "Evolution IV: Survivor's Edge"]
    }
}

class IncarnonEngine:
    """Manages player progression trackers for Incarnon weapon evolution targets."""

    def __init__(self, state_path: Path | str | None = None) -> None:
        self.state_path = Path(state_path) if state_path else INCARNON_STATE_PATH

    def load_incarnon_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            # Generate default blank states for each weapon template
            default_state = {}
            for name, data in INCARNON_TEMPLATES.items():
                default_state[name] = [False] * len(data["evolutions"])
            return default_state
            
        try:
            with open(self.state_path, 'r', encoding='utf-8') as fh:
                return json.load(fh)
        except Exception:
            pass
        return {}

    def save_incarnon_state(self, state: dict[str, Any]) -> None:
        try:
            with open(self.state_path, 'w', encoding='utf-8') as fh:
                json.dump(state, fh, indent=4)
        except Exception:
            pass

    def get_weapon_status(self, player: Player, weapon_name: str) -> dict[str, Any]:
        data = INCARNON_TEMPLATES.get(weapon_name)
        if not data:
            return {}

        owned_weapons = {w.lower() for w in player.owned_weapons}
        is_owned = weapon_name.lower() in owned_weapons or (weapon_name == "Burston Incarnon" and "burston" in owned_weapons) or (weapon_name == "Latron Incarnon" and "latron" in owned_weapons)
        
        # Load checkboxes progress state
        state = self.load_incarnon_state()
        evolutions_done = state.get(weapon_name, [False] * len(data["evolutions"]))
        
        # Make sure size aligns
        if len(evolutions_done) < len(data["evolutions"]):
            evolutions_done += [False] * (len(data["evolutions"]) - len(evolutions_done))

        return {
            "name": weapon_name,
            "owned": is_owned,
            "mr_requirement_met": player.mastery_rank >= data["mr_req"],
            "mr_needed": data["mr_req"],
            "source": data["source"],
            "resources": data["resources"],
            "evolutions": [{"text": text, "completed": completed} for text, completed in zip(data["evolutions"], evolutions_done)]
        }

    def get_templates(self) -> list[str]:
        return list(INCARNON_TEMPLATES.keys())
