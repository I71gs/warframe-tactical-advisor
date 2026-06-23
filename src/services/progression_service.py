from __future__ import annotations
from typing import TYPE_CHECKING, Any
from src.core.progression_engine import ProgressionEngine
from src.core.personalized_progression_engine import PersonalizedProgressionEngine
from src.core.milestone_engine import MilestoneEngine
from src.core.progression_ai import ProgressionAI
from src.core.daily_objectives_engine import DailyObjectivesEngine
from src.core.weekly_planner import WeeklyPlanner
from src.core.long_term_planner import LongTermPlanner

if TYPE_CHECKING:
    from src.core.app_context import AppContext

class ProgressionService:
    """Orchestrates story progression, readiness checks, milestones, daily/weekly/long-term planners, and coach intelligence."""

    def __init__(self, context: AppContext) -> None:
        self.context = context
        self.pe = ProgressionEngine()
        self.ppe = PersonalizedProgressionEngine()
        self.me = MilestoneEngine()
        self.pai = ProgressionAI()
        self.doe = DailyObjectivesEngine()
        self.wp = WeeklyPlanner()
        self.ltp = LongTermPlanner()

    def get_stage(self) -> str:
        player = self.context.player_service.get_player()
        return self.pe.determine_stage(player)

    def get_primary_goal(self) -> str:
        player = self.context.player_service.get_player()
        return self.pe.get_primary_goal(player)

    def get_story_score(self) -> float:
        player = self.context.player_service.get_player()
        return self.pe.get_story_score(player)

    def get_readiness_score(self) -> float:
        player = self.context.player_service.get_player()
        return self.pe.get_readiness_score(player)

    def get_personalized_recommendation(self) -> dict[str, Any]:
        player = self.context.player_service.get_player()
        return self.ppe.analyze_profile(player)

    def get_next_action_directive(self) -> dict[str, Any]:
        player = self.context.player_service.get_player()
        return self.pai.get_session_plan(player)

    def get_milestones(self) -> list[dict[str, Any]]:
        player = self.context.player_service.get_player()
        return self.me.get_roadmap_timeline(player)

    def get_daily_objectives(self) -> dict[str, Any]:
        player = self.context.player_service.get_player()
        return self.doe.get_daily_objectives(player)

    def save_daily_objectives(self, state: dict[str, Any]) -> None:
        self.doe.save_daily_state(state)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def get_weekly_goals(self) -> dict[str, Any]:
        player = self.context.player_service.get_player()
        return self.wp.get_weekly_state(player)

    def save_weekly_goals(self, state: dict[str, Any]) -> None:
        self.wp.save_weekly_state(state)
        self.context.event_bus.publish("PROFILE_UPDATED")

    def get_long_term_plan(self) -> dict[str, Any]:
        player = self.context.player_service.get_player()
        return self.ltp.get_plan(player)
