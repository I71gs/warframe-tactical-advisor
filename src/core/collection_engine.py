from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from src.models.player import Player
from src.core.weapon_database import WEAPONS
from src.core.arcane_database import ARCANES
from src.core.knowledge_base import KnowledgeBase

_DATA = Path(__file__).resolve().parents[1] / "resources" / "data"


def _load_json(filename: str) -> list[dict]:
    path = _DATA / filename
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


WARFRAME_ROSTER: list[dict] = _load_json("warframe_inventory.json")
COMPANION_ROSTER: list[dict] = _load_json("companions_full.json")
MASTERY_DATA: dict = {}
try:
    with open(_DATA / "mastery_items.json", encoding="utf-8") as _f:
        MASTERY_DATA = json.load(_f)
except Exception:
    pass

# Backward-compat alias used by search_engine_v2 and api/app
CORE_WARFRAMES: list[str] = [w["name"] for w in WARFRAME_ROSTER] or [
    "Wisp", "Saryn", "Mesa", "Volt", "Mirage", "Excalibur", "Rhino",
]


class CollectionEngine:
    """Calculates real inventory coverage across all collectible categories.

    Works with both the legacy flat Player lists (v1) and the v2 inventory
    dicts loaded from the database.  The v2 path is preferred when available.
    """

    # ── public API ────────────────────────────────────────────────────────────

    def get_collection_status(self, player: Player) -> dict[str, Any]:
        """Return per-category owned/total/pct stats and overall coverage."""
        kb = KnowledgeBase()

        wf = self._warframe_stats(player)
        comp = self._companion_stats(player)
        weap = self._weapon_stats(player)
        mod = self._mod_stats(player, kb)
        arc = self._arcane_stats(player)
        archwing = self._archwing_stats(player)
        necramech = self._necramech_stats(player)
        focus = self._focus_stats(player)
        intrinsics = self._intrinsic_stats(player)

        categories = [wf, comp, weap, mod, arc, archwing, necramech]
        overall_pct = round(
            sum(c["pct"] for c in categories) / len(categories), 1
        )

        return {
            "warframes":   wf,
            "companions":  comp,
            "weapons":     weap,
            "mods":        mod,
            "arcanes":     arc,
            "archwings":   archwing,
            "necramechs":  necramech,
            "focus":       focus,
            "intrinsics":  intrinsics,
            "overall_pct": overall_pct,
        }

    def get_missing_items(self, player: Player, category: str) -> list[str]:
        """Return a list of item names not yet owned in a given category."""
        status = self.get_collection_status(player)
        section = status.get(category, {})
        return section.get("missing", [])

    def get_full_collection_status(self, player: Player) -> dict[str, Any]:
        """Alias for get_collection_status — full detail including missing lists."""
        return self.get_collection_status(player)

    # ── internal helpers ──────────────────────────────────────────────────────

    def _warframe_stats(self, player: Player) -> dict[str, Any]:
        """Stats for Warframe inventory using v2 data where available."""
        roster = WARFRAME_ROSTER
        total = len(roster)
        if not total:
            total = 7

        if player.warframe_inventory:
            owned_names = {e["name"].lower() for e in player.warframe_inventory if e.get("owned")}
        else:
            # legacy fallback — use quest completion heuristics
            owned_names: set[str] = {"excalibur"}
            completed = {q.lower() for q in player.completed_quests}
            if player.mastery_rank >= 5:
                owned_names.add("rhino")
            if "angels of the zariman" in completed:
                owned_names.update({"wisp", "saryn"})

        owned_count = (
            len({e["name"].lower() for e in player.warframe_inventory if e.get("owned")})
            if player.warframe_inventory
            else len(owned_names)
        )

        missing = [
            w["name"] for w in roster
            if w["name"].lower() not in owned_names
        ]

        return {
            "owned": owned_count,
            "total": total,
            "pct": round(owned_count / total * 100, 1),
            "missing": missing[:20],  # cap list length for display
        }

    def _companion_stats(self, player: Player) -> dict[str, Any]:
        roster = COMPANION_ROSTER
        total = len(roster) or 1

        if player.companion_inventory:
            owned_names = {e["name"].lower() for e in player.companion_inventory if e.get("owned")}
            owned_count = len(owned_names)
        else:
            owned_names = {"carrier", "taxon"}  # most players start with these
            owned_count = len(owned_names)

        missing = [
            c["name"] for c in roster
            if c["name"].lower() not in owned_names
        ]

        return {
            "owned": owned_count,
            "total": total,
            "pct": round(owned_count / total * 100, 1),
            "missing": missing[:20],
        }

    def _weapon_stats(self, player: Player) -> dict[str, Any]:
        total = len(WEAPONS) or 1
        owned_lower = {w.lower() for w in player.owned_weapons}
        owned_count = sum(1 for w in WEAPONS if w["name"].lower() in owned_lower)
        missing = [w["name"] for w in WEAPONS if w["name"].lower() not in owned_lower]
        return {
            "owned": owned_count,
            "total": total,
            "pct": round(owned_count / total * 100, 1),
            "missing": missing[:20],
        }

    def _mod_stats(self, player: Player, kb: KnowledgeBase) -> dict[str, Any]:
        total = len(kb.mods) or 1
        owned_lower = {m.lower() for m in player.owned_mods}
        owned_count = sum(1 for m in kb.mods if m.get("name", "").lower() in owned_lower)
        missing = [
            m["name"] for m in kb.mods
            if m.get("name", "").lower() not in owned_lower
        ]
        return {
            "owned": owned_count,
            "total": total,
            "pct": round(owned_count / total * 100, 1),
            "missing": missing[:20],
        }

    def _arcane_stats(self, player: Player) -> dict[str, Any]:
        total = len(ARCANES) or 1
        owned_lower = {a.lower() for a in player.owned_arcanes}
        owned_count = sum(1 for a in ARCANES if a["name"].lower() in owned_lower)
        missing = [a["name"] for a in ARCANES if a["name"].lower() not in owned_lower]
        return {
            "owned": owned_count,
            "total": total,
            "pct": round(owned_count / total * 100, 1),
            "missing": missing[:20],
        }

    def _archwing_stats(self, player: Player) -> dict[str, Any]:
        roster = MASTERY_DATA.get("archwings", [
            {"name": "Itzal"}, {"name": "Elytron"},
            {"name": "Odonata"}, {"name": "Odonata Prime"}, {"name": "Amesha"},
        ])
        total = len(roster) or 1

        if player.archwing_inventory:
            owned_names = {e["name"].lower() for e in player.archwing_inventory if e.get("owned")}
        else:
            # Default: Odonata given from quest
            owned_names = {"odonata"}

        owned_count = len(owned_names)
        missing = [w["name"] for w in roster if w["name"].lower() not in owned_names]
        return {
            "owned": owned_count,
            "total": total,
            "pct": round(owned_count / total * 100, 1),
            "missing": missing,
        }

    def _necramech_stats(self, player: Player) -> dict[str, Any]:
        roster = MASTERY_DATA.get("necramechs", [
            {"name": "Voidrig"}, {"name": "Bonewidow"},
        ])
        total = len(roster) or 1

        if player.necramech_inventory:
            owned_names = {e["name"].lower() for e in player.necramech_inventory if e.get("owned")}
        else:
            owned_names = set()

        owned_count = len(owned_names)
        missing = [w["name"] for w in roster if w["name"].lower() not in owned_names]
        return {
            "owned": owned_count,
            "total": total,
            "pct": round(owned_count / total * 100, 1),
            "missing": missing,
        }

    def _focus_stats(self, player: Player) -> dict[str, Any]:
        schools = ["Zenurik", "Naramon", "Unairu", "Madurai", "Vazarin"]
        if player.focus_schools:
            active = [s["school"] for s in player.focus_schools if s.get("active")]
            unlocked_count = len(active)
        else:
            unlocked_count = 0
            active = []
        return {
            "schools": schools,
            "active": active,
            "unlocked": unlocked_count,
            "total": len(schools),
        }

    def _intrinsic_stats(self, player: Player) -> dict[str, Any]:
        categories = ["Piloting", "Gunnery", "Tactical", "Engineering", "Command"]
        intrinsics = player.intrinsics or {}
        total_possible = len(categories) * 10  # max rank 10 each
        current_total = sum(intrinsics.get(c, 0) for c in categories)
        per_cat = {c: intrinsics.get(c, 0) for c in categories}
        return {
            "per_category": per_cat,
            "total_ranks": current_total,
            "max_ranks": total_possible,
            "pct": round(current_total / total_possible * 100, 1) if total_possible > 0 else 0.0,
        }
