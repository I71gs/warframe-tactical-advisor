from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from src.core.resource_engine import ResourceEngine

_DATA = Path(__file__).resolve().parents[1] / "resources" / "data"


def _load_resources() -> list[dict]:
    path = _DATA / "resources.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


RESOURCE_DATA: list[dict] = _load_resources()

# Lookup by name for fast access
_RESOURCE_BY_NAME: dict[str, dict] = {r["name"].lower(): r for r in RESOURCE_DATA}

# Dynamic targets: what a well-equipped account needs (can be overridden)
DEFAULT_TARGETS: dict[str, int] = {
    "Credits":           2_500_000,
    "Endo":              120_000,
    "Kuva":               50_000,
    "Steel Essence":         100,
    "Vitus Essence":          80,
    "Voidplumes":             50,
    "Entrati Lanthorn":       20,
    "Pathos Clamps":         100,
    "Orokin Cell":           200,
    "Neural Sensors":        200,
    "Tellurium":             100,
    "Argon Crystal":          30,
    "Cryotic":            10_000,
    "Oxium":               5_000,
    "Hexenon":             3_000,
    "Plastids":           10_000,
    "Alloy Plate":        20_000,
    "Ferrite":            20_000,
    "Control Module":        200,
    "Morphics":              100,
    "Nano Spores":        20_000,
    "Polymer Bundle":     10_000,
    "Rubedo":             10_000,
    "Circuits":           10_000,
    "Salvage":            20_000,
}

BOOSTER_RECOMMENDATION: dict[str, str] = {
    "Credits":         "Credit Booster (doubles Profit-Taker and mission rewards)",
    "Endo":            "Resource Booster (doubles Endo drops in Arbitrations/Arena)",
    "Kuva":            "Smeeta Kavat Charm (doubles Kuva pickup, stacks with boosters)",
    "Orokin Cell":     "Resource Booster + Orokin Cell Farm (boss runs or Dark Sector)",
    "Neural Sensors":  "Resource Booster (Cameria Dark Sector Survival)",
    "Tellurium":       "Resource Booster (Ophelia, Uranus — Archwing only)",
    "Argon Crystal":   "Resource Booster — but FARM IMMEDIATELY, Argon decays in 24h!",
    "Oxium":           "Resource Booster (kill Oxium Ospreys before they self-destruct)",
}


class EconomyEngine:
    """Calculates account currency requirements, deficits, farming times, and booster advice.

    Covers 25+ resources with real farming data loaded from resources.json.
    """

    # ── public API ────────────────────────────────────────────────────────────

    def get_economy_plan(self, custom_targets: dict[str, int] | None = None) -> list[dict[str, Any]]:
        """Return a deficit/farming plan for all tracked resources.

        Args:
            custom_targets: Optional dict overriding default target quantities.

        Returns:
            List of resource plan dicts with owned, missing, farm_hours, best_node.
        """
        targets = {**DEFAULT_TARGETS, **(custom_targets or {})}
        re = ResourceEngine()
        owned = re.load_owned_resources()

        plan = []
        for resource_name, target in targets.items():
            own_qty = self._resolve_owned(owned, resource_name)
            missing = max(0, target - own_qty)
            resource_info = _RESOURCE_BY_NAME.get(resource_name.lower(), {})
            rate = resource_info.get("rate_per_hr", 1)
            best_nodes = resource_info.get("best_nodes", [])
            best_node = best_nodes[0]["node"] if best_nodes else "See in-game drop tables"
            farm_hours = round(missing / rate, 2) if missing > 0 and rate > 0 else 0.0

            plan.append({
                "resource": resource_name,
                "category": resource_info.get("category", "Resource"),
                "required": target,
                "owned": own_qty,
                "missing": missing,
                "farm_hours": farm_hours,
                "best_node": best_node,
                "rate_per_hr": rate,
                "booster": resource_info.get("booster_type", "Resource Booster"),
                "notes": resource_info.get("notes", ""),
            })

        # Sort: biggest deficit first
        plan.sort(key=lambda x: x["farm_hours"], reverse=True)
        return plan

    def get_resource_farm_plan(self, goal: str) -> dict[str, Any]:
        """Return farming breakdown for a named goal (e.g. 'Wisp', 'Forma').

        Returns dict with resource list, total farm hours, and booster advice.
        """
        goal_resources = GOAL_RESOURCE_REQUIREMENTS.get(goal.lower(), {})
        if not goal_resources:
            return {
                "goal": goal,
                "found": False,
                "message": f"No resource requirements found for '{goal}'. Goals include: {', '.join(GOAL_RESOURCE_REQUIREMENTS.keys())}",
            }

        re = ResourceEngine()
        owned = re.load_owned_resources()
        items: list[dict] = []
        total_hours = 0.0

        for resource_name, required in goal_resources.items():
            own_qty = self._resolve_owned(owned, resource_name)
            missing = max(0, required - own_qty)
            resource_info = _RESOURCE_BY_NAME.get(resource_name.lower(), {})
            rate = resource_info.get("rate_per_hr", 1)
            best_nodes = resource_info.get("best_nodes", [])
            best_node = best_nodes[0]["node"] if best_nodes else "See drop tables"
            hours = round(missing / rate, 2) if missing > 0 and rate > 0 else 0.0
            total_hours += hours

            items.append({
                "resource": resource_name,
                "required": required,
                "owned": own_qty,
                "missing": missing,
                "farm_hours": hours,
                "best_node": best_node,
            })

        items.sort(key=lambda x: x["farm_hours"], reverse=True)
        boosters = self.recommend_boosters([i["resource"] for i in items if i["missing"] > 0])

        return {
            "goal": goal,
            "found": True,
            "resources": items,
            "total_farm_hours": round(total_hours, 1),
            "recommended_boosters": boosters,
        }

    def recommend_boosters(self, resource_names: list[str]) -> list[str]:
        """Return relevant booster recommendations for a list of resources."""
        boosters: list[str] = []
        seen: set[str] = set()
        for name in resource_names:
            advice = BOOSTER_RECOMMENDATION.get(name)
            if advice and advice not in seen:
                boosters.append(advice)
                seen.add(advice)
        if not boosters:
            boosters.append("Resource Booster (doubles most material drops)")
        return boosters

    def get_bottleneck_resources(self, top_n: int = 5) -> list[dict[str, Any]]:
        """Return the top N resources with the highest farming time deficit."""
        plan = self.get_economy_plan()
        return [r for r in plan if r["missing"] > 0][:top_n]

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _resolve_owned(owned: dict, name: str) -> int:
        """Try to find an owned resource by name (case-insensitive)."""
        direct = owned.get(name, None)
        if direct is not None:
            return int(direct)
        lower_name = name.lower()
        for key, val in owned.items():
            if key.lower() == lower_name:
                return int(val)
        return 0


# ── Goal resource tables ──────────────────────────────────────────────────────
# Resource costs for common crafting goals (blueprint + parts combined)
GOAL_RESOURCE_REQUIREMENTS: dict[str, dict[str, int]] = {
    "wisp": {
        "Credits": 100_000,
        "Orokin Cell": 5,
        "Neural Sensors": 5,
        "Hexenon": 1_400,
        "Polymer Bundle": 1_200,
        "Circuits": 900,
        "Plastids": 650,
        "Nano Spores": 5_000,
    },
    "saryn": {
        "Credits": 100_000,
        "Orokin Cell": 6,
        "Neural Sensors": 3,
        "Plastids": 5_000,
        "Polymer Bundle": 3_000,
        "Circuits": 1_500,
        "Nano Spores": 6_500,
    },
    "rhino": {
        "Credits": 100_000,
        "Alloy Plate": 900,
        "Circuits": 1_200,
        "Neural Sensors": 5,
        "Plastids": 900,
        "Polymer Bundle": 600,
    },
    "forma": {
        "Credits": 35_000,
        "Orokin Cell": 1,
        "Morphics": 1,
        "Polymer Bundle": 500,
        "Neural Sensors": 1,
    },
    "reactor": {
        "Credits": 25_000,
        "Orokin Cell": 1,
        "Alloy Plate": 500,
        "Circuits": 650,
    },
    "catalyst": {
        "Credits": 25_000,
        "Orokin Cell": 1,
        "Alloy Plate": 500,
        "Morphics": 1,
    },
    "voidrig": {
        "Credits": 100_000,
        "Orokin Cell": 5,
        "Tellurium": 10,
        "Alloy Plate": 6_000,
        "Circuits": 2_100,
        "Polymer Bundle": 3_000,
    },
    "bonewidow": {
        "Credits": 100_000,
        "Orokin Cell": 5,
        "Tellurium": 10,
        "Rubedo": 5_000,
        "Circuits": 2_100,
        "Salvage": 10_000,
    },
}
