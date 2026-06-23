from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.goal_planner import GoalPlanner

class GoalCostEngine:
    """Calculates completion requirements, estimates difficulty, and tracks time for selected player goals."""

    def calculate_cost(self, player: Player, goal: str) -> dict[str, Any]:
        gp = GoalPlanner()
        steps = gp.get_goal_plan(player, goal)
        
        prereqs = 0
        est_time = 0
        hardest_priority = 0 # 1=Easy, 2=Medium, 3=Hard
        
        # Hardcoded static baseline values if goals are already completed
        power_gains = {
            "Unlock Steel Path": 25,
            "Become Archon Ready": 30,
            "Reach Endgame": 40,
            "Finish Main Story": 20
        }
        
        for s in steps:
            if not s["completed"]:
                prereqs += 1
                step_text = s["step"].lower()
                
                # Estimate time dynamically based on task type
                if "complete" in step_text:
                    if "new war" in step_text:
                        est_time += 5
                        hardest_priority = max(hardest_priority, 2)
                    elif "zariman" in step_text:
                        est_time += 3
                        hardest_priority = max(hardest_priority, 2)
                    else:
                        est_time += 2
                        hardest_priority = max(hardest_priority, 1)
                elif "acquire" in step_text:
                    if "phenmor" in step_text or "laetum" in step_text or "felarx" in step_text:
                        est_time += 5
                        hardest_priority = max(hardest_priority, 3)
                    elif "merciless" in step_text:
                        est_time += 3
                        hardest_priority = max(hardest_priority, 2)
                    elif "galvanized" in step_text:
                        est_time += 2
                        hardest_priority = max(hardest_priority, 2)
                    else:
                        est_time += 3
                        hardest_priority = max(hardest_priority, 1)
                elif "steel path" in step_text:
                    est_time += 1
                    hardest_priority = max(hardest_priority, 3)
                else:
                    est_time += 1
                    hardest_priority = max(hardest_priority, 1)
                    
        # Difficulty categorization
        difficulty_labels = {0: "None (Done)", 1: "Easy", 2: "Medium", 3: "Hard"}
        difficulty = difficulty_labels.get(hardest_priority, "Medium")

        return {
            "goal": goal,
            "time": f"{est_time} hours" if est_time > 0 else "0 hours (Complete)",
            "difficulty": difficulty,
            "prerequisites": prereqs,
            "power_gain": f"+{power_gains.get(goal, 15)}%"
        }
