from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RESOURCE_STATE_PATH = ROOT / 'resource_state.json'

RECIPES = {
    "Phenmor": {
        "Voidplumes": 15,
        "Entrati Lanthorn": 5,
        "Thrax Plasm": 100,
        "Credits": 30000,
        "Endo": 5000,
        "Forma": 3
    },
    "Laetum": {
        "Voidplumes": 10,
        "Entrati Lanthorn": 8,
        "Thrax Plasm": 80,
        "Credits": 30000,
        "Endo": 5000,
        "Forma": 3
    },
    "Unlock Steel Path": {
        "Credits": 50000,
        "Endo": 10000,
        "Forma": 2
    },
    "Arbitrations Unlocked": {
        "Credits": 25000,
        "Endo": 3000
    },
    "Become Archon Ready": {
        "Forma": 5,
        "Credits": 100000,
        "Endo": 15000
    }
}

class ResourceEngine:
    """Calculates resource requirements and deficits based on player target items."""

    def __init__(self, state_path: Path | str | None = None) -> None:
        if state_path:
            self.state_path = Path(state_path)
        else:
            from src.core.settings_manager import SettingsManager
            profile = SettingsManager().get('current_profile', 'default')
            from src.core.save_manager import SaveManager
            sm = SaveManager()
            # Ensure the directory exists
            sm.profiles_dir.mkdir(parents=True, exist_ok=True)
            (sm.profiles_dir / profile).mkdir(parents=True, exist_ok=True)
            self.state_path = sm.profiles_dir / profile / 'resource_state.json'

    def load_owned_resources(self) -> dict[str, int]:
        """Loads player's currently owned resource counts."""
        default_resources = {
            "Voidplumes": 0,
            "Entrati Lanthorn": 0,
            "Thrax Plasm": 0,
            "Credits": 0,
            "Endo": 0,
            "Forma": 0
        }
        if not self.state_path.exists():
            return default_resources
            
        try:
            with open(self.state_path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                if isinstance(data, dict):
                    # Merge defaults with saved keys
                    for k, v in data.items():
                        default_resources[k] = int(v)
        except Exception:
            pass
        return default_resources

    def save_owned_resources(self, owned: dict[str, int]) -> None:
        """Saves player's currently owned resource counts."""
        try:
            with open(self.state_path, 'w', encoding='utf-8') as fh:
                json.dump(owned, fh, indent=4)
        except Exception:
            pass

    def get_recipes(self) -> dict[str, dict[str, int]]:
        """Return raw recipe configurations."""
        return RECIPES

    def get_plan(self, target: str) -> list[dict[str, Any]]:
        """Calculates owned, required, and missing values for a given milestone target."""
        recipe = RECIPES.get(target, {})
        owned = self.load_owned_resources()
        
        plan = []
        for resource, req_qty in recipe.items():
            owned_qty = owned.get(resource, 0)
            missing = max(0, req_qty - owned_qty)
            plan.append({
                "resource": resource,
                "required": req_qty,
                "owned": owned_qty,
                "missing": missing
            })
        return plan
