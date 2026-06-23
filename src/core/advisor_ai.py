from __future__ import annotations
from typing import Any
from src.core.app_context import AppContext
from src.core.intent_parser import IntentParser
from src.core.expert_system import ExpertSystem
from src.core.daily_objectives_engine import DailyObjectivesEngine

class AdvisorAI:
    """Coordinates natural language queries and translates them to tactical progression steps."""

    def __init__(self, context: AppContext | None = None) -> None:
        self.context = context or AppContext()
        self.intent_parser = IntentParser()
        self.expert_system = ExpertSystem()
        self.daily_engine = DailyObjectivesEngine()

    def get_advice(self, query: str) -> dict[str, str]:
        """Runs the expert system and intent parser to map user queries to progression tasks."""
        parsed = self.intent_parser.parse_intent(query)
        intent = parsed["intent"]
        
        player = self.context.player_service.get_player()
        advice_list = self.expert_system.evaluate(player)
        
        if intent == "RECOMMEND_DAILY_SESSION":
            # Retrieve objectives
            daily_data = self.daily_engine.get_daily_objectives(player)
            objs = daily_data.get("objectives", [])
            active_objs = [o["text"] for o in objs if not o.get("completed")]
            
            task = active_objs[0] if active_objs else "Complete 3 Void Fissures to gather Prime items"
            
            # Map daily tasks to ETAs and power gains from rules if possible
            matching_rule = None
            for rule in advice_list:
                if rule["rule_name"].lower() in task.lower() or task.lower() in rule["task"].lower():
                    matching_rule = rule
                    break
            
            if matching_rule:
                return {
                    "task": matching_rule["task"],
                    "eta": matching_rule["eta"],
                    "power_gain": matching_rule["power_gain"],
                    "prerequisites": matching_rule["prerequisites"],
                    "follow_up": matching_rule["follow_up"]
                }
            else:
                return {
                    "task": task,
                    "eta": "1-2 hours",
                    "power_gain": "+20% general progress",
                    "prerequisites": "Complete previous story milestone",
                    "follow_up": "Check the Session Planner tab to optimize your farming."
                }
                
        elif intent == "UNLOCK_STEEL_PATH":
            # Search advice list for steel path rules
            sp_rule = next((r for r in advice_list if "steel path" in r["rule_name"].lower() or "arbitrations" in r["rule_name"].lower()), None)
            if sp_rule:
                return {
                    "task": sp_rule["task"],
                    "eta": sp_rule["eta"],
                    "power_gain": sp_rule["power_gain"],
                    "prerequisites": sp_rule["prerequisites"],
                    "follow_up": sp_rule["follow_up"]
                }
            else:
                return {
                    "task": "Steel Path difficulty is already unlocked. Clear SP nodes to farm Acolyte Arcanes.",
                    "eta": "N/A",
                    "power_gain": "+60% (Acquire primary and secondary weapon arcanes)",
                    "prerequisites": "Talk to Teshin at any relay to activate",
                    "follow_up": "Acquire primary merciless to increase weapon damage by +360%."
                }
                
        elif intent == "POWER_GAIN":
            # Target build upgrades or weapon acqusitions first
            power_rule = next((r for r in advice_list if "upgrade" in r["rule_name"].lower() or "arcane" in r["rule_name"].lower() or "phenmor" in r["rule_name"].lower()), None)
            if not power_rule:
                power_rule = next((r for r in advice_list if r["power_gain"]), None)
                
            if power_rule:
                return {
                    "task": power_rule["task"],
                    "eta": power_rule["eta"],
                    "power_gain": power_rule["power_gain"],
                    "prerequisites": power_rule["prerequisites"],
                    "follow_up": power_rule["follow_up"]
                }
            else:
                return {
                    "task": "Max out all installed mods on your current meta loadout weapons",
                    "eta": "1-3 hours",
                    "power_gain": "+15% weapon scaling",
                    "prerequisites": "Own sufficient Credits and Endo",
                    "follow_up": "Use the Build Simulator tab to verify status multipliers."
                }
                
        else: # GENERAL_QUERY
            # Search global database for items matching query
            from src.core.search_engine_v2 import SearchEngineV2
            se = SearchEngineV2(self.context)
            results = se.search(query)
            if results:
                top = results[0]
                return {
                    "task": f"Search result: Learn about {top['name']} ({top['category']})",
                    "eta": "N/A",
                    "power_gain": "Varies by item utility",
                    "prerequisites": "None",
                    "follow_up": f"Details: {top['details']}. Wiki URL: {top['wiki_url']}"
                }
            else:
                return {
                    "task": "No direct matches found. Try searching for: Phenmor, Steel Path, or Galvanized Chamber",
                    "eta": "N/A",
                    "power_gain": "N/A",
                    "prerequisites": "N/A",
                    "follow_up": "Type a query related to Warframe milestones or weapons."
                }
