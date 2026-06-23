from __future__ import annotations
from typing import Any
from src.models.player import Player

class GoalPlanner:
    """Generates dynamic, profile-aware progression plans for specific endgame goals."""

    def get_goal_plan(self, player: Player, goal: str) -> list[dict[str, Any]]:
        plans = {
            "Unlock Steel Path": [
                "Complete The New War",
                "Complete Angels of the Zariman",
                "Clear Remaining Star Chart Nodes",
                "Acquire Galvanized Chamber",
                "Acquire Primary Merciless",
                "Unlock Steel Path"
            ],
            "Become Archon Ready": [
                "Complete The New War",
                "Reach MR12",
                "Acquire Primary Merciless",
                "Acquire Strong Primary Weapon",
                "Unlock Archon Hunts"
            ],
            "Reach Endgame": [
                "Complete Complete Main Story", # will fall back to general story checks
                "Unlock Steel Path",
                "Acquire Phenmor",
                "Acquire Endgame Arcanes",
                "Optimize Builds"
            ],
            "Finish Main Story": [
                "Complete The War Within",
                "Complete The Sacrifice",
                "Complete The New War"
            ]
        }

        steps = plans.get(goal, [])
        result = []

        for step in steps:
            completed, unmet = self._is_step_completed(player, step)
            result.append({
                "step": step,
                "completed": completed,
                "unmet": unmet
            })

        return result

    def _is_step_completed(self, player: Player, step_text: str) -> tuple[bool, list[str]]:
        from src.core.dependency_engine import DependencyEngine
        dep_engine = DependencyEngine()
        
        text_lower = step_text.lower()
        completed = False
        unmet: list[str] = []
        
        # 1. Quests check
        if "complete " in text_lower:
            quest_name = step_text.replace("Complete ", "").strip()
            if quest_name == "Complete Main Story":
                quest_name = "The New War"
            completed = any(q.lower() == quest_name.lower() for q in player.completed_quests)
            if not completed:
                from src.core.quest_graph import QuestGraph
                qg = QuestGraph()
                unmet_quests = qg.get_prerequisites(quest_name)
                for uq in unmet_quests:
                    if uq.lower() not in {q.lower() for q in player.completed_quests}:
                        unmet.append(f"Quest: {uq}")

        # 2. Acquire check (mods, arcanes, weapons)
        elif "acquire " in text_lower:
            item_name = step_text.replace("Acquire ", "").strip()
            item_lower = item_name.lower()
            
            owned_mods = {m.lower() for m in player.owned_mods}
            owned_arcanes = {a.lower() for a in player.owned_arcanes}
            owned_weapons = {w.lower() for w in player.owned_weapons}
            
            if item_lower == "strong primary weapon":
                meta_primaries = {"phenmor", "felarx", "torid", "burston incarnon", "latron incarnon", "kuva bramma"}
                completed = any(p in owned_weapons for p in meta_primaries)
            elif item_lower == "strong meta weapon" or item_lower == "strong weapon":
                meta_weapons = {"phenmor", "laetum", "felarx", "torid", "burston incarnon", "latron incarnon", "kuva bramma", "kuva nukor"}
                completed = any(w in owned_weapons for w in meta_weapons)
            elif item_lower == "endgame arcanes":
                meta_arcanes = {"primary merciless", "secondary merciless", "arcane energize", "molt augmented"}
                completed = any(a in owned_arcanes for a in meta_arcanes)
            else:
                completed = (item_lower in owned_mods) or (item_lower in owned_arcanes) or (item_lower in owned_weapons)
                
            if not completed:
                unmet = dep_engine.get_unmet_dependencies(item_name, player)
                
        # 3. Steel Path check
        elif "unlock steel path" in text_lower:
            completed = player.steel_path_unlocked
            if not completed:
                if not player.arbitrations_unlocked:
                    unmet.append("Clear Star Chart Nodes")
                if player.mastery_rank < 10:
                    unmet.append("MR10+")
                    
        # 4. Clear star chart nodes
        elif "clear remaining star chart nodes" in text_lower:
            completed = player.arbitrations_unlocked
            
        # 5. MR checks
        elif "reach mr" in text_lower:
            try:
                mr_val = int("".join(c for c in step_text if c.isdigit()))
                completed = player.mastery_rank >= mr_val
            except Exception:
                pass
                
        # 6. Unlock Archon Hunts
        elif "unlock archon hunts" in text_lower or "become archon ready" in text_lower:
            completed = ("the new war" in {q.lower() for q in player.completed_quests}) and player.mastery_rank >= 12
            if not completed:
                if "the new war" not in {q.lower() for q in player.completed_quests}:
                    unmet.append("Quest: The New War")
                if player.mastery_rank < 12:
                    unmet.append("MR12+")
                    
        # 7. Optimize builds
        elif "optimize builds" in text_lower:
            owned_mods = {m.lower() for m in player.owned_mods}
            owned_arcanes = {a.lower() for a in player.owned_arcanes}
            galvanized_count = sum(1 for m in ["galvanized chamber", "galvanized aptitude"] if m in owned_mods)
            merciless_count = sum(1 for a in ["primary merciless", "secondary merciless"] if a in owned_arcanes)
            completed = galvanized_count >= 1 and merciless_count >= 1

        return completed, unmet