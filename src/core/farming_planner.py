from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.goal_planner import GoalPlanner

class FarmingPlanner:
    """Calculates optimized sequential farming roadmaps for player goals."""

    def __init__(self) -> None:
        # Define detailed farm details for item types
        # Priority defines sequencing order: lower priority numbers are farmed first.
        self._farm_db = {
            "galvanized chamber": {
                "source": "Arbitrations",
                "requirements": "Star Chart Complete",
                "time": "1-3 hours",
                "priority": 1
            },
            "galvanized aptitude": {
                "source": "Arbitrations",
                "requirements": "Star Chart Complete",
                "time": "1-3 hours",
                "priority": 1
            },
            "primary merciless": {
                "source": "Steel Path Acolytes",
                "requirements": "Steel Path Unlocked",
                "time": "2-5 hours",
                "priority": 2
            },
            "secondary merciless": {
                "source": "Steel Path Acolytes",
                "requirements": "Steel Path Unlocked",
                "time": "2-5 hours",
                "priority": 2
            },
            "phenmor": {
                "source": "Zariman (Cavalero)",
                "requirements": "Quest: Angels of the Zariman, MR14",
                "time": "4-6 hours",
                "priority": 3
            },
            "laetum": {
                "source": "Zariman (Cavalero)",
                "requirements": "Quest: Angels of the Zariman, MR14",
                "time": "3-5 hours",
                "priority": 3
            },
            "felarx": {
                "source": "Zariman (Cavalero)",
                "requirements": "Quest: Angels of the Zariman, MR14",
                "time": "4-6 hours",
                "priority": 3
            },
            "latron incarnon": {
                "source": "Steel Path Circuit",
                "requirements": "Quest: Angels of the Zariman, Steel Path",
                "time": "4-8 hours",
                "priority": 4
            },
            "burston incarnon": {
                "source": "Steel Path Circuit",
                "requirements": "Quest: Angels of the Zariman, Steel Path",
                "time": "4-8 hours",
                "priority": 4
            },
            "kuva bramma": {
                "source": "Kuva Liches",
                "requirements": "Quest: The War Within, MR15",
                "time": "3-6 hours",
                "priority": 2
            },
            "kuva nukor": {
                "source": "Kuva Liches",
                "requirements": "Quest: The War Within, MR13",
                "time": "3-6 hours",
                "priority": 2
            },
            "arcane energize": {
                "source": "Eidolons / Events",
                "requirements": "MR16",
                "time": "20+ hours",
                "priority": 5
            }
        }

    def generate_farming_path(self, player: Player, goal: str) -> list[dict[str, Any]]:
        """Identify missing items for the given goal and order them sequentially."""
        gp = GoalPlanner()
        goal_steps = gp.get_goal_plan(player, goal)
        missing_items = []

        for step in goal_steps:
            # We only plan farming path for tasks that are "Acquire [Item]" and not yet completed
            if not step["completed"] and step["step"].startswith("Acquire "):
                item_name = step["step"].replace("Acquire ", "").strip()
                missing_items.append(item_name)

        farming_steps = []
        for item in missing_items:
            item_lower = item.lower()
            if item_lower in self._farm_db:
                info = self._farm_db[item_lower]
                farming_steps.append({
                    "item": item,
                    "source": info["source"],
                    "requirements": info["requirements"],
                    "time": info["time"],
                    "priority": info["priority"]
                })
            else:
                # Default generic farming info
                farming_steps.append({
                    "item": item,
                    "source": "Market / Trading / Clan Dojo",
                    "requirements": "Mastery Rank & Credits",
                    "time": "Unknown",
                    "priority": 10
                })

        # Sort based on sequence/priority
        farming_steps.sort(key=lambda x: x["priority"])
        return farming_steps