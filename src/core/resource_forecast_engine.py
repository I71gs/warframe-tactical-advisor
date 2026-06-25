from __future__ import annotations
from typing import Any
from src.core.resource_engine import ResourceEngine

class ResourceForecastEngine:
    """Estimates cumulative resource deficits and projects required farming times."""
    
    def __init__(self, resource_engine: ResourceEngine | None = None) -> None:
        self.re = resource_engine or ResourceEngine()

    def get_hourly_rates(self) -> dict[str, float]:
        return {
            "Endo": 15000.0,
            "Credits": 2500000.0,
            "Kuva": 30000.0
        }

    def get_optimal_nodes(self) -> dict[str, str]:
        return {
            "Endo": "Vodyanoi (Sedna, Arena)",
            "Credits": "The Index (Neptune, High Risk)",
            "Kuva": "Taveuni (Kuva Fortress, Steel Path Survival)",
            "Voidplumes": "Zariman Bounties",
            "Entrati Lanthorn": "Zariman missions (Smeeta Kavat/Spare Parts)",
            "Thrax Plasm": "Zariman Mobile Defense/Survival",
            "Forma": "Void Relic Fissures"
        }

    def calculate_forecast(self, target_goals: dict[str, int] | str) -> dict[str, Any]:
        """
        Calculates deficits, hourly rates, project farming hours, and optimal farm nodes.
        target_goals can be a dictionary of resource requirements OR a recipe name from ResourceEngine.
        """
        if isinstance(target_goals, str):
            recipes = self.re.get_recipes()
            goals = recipes.get(target_goals, {})
        else:
            goals = target_goals or {}

        owned = self.re.load_owned_resources()
        rates = self.get_hourly_rates()
        nodes = self.get_optimal_nodes()

        deficits = {}
        total_farming_hours = 0.0
        details = []

        for res, goal_qty in goals.items():
            current_qty = owned.get(res, 0)
            deficit = max(0, goal_qty - current_qty)
            rate = rates.get(res, 5000.0)  # Fallback: 5000/hr
            hours = deficit / rate if deficit > 0 else 0.0
            
            node = nodes.get(res, "General Missions / Bounties")
            
            deficits[res] = deficit
            total_farming_hours += hours
            
            details.append({
                "resource": res,
                "goal": goal_qty,
                "owned": current_qty,
                "deficit": deficit,
                "hourly_rate": rate,
                "estimated_hours": round(hours, 2),
                "optimal_node": node
            })

        return {
            "target": target_goals if isinstance(target_goals, str) else "Custom Goal",
            "total_hours": round(total_farming_hours, 2),
            "details": details
        }
