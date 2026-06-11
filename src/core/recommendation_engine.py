from __future__ import annotations

from src.models.player import Player
from src.models.recommendation import Recommendation

from src.core.knowledge_base import KnowledgeBase
from src.core.quest_graph import QuestGraph
from src.core.progression_engine import ProgressionEngine

from src.core.wiki_service import WikiService
from src.core.arcane_database import ARCANES
from src.core.weapon_database import WEAPONS

try:
    from src.core.wiki_service import WikiService
    wiki = WikiService()
except Exception:
    wiki = None


kb = KnowledgeBase()
graph = QuestGraph()
progression = ProgressionEngine()
wiki = WikiService()


class RecommendationEngine:

    def generate_recommendations(
        self,
        player: Player
    ) -> list[Recommendation]:

        recommendations: list[Recommendation] = []

        owned_mods = {
            mod.lower()
            for mod in player.owned_mods
        }

        owned_arcanes = {
            arcane.lower()
            for arcane in player.owned_arcanes
        }

        owned_weapons = {
            weapon.lower()
            for weapon in player.owned_weapons
        }

        stage = progression.determine_stage(
            player
        )

        next_quest = (
            progression.get_next_story_quest(
                player
            )
        )

        # ----------------------------------
        # STORY PROGRESSION
        # ----------------------------------

        if next_quest != "Story Complete":

            recommendations.append(
                Recommendation(
                    action=f"Complete {next_quest}",
                    reason="Next story progression milestone",
                    power_gain=100,
                    account_progress=100,
                    time_efficiency=90,
                    category="STORY"
                )
            )

        # ----------------------------------
        # STAGE OBJECTIVES
        # ----------------------------------

        if stage == "early_game":

            recommendations.append(
                Recommendation(
                    action="Clear Star Chart",
                    reason="Unlock major systems",
                    power_gain=80,
                    account_progress=95,
                    time_efficiency=85,
                    category="PROGRESSION"
                )
            )

        elif stage == "mid_game":

            recommendations.append(
                Recommendation(
                    action="Prepare For The New War",
                    reason="Major story milestone",
                    power_gain=90,
                    account_progress=95,
                    time_efficiency=80,
                    category="STORY"
                )
            )

        elif stage == "late_game":

            recommendations.append(
                Recommendation(
                    action="Farm Arbitrations",
                    reason="Unlock Galvanized Mods",
                    power_gain=95,
                    account_progress=90,
                    time_efficiency=80,
                    category="ENDGAME"
                )
            )

            if not player.steel_path_unlocked:

                recommendations.append(
                    Recommendation(
                        action="Unlock Steel Path",
                        reason="Access endgame content",
                        power_gain=100,
                        account_progress=100,
                        time_efficiency=60,
                        category="ENDGAME"
                    )
                )

        elif stage == "end_game":

            recommendations.append(
                Recommendation(
                    action="Optimize Endgame Builds",
                    reason="Maximize account power",
                    power_gain=90,
                    account_progress=70,
                    time_efficiency=95,
                    category="ENDGAME"
                )
            )

        # ----------------------------------
        # IMPORTANT MODS
        # ----------------------------------

        for mod in kb.mods:

            mod_name = mod["name"]

            if mod_name.lower() not in owned_mods:

                recommendations.append(
                    Recommendation(
                        action=f"Acquire {mod_name}",
                        reason=f"Farm from {mod['source']}",
                        power_gain=float(
                            mod["importance"]
                        ),
                        account_progress=80,
                        time_efficiency=70,
                        category="MOD"
                    )
                )

        # ----------------------------------
        # IMPORTANT ARCANES
        # ----------------------------------

        for arcane in ARCANES:

            name = arcane["name"]

            if name.lower() not in owned_arcanes:

                recommendations.append(
                    Recommendation(
                        action=f"Acquire {name}",
                        reason=(
                                    f"Farm from {arcane.get('acquisition', 'Unknown Source')}"
                                    f"\nWiki: {wiki.get_article_url(name)}"
                                ),
                        power_gain=float(
                            arcane.get(
                                "importance",
                                80
                            )
                        ),
                        account_progress=80,
                        time_efficiency=75,
                        category="ARCANE"
                    )
                )
        # ----------------------------------
        # IMPORTANT WEAPONS
        # ----------------------------------

        for weapon in WEAPONS:

            name = weapon["name"]

            if name.lower() not in owned_weapons:

                recommendations.append(
                    Recommendation(
                        action=f"Acquire {name}",
                        reason=(
                            f"{weapon.get('acquisition', 'Strong Meta Weapon')}"
                            f"\nWiki: {wiki.get_article_url(name)}"
                        ),
                        power_gain=float(
                            weapon.get(
                                "meta_rating",
                                70
                            )
                        ),
                        account_progress=70,
                        time_efficiency=75,
                        category="WEAPON"
                    )
                )
        # ----------------------------------
        # REMOVE DUPLICATES
        # ----------------------------------

        unique = {}

        for rec in recommendations:

            unique[rec.action] = rec

        recommendations = list(
            unique.values()
        )

        # ----------------------------------
        # SORT BY SCORE
        # ----------------------------------

        recommendations.sort(
            key=lambda r: r.calculate_score(),
            reverse=True
        )

        return recommendations