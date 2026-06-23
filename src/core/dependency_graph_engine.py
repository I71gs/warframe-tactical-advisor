from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.dependency_engine import DependencyEngine
from src.core.quest_graph import QuestGraph

class DependencyGraphEngine:
    """Recursively constructs dependency trees for items and milestones with status resolution."""

    def __init__(self) -> None:
        self.de = DependencyEngine()
        self.qg = QuestGraph()

    def get_graph(self, target_name: str, player: Player) -> dict[str, Any]:
        """Entry point to build the dependency tree for a target item or system unlock."""
        return self._resolve_node(target_name.strip(), player)

    def _resolve_node(self, name: str, player: Player) -> dict[str, Any]:
        name_lower = name.lower()
        completed_quests = {q.lower() for q in player.completed_quests}
        owned_weapons = {w.lower() for w in player.owned_weapons}
        owned_mods = {m.lower() for m in player.owned_mods}
        owned_arcanes = {a.lower() for a in player.owned_arcanes}

        children = []
        is_owned = False
        is_completed = False

        # 1. Check if the target is a Quest
        if name in self.qg.dependencies:
            is_completed = name_lower in completed_quests
            prereqs = self.qg.get_prerequisites(name)
            for p in prereqs:
                children.append(self._resolve_node(p, player))
            
            status = self._determine_status(is_completed, children)
            return {
                "name": name,
                "type": "QUEST",
                "status": status,
                "children": children
            }

        # 2. Check if the target is an Item (Weapon, Mod, Arcane)
        elif name_lower in self.de._prereqs:
            # Determine ownership
            if name_lower in owned_weapons or name_lower in owned_mods or name_lower in owned_arcanes:
                is_owned = True
            
            # Resolve prerequisites
            reqs = self.de._prereqs[name_lower]
            
            # Add MR prerequisite
            if reqs["mr"] > 0:
                mr_unlocked = player.mastery_rank >= reqs["mr"]
                children.append({
                    "name": f"Mastery Rank {reqs['mr']}",
                    "type": "MR",
                    "status": "unlocked" if mr_unlocked else "locked",
                    "children": []
                })
                
            # Add Quest prerequisites
            for q in reqs["quests"]:
                children.append(self._resolve_node(q, player))
                
            # Add other system prerequisites
            for flag in reqs["other"]:
                if flag == "arbitrations_unlocked":
                    children.append(self._resolve_node("Arbitrations", player))
                elif flag == "steel_path_unlocked":
                    children.append(self._resolve_node("Steel Path", player))
                elif flag == "helminth_unlocked":
                    children.append(self._resolve_node("Helminth System", player))

            status = self._determine_status(is_owned, children)
            return {
                "name": name,
                "type": "ITEM",
                "status": status,
                "children": children
            }

        # 3. Check if target is a core System Unlock
        elif name_lower == "arbitrations":
            is_completed = player.arbitrations_unlocked
            # Arbitrations require Angels of the Zariman completed (implied star chart clear)
            children.append(self._resolve_node("Angels of the Zariman", player))
            status = self._determine_status(is_completed, children)
            return {
                "name": "Arbitrations Unlocked",
                "type": "SYSTEM",
                "status": status,
                "children": children
            }

        elif name_lower == "steel path":
            is_completed = player.steel_path_unlocked
            children.append(self._resolve_node("Arbitrations", player))
            status = self._determine_status(is_completed, children)
            return {
                "name": "Steel Path Unlocked",
                "type": "SYSTEM",
                "status": status,
                "children": children
            }

        elif name_lower == "helminth system":
            is_completed = player.helminth_unlocked
            # Requires Rank 3 standing with Entrati - mock prerequisite as MR 8
            mr_unlocked = player.mastery_rank >= 8
            children.append({
                "name": "Mastery Rank 8",
                "type": "MR",
                "status": "unlocked" if mr_unlocked else "locked",
                "children": []
            })
            status = self._determine_status(is_completed, children)
            return {
                "name": "Helminth System Unlocked",
                "type": "SYSTEM",
                "status": status,
                "children": children
            }

        elif name_lower == "archon hunts":
            # Check player status (mock: unlocked if MR >= 5, New War completed, and Steel Path unlocked)
            is_completed = "the new war" in completed_quests and player.steel_path_unlocked and player.mastery_rank >= 5
            children.append(self._resolve_node("The New War", player))
            children.append(self._resolve_node("Steel Path", player))
            children.append(self._resolve_node("Arbitrations", player))
            children.append(self._resolve_node("Galvanized Chamber", player))
            status = self._determine_status(is_completed, children)
            return {
                "name": "Archon Hunts Unlocked",
                "type": "SYSTEM",
                "status": status,
                "children": children
            }

        # 4. Fallback default leaf node
        return {
            "name": name,
            "type": "UNKNOWN",
            "status": "unlocked",
            "children": []
        }

    def _determine_status(self, is_owned_or_completed: bool, children: list[dict[str, Any]]) -> str:
        if is_owned_or_completed:
            return "unlocked"
        
        # Check if all children (prerequisites) are unlocked
        all_unlocked = True
        for c in children:
            if c["status"] != "unlocked":
                all_unlocked = False
                break
                
        return "available" if all_unlocked else "locked"
