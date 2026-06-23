from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.quest_graph import QuestGraph
from src.core.knowledge_base import KnowledgeBase
from src.core.arcane_database import ARCANES
from src.core.weapon_database import WEAPONS

class GapAnalyzer:
    """Scans player profiles to determine missing quests, mods, arcanes, weapons, and unlocks."""

    def analyze_gaps(self, player: Player) -> list[dict[str, Any]]:
        gaps = []
        
        owned_mods = {m.lower() for m in player.owned_mods}
        owned_arcanes = {a.lower() for a in player.owned_arcanes}
        owned_weapons = {w.lower() for w in player.owned_weapons}
        completed_quests = {q.lower() for q in player.completed_quests}

        # 1. Unlocks & Main Benchmarks
        if not player.steel_path_unlocked:
            gaps.append({
                "category": "Unlock",
                "name": "Steel Path",
                "severity": "HIGH",
                "details": "Unlocks Steel Path missions, SP Honors, and Acolyte Arcane farming."
            })
        if not player.arbitrations_unlocked:
            gaps.append({
                "category": "Unlock",
                "name": "Arbitrations",
                "severity": "HIGH",
                "details": "Unlocks Arbitrations for farming Vitus Essence and Galvanized mods."
            })
        if not player.helminth_unlocked:
            gaps.append({
                "category": "Unlock",
                "name": "Helminth System",
                "severity": "MEDIUM",
                "details": "Unlocks ability to swap Warframe abilities."
            })

        # 2. Mastery Rank Gaps
        mr_benchmarks = [
            (10, "HIGH", "Required to access Arbitrations and Steel Path properly."),
            (12, "MEDIUM", "Required for Archon Hunts and secondary meta weapons."),
            (14, "MEDIUM", "Required for top-tier Zariman Incarnon weapons (Phenmor, Laetum, Felarx)."),
            (15, "LOW", "Required for Kuva Bramma and other high-mr items."),
            (16, "LOW", "Required to trade/wield all possible Riven mods.")
        ]
        for mr, severity, desc in mr_benchmarks:
            if player.mastery_rank < mr:
                gaps.append({
                    "category": "Mastery",
                    "name": f"Mastery Rank {mr}",
                    "severity": severity,
                    "details": desc
                })
                break # Only show the next immediate MR gap to keep UI clean

        # 3. Quests Gaps
        qg = QuestGraph()
        for quest in qg.dependencies.keys():
            if quest.lower() not in completed_quests:
                gaps.append({
                    "category": "Quest",
                    "name": quest,
                    "severity": "CRITICAL",
                    "details": "Key story progression milestone blocking gameplay content."
                })

        # 4. Mod Gaps
        kb = KnowledgeBase()
        for mod in kb.mods:
            mod_name = mod["name"]
            if mod_name.lower() not in owned_mods:
                severity = "HIGH" if "galvanized" in mod_name.lower() else "MEDIUM"
                gaps.append({
                    "category": "Mod",
                    "name": mod_name,
                    "severity": severity,
                    "details": f"Farmed from: {mod.get('source', 'Unknown')}"
                })

        # 5. Arcane Gaps
        for arcane in ARCANES:
            arc_name = arcane["name"]
            if arc_name.lower() not in owned_arcanes:
                severity = "HIGH" if "merciless" in arc_name.lower() else "LOW"
                gaps.append({
                    "category": "Arcane",
                    "name": arc_name,
                    "severity": severity,
                    "details": f"Farmed from: {arcane.get('acquisition', 'Unknown')}"
                })

        # 6. Weapon Gaps
        high_meta = {"phenmor", "laetum", "felarx", "kuva bramma", "kuva nukor"}
        for weapon in WEAPONS:
            w_name = weapon["name"]
            w_lower = w_name.lower()
            if w_lower not in owned_weapons:
                severity = "MEDIUM" if w_lower in high_meta else "LOW"
                gaps.append({
                    "category": "Weapon",
                    "name": w_name,
                    "severity": severity,
                    "details": f"Farmed from: {weapon.get('acquisition', 'Unknown')}"
                })

        # Sort gaps: CRITICAL first, then HIGH, then MEDIUM, then LOW
        sev_priority = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        gaps.sort(key=lambda g: sev_priority.get(g["severity"], 4))
        return gaps
