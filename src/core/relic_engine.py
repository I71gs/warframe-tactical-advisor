from __future__ import annotations
import json
import math
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parents[1] / "resources" / "data"


def _load_relics() -> list[dict]:
    path = _DATA / "relics.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


RELIC_DATA: list[dict] = _load_relics()

# Trace costs to reach each refinement tier
REFINEMENT_TRACE_COST = {
    "Intact": 0,
    "Exceptional": 25,
    "Flawless": 50,
    "Radiant": 100,
}

# Best farming nodes by era (fallback when relic has no node listed)
ERA_BEST_NODES: dict[str, str] = {
    "Lith": "Hepit (Void, Capture)",
    "Meso": "Io (Jupiter, Defense)",
    "Neo": "Ukko (Void, Capture)",
    "Axi": "Apollo (Lua, Disruption)",
    "Requiem": "Any Kuva Fissure mission",
}

# Drop chance key per refinement
REFINEMENT_CHANCE_KEY = {
    "Intact": "drop_chance_intact",
    "Exceptional": "drop_chance_exceptional",
    "Flawless": "drop_chance_flawless",
    "Radiant": "drop_chance_radiant",
}


class RelicEngine:
    """Calculates optimal void relic refinements and farming routes for prime rewards.

    Uses full drop-table data from relics.json with per-refinement probabilities.
    """

    # ── public API ────────────────────────────────────────────────────────────

    def search_relics(self, query: str) -> list[dict[str, Any]]:
        """Return relics that contain items matching the query string."""
        q = query.strip().lower()
        if not q:
            return RELIC_DATA
        results = []
        for relic in RELIC_DATA:
            if q in relic["relic_name"].lower() or q in relic["era"].lower():
                results.append(relic)
                continue
            for reward in relic.get("rewards", []):
                if q in reward["item"].lower():
                    results.append(relic)
                    break
        return results

    def get_relics_for_item(self, item_name: str) -> list[dict[str, Any]]:
        """Return all relics that contain a specific item, with rarity info."""
        q = item_name.strip().lower()
        results = []
        for relic in RELIC_DATA:
            for reward in relic.get("rewards", []):
                if q in reward["item"].lower():
                    results.append({
                        "era": relic["era"],
                        "relic_name": relic["relic_name"],
                        "item": reward["item"],
                        "rarity": reward["rarity"],
                        "drop_chance_intact": reward.get("drop_chance_intact", 0),
                        "drop_chance_radiant": reward.get("drop_chance_radiant", 0),
                        "best_farm_node": relic.get("best_farm_node", ERA_BEST_NODES.get(relic["era"], "Unknown")),
                    })
        return results

    def plan_farming(self, item_name: str) -> dict[str, Any]:
        """Generate a complete farming plan for a specific item.

        Returns the best relic, recommended refinement, expected runs,
        best farm node, and trace cost breakdown.
        """
        matches = self.get_relics_for_item(item_name)
        if not matches:
            return {
                "item": item_name,
                "found": False,
                "message": f"No relic found containing '{item_name}'. Check spelling or try a partial name.",
            }

        # Pick the relic with highest Radiant drop chance
        best = max(matches, key=lambda r: r.get("drop_chance_radiant", 0))

        rarity = best["rarity"]
        recommended_refinement = self._recommend_refinement(rarity)
        chance_key = REFINEMENT_CHANCE_KEY[recommended_refinement]

        # Find the full relic entry to get the actual chance
        drop_chance = best.get(
            "drop_chance_radiant" if recommended_refinement == "Radiant" else "drop_chance_intact",
            2.0
        )

        expected_runs = self._expected_runs(drop_chance)
        trace_cost = REFINEMENT_TRACE_COST[recommended_refinement]
        era = best["era"]
        farm_node = best["best_farm_node"] or ERA_BEST_NODES.get(era, "Any Fissure mission")

        return {
            "item": best["item"],
            "found": True,
            "era": era,
            "relic_name": best["relic_name"],
            "rarity": rarity,
            "recommended_refinement": recommended_refinement,
            "drop_chance_pct": drop_chance,
            "expected_runs": expected_runs,
            "traces_needed": trace_cost,
            "best_farm_node": farm_node,
            "tip": self._farming_tip(rarity, era, expected_runs),
            "alternative_relics": [
                f"{m['era']} {m['relic_name']}" for m in matches
                if m["relic_name"] != best["relic_name"]
            ][:3],
        }

    def plan_farming_multi(self, item_names: list[str]) -> list[dict[str, Any]]:
        """Return farming plans for multiple items, sorted by expected runs (hardest first)."""
        plans = [self.plan_farming(name) for name in item_names]
        found = [p for p in plans if p.get("found")]
        not_found = [p for p in plans if not p.get("found")]
        found.sort(key=lambda p: p.get("expected_runs", 0), reverse=True)
        return found + not_found

    def calculate_expected_runs(self, drop_chance_pct: float) -> int:
        """Calculate expected number of runs to obtain an item given drop chance %."""
        return self._expected_runs(drop_chance_pct)

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _recommend_refinement(rarity: str) -> str:
        """Return the cost-effective refinement level based on rarity."""
        if "Rare" in rarity:
            return "Radiant"
        if "Uncommon" in rarity:
            return "Flawless"
        return "Intact"  # Common items are best opened Intact (saves traces)

    @staticmethod
    def _expected_runs(drop_chance_pct: float) -> int:
        """E[runs] = 1 / p (geometric distribution mean).

        Uses ceiling so we always recommend a whole number of runs.
        """
        if drop_chance_pct <= 0:
            return 999
        probability = drop_chance_pct / 100.0
        return max(1, math.ceil(1.0 / probability))

    @staticmethod
    def _farming_tip(rarity: str, era: str, expected_runs: int) -> str:
        tips = []
        if "Rare" in rarity:
            tips.append("Refine to Radiant and run with a full squad for shared reward picks.")
        if era == "Axi":
            tips.append("Apollo (Lua, Disruption) gives Axi relics every round.")
        if era == "Lith":
            tips.append("Hepit (Void, Capture) completes in ~90 sec — fastest Lith farm.")
        if era == "Neo":
            tips.append("Ukko (Void, Capture) is fastest for Neo relics.")
        if era == "Meso":
            tips.append("Io (Jupiter, Defense) gives Meso relics at Rotation B/C.")
        if expected_runs > 15:
            tips.append("High run count — consider using a resource booster weekend.")
        return " ".join(tips) if tips else "Happy farming, Tenno!"
