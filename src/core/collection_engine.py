from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.weapon_database import WEAPONS
from src.core.arcane_database import ARCANES
from src.core.knowledge_base import KnowledgeBase

CORE_WARFRAMES = ["Wisp", "Saryn", "Mesa", "Volt", "Mirage", "Excalibur", "Rhino"]

class CollectionEngine:
    """Calculates inventory coverage metrics across Warframes, weapons, mods, and arcanes."""

    def get_collection_status(self, player: Player) -> dict[str, Any]:
        kb = KnowledgeBase()
        
        owned_weapons = {w.lower() for w in player.owned_weapons}
        owned_mods = {m.lower() for m in player.owned_mods}
        owned_arcanes = {a.lower() for a in player.owned_arcanes}
        
        # 1. Warframes
        # Mock Warframe inventory check (assume Excalibur, Rhino, Wisp owned if present, or check if player completed story)
        completed_quests = {q.lower() for q in player.completed_quests}
        owned_frames_count = 1 # Start with Excalibur
        if player.mastery_rank >= 5:
            owned_frames_count += 1 # Rhino
        if "angels of the zariman" in completed_quests:
            owned_frames_count += 2 # Wisp, Saryn
        
        total_frames = len(CORE_WARFRAMES)
        wf_pct = round(owned_frames_count / total_frames * 100, 1)

        # 2. Weapons
        total_weapons = len(WEAPONS)
        owned_weapons_count = sum(1 for w in WEAPONS if w["name"].lower() in owned_weapons)
        weap_pct = round(owned_weapons_count / total_weapons * 100, 1) if total_weapons > 0 else 0.0

        # 3. Mods
        total_mods = len(kb.mods)
        owned_mods_count = sum(1 for m in kb.mods if m.get("name", "").lower() in owned_mods)
        mod_pct = round(owned_mods_count / total_mods * 100, 1) if total_mods > 0 else 0.0

        # 4. Arcanes
        total_arcanes = len(ARCANES)
        owned_arcanes_count = sum(1 for a in ARCANES if a["name"].lower() in owned_arcanes)
        arc_pct = round(owned_arcanes_count / total_arcanes * 100, 1) if total_arcanes > 0 else 0.0

        # Aggregate overall completion percentage
        avg_pct = round((wf_pct + weap_pct + mod_pct + arc_pct) / 4, 1)

        return {
            "warframes": {"owned": owned_frames_count, "total": total_frames, "pct": wf_pct},
            "weapons": {"owned": owned_weapons_count, "total": total_weapons, "pct": weap_pct},
            "mods": {"owned": owned_mods_count, "total": total_mods, "pct": mod_pct},
            "arcanes": {"owned": owned_arcanes_count, "total": total_arcanes, "pct": arc_pct},
            "overall_pct": avg_pct
        }
