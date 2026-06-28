from __future__ import annotations
import json
import math
from pathlib import Path
from typing import Any

from src.models.player import Player
from src.core.weapon_database import WEAPONS

_DATA = Path(__file__).resolve().parents[1] / "resources" / "data"


def _load_mastery_data() -> dict:
    path = _DATA / "mastery_items.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _load_warframe_roster() -> list[dict]:
    path = _DATA / "warframe_inventory.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _load_companions() -> list[dict]:
    path = _DATA / "companions_full.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


MASTERY_DATA: dict = _load_mastery_data()
WARFRAME_ROSTER: list[dict] = _load_warframe_roster()
COMPANION_ROSTER: list[dict] = _load_companions()

# Mastery XP thresholds per rank (cumulative, from MR0 to MR30)
MR_THRESHOLDS: dict[int, int] = {}
raw_thresholds = MASTERY_DATA.get("mastery_thresholds", {})
if raw_thresholds:
    MR_THRESHOLDS = {int(k): int(v) for k, v in raw_thresholds.items()}
else:
    # Fallback: 2500 * MR^2 cumulative formula
    cumulative = 0
    for mr in range(1, 31):
        cumulative += 2500 * mr
        MR_THRESHOLDS[mr] = cumulative

# XP per category (from JSON or defaults)
CATEGORY_XP = MASTERY_DATA.get("categories", {
    "Warframe":            {"xp_per_item": 6000},
    "Primary Weapon":      {"xp_per_item": 3000},
    "Secondary Weapon":    {"xp_per_item": 3000},
    "Melee Weapon":        {"xp_per_item": 3000},
    "Archwing":            {"xp_per_item": 6000},
    "Archwing Gun":        {"xp_per_item": 3000},
    "Archwing Melee":      {"xp_per_item": 3000},
    "Companion":           {"xp_per_item": 6000},
    "Companion Weapon":    {"xp_per_item": 3000},
    "K-Drive":             {"xp_per_item": 3000},
    "Necramech":           {"xp_per_item": 6000},
    "Necramech Weapon":    {"xp_per_item": 3000},
    "Parazon":             {"xp_per_item": 3000},
})


def _xp_needed_for_rank(mr: int) -> int:
    """Total XP needed to *reach* MR `mr` from MR 0."""
    return MR_THRESHOLDS.get(mr, 2500 * (mr ** 2))


def _xp_gap_to_next(mr: int) -> int:
    """XP needed to advance from `mr` to `mr+1`."""
    return _xp_needed_for_rank(mr + 1) - _xp_needed_for_rank(mr)


class MasteryPlanner:
    """Full Mastery Rank planning engine.

    Calculates:
    - XP deficit to next rank
    - Per-category item suggestions (weapons, frames, companions, K-drives, etc.)
    - Fastest path (items sorted by easiest-to-obtain per XP unit)
    - Timeline forecast (days to target MR at given items/day pace)
    """

    # ── public API ────────────────────────────────────────────────────────────

    def calculate_plan(self, player: Player) -> dict[str, Any]:
        """Return the core MR plan: deficit, suggestions, and timeline."""
        mr = player.mastery_rank
        xp_needed = _xp_gap_to_next(mr)

        owned_weapons_lower = {w.lower() for w in player.owned_weapons}
        owned_warframes_lower = {w.lower() for w in player.owned_warframes}
        owned_companions_lower = {c.lower() for c in player.owned_companions}

        suggestions = self._build_suggestions(
            owned_weapons_lower, owned_warframes_lower, owned_companions_lower, mr
        )

        daily_cap = 12_000
        days_to_next = max(1, math.ceil(xp_needed / daily_cap))

        return {
            "current_mr":    mr,
            "next_mr":       mr + 1,
            "xp_needed":     xp_needed,
            "xp_to_mr30":    max(0, _xp_needed_for_rank(30) - _xp_needed_for_rank(mr)),
            "days_estimate": f"≈ {days_to_next} day{'s' if days_to_next > 1 else ''}",
            "weapons_to_level":   suggestions["weapons"][:5],
            "frames_to_build":    suggestions["warframes"][:5],
            "companions_to_level": suggestions["companions"][:5],
            "archwings_to_level": suggestions["archwings"][:3],
            "all_suggestions":    suggestions,
        }

    def get_fastest_mr_path(self, player: Player, limit: int = 20) -> list[dict[str, Any]]:
        """Return the top `limit` items sorted by easiest-to-farm per XP unit.

        Prioritises items with low crafting cost / short acquisition and high XP.
        """
        mr = player.mastery_rank
        owned_lower = {w.lower() for w in player.owned_weapons}
        owned_lower |= {w.lower() for w in player.owned_warframes}
        owned_lower |= {w.lower() for w in player.owned_companions}

        candidates = self._all_unowned_items(player, owned_lower)

        # Simple heuristic score: items labelled "Market" or "Dojo" are easiest
        def ease_score(item: dict) -> int:
            acq = item.get("acquisition", "").lower()
            if "dojo" in acq or "market" in acq or "research" in acq:
                return 3
            if "junction" in acq or "quest" in acq or "nightwave" in acq:
                return 2
            if "void relic" in acq or "prime" in acq:
                return 1
            return 0

        candidates.sort(key=lambda i: (ease_score(i), i.get("xp", 3000)), reverse=True)
        return candidates[:limit]

    def get_mr_forecast(
        self, player: Player, items_per_day: int = 2
    ) -> dict[str, Any]:
        """Project how many days it will take to reach target MR levels.

        Args:
            player: Current player state.
            items_per_day: Average items the player can level to 30 per day.

        Returns:
            Dict with projections for MR+1, MR+5, MR 20, MR 30.
        """
        mr = player.mastery_rank
        xp_per_day = items_per_day * 3000  # conservative: weapon-level XP

        def days_to(target_mr: int) -> str:
            if target_mr <= mr:
                return "Already achieved"
            gap = _xp_needed_for_rank(target_mr) - _xp_needed_for_rank(mr)
            days = math.ceil(gap / xp_per_day)
            return f"≈ {days} day{'s' if days != 1 else ''}"

        return {
            "current_mr": mr,
            "items_per_day": items_per_day,
            "xp_per_day": xp_per_day,
            f"days_to_mr{mr + 1}":  days_to(mr + 1),
            "days_to_mr20":  days_to(20),
            "days_to_mr30":  days_to(30),
            "mr_milestones": {
                f"MR {t}": days_to(t)
                for t in (5, 10, 15, 20, 25, 30)
                if t > mr
            },
        }

    def get_category_breakdown(self, player: Player) -> dict[str, Any]:
        """Return unowned counts per category with XP potential."""
        owned_lower = {w.lower() for w in player.owned_weapons}
        owned_lower |= {w.lower() for w in player.owned_warframes}
        owned_lower |= {w.lower() for w in player.owned_companions}

        candidates = self._all_unowned_items(player, owned_lower)
        breakdown: dict[str, dict] = {}
        for item in candidates:
            cat = item.get("category", "Unknown")
            if cat not in breakdown:
                breakdown[cat] = {"count": 0, "xp_potential": 0}
            breakdown[cat]["count"] += 1
            breakdown[cat]["xp_potential"] += item.get("xp", 3000)

        return breakdown

    # ── internals ─────────────────────────────────────────────────────────────

    def _build_suggestions(
        self,
        owned_weapons: set[str],
        owned_warframes: set[str],
        owned_companions: set[str],
        mr: int,
    ) -> dict[str, list[dict]]:
        weapons: list[dict] = []
        for w in WEAPONS:
            if w["name"].lower() not in owned_weapons:
                weapons.append({
                    "name":     w["name"],
                    "category": w.get("category", "Primary"),
                    "xp":       CATEGORY_XP.get(w.get("category", "Primary Weapon"), {}).get("xp_per_item", 3000),
                    "source":   w.get("acquisition", "Dojo/Market"),
                })

        warframes: list[dict] = []
        for wf in WARFRAME_ROSTER:
            if wf["name"].lower() not in owned_warframes:
                warframes.append({
                    "name":     wf["name"],
                    "category": "Warframe",
                    "xp":       wf.get("xp", 6000),
                    "source":   wf.get("acquisition", "Various"),
                })

        companions: list[dict] = []
        for c in COMPANION_ROSTER:
            if c["name"].lower() not in owned_companions:
                companions.append({
                    "name":     c["name"],
                    "category": c.get("category", "Companion"),
                    "xp":       c.get("xp", 6000),
                    "source":   c.get("acquisition", "Various"),
                })

        archwings = [
            {"name": w["name"], "category": "Archwing", "xp": w.get("xp", 6000), "source": w.get("acquisition", "")}
            for w in MASTERY_DATA.get("archwings", [])
        ]

        return {
            "weapons":    weapons,
            "warframes":  warframes,
            "companions": companions,
            "archwings":  archwings,
        }

    def _all_unowned_items(self, player: Player, owned_lower: set[str]) -> list[dict]:
        items: list[dict] = []

        for w in WEAPONS:
            if w["name"].lower() not in owned_lower:
                items.append({
                    "name":     w["name"],
                    "category": w.get("category", "Primary Weapon"),
                    "xp":       3000,
                    "acquisition": w.get("acquisition", ""),
                })

        for wf in WARFRAME_ROSTER:
            if wf["name"].lower() not in owned_lower:
                items.append({
                    "name":     wf["name"],
                    "category": "Warframe",
                    "xp":       6000,
                    "acquisition": wf.get("acquisition", ""),
                })

        for c in COMPANION_ROSTER:
            if c["name"].lower() not in owned_lower:
                items.append({
                    "name":     c["name"],
                    "category": c.get("category", "Companion"),
                    "xp":       c.get("xp", 6000),
                    "acquisition": c.get("acquisition", ""),
                })

        for aw in MASTERY_DATA.get("archwings", []):
            if aw["name"].lower() not in owned_lower and aw.get("xp", 0) > 0:
                items.append({
                    "name":     aw["name"],
                    "category": "Archwing",
                    "xp":       aw.get("xp", 6000),
                    "acquisition": aw.get("acquisition", ""),
                })

        for nec in MASTERY_DATA.get("necramechs", []):
            if nec["name"].lower() not in owned_lower:
                items.append({
                    "name":     nec["name"],
                    "category": "Necramech",
                    "xp":       nec.get("xp", 6000),
                    "acquisition": nec.get("acquisition", ""),
                })

        return items
