from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from src.models.player import Player
from src.utils.logger import logger

ROOT = Path(__file__).resolve().parents[2]
ROUTES_DIR = ROOT / "src" / "resources" / "routes"

class RouteEngine:
    """Loads and evaluates preset JSON routes against player progression states."""

    def __init__(self, routes_dir: Path | str | None = None) -> None:
        self.routes_dir = Path(routes_dir) if routes_dir else ROUTES_DIR
        self.routes_dir.mkdir(parents=True, exist_ok=True)

    def load_routes(self) -> list[dict[str, Any]]:
        """Loads all JSON files from routes directory."""
        routes = []
        for file in self.routes_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    route_data = json.load(f)
                    routes.append(route_data)
            except Exception as e:
                logger.error("Failed to load route file %s: %s", file.name, e)
        return routes

    def evaluate_routes(self, player: Player) -> list[dict[str, Any]]:
        """
        Evaluates loaded routes against player's progression state.
        Determines unlocked status based on mastery rank, quest completion, etc.
        """
        routes = self.load_routes()
        evaluated = []
        
        completed_quests = {q.lower() for q in player.completed_quests}
        
        for r in routes:
            reqs = r.get("requirements", {})
            unlocked = True
            reasons = []
            
            # Check Mastery Rank
            mr_req = reqs.get("mastery_rank", 0)
            if player.mastery_rank < mr_req:
                unlocked = False
                reasons.append(f"Requires MR {mr_req} (Current: {player.mastery_rank})")
                
            # Check Quests
            for q in reqs.get("completed_quests", []):
                if q.lower() not in completed_quests:
                    unlocked = False
                    reasons.append(f"Requires quest '{q}' completed")
                    
            # Check custom flags
            if reqs.get("steel_path_unlocked", False) and not player.steel_path_unlocked:
                unlocked = False
                reasons.append("Requires Steel Path unlocked")
                
            if reqs.get("arbitrations_unlocked", False) and not player.arbitrations_unlocked:
                unlocked = False
                reasons.append("Requires Arbitrations unlocked")
                
            route_copy = r.copy()
            route_copy["unlocked"] = unlocked
            route_copy["lock_reasons"] = reasons
            evaluated.append(route_copy)
            
        # Sort by unlocked desc, then efficiency score descending
        return sorted(evaluated, key=lambda x: (x["unlocked"], x.get("efficiency_score", 0.0)), reverse=True)
