from __future__ import annotations
from typing import Any
from src.models.player import Player
from src.core.advisor_rules.progression_rules import check_progression
from src.core.advisor_rules.build_rules import check_builds
from src.core.advisor_rules.resource_rules import check_resources
from src.core.advisor_rules.strategy_rules import check_strategy

class ExpertSystem:
    """Rule-based inference engine matching player profile variables against optimization rules."""

    def evaluate(self, player: Player) -> list[dict[str, Any]]:
        """Run all progression, build, resource, and strategy checks to determine advice."""
        advice_list = []
        
        advice_list.extend(check_progression(player))
        advice_list.extend(check_builds(player))
        advice_list.extend(check_resources(player))
        advice_list.extend(check_strategy(player))
        
        return advice_list
