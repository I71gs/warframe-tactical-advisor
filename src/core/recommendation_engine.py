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
        # LIVE WORLD STATE ALERTS & EVENTS
        # ----------------------------------
        try:
            from src.core.app_context import AppContext
            from src.utils.logger import logger
            wss = AppContext().world_state_service
            world_state = wss.get_world_state()
            
            # Alerts
            for alert in world_state.get("alerts", []):
                reward = alert.get("reward", "Unknown Reward")
                node = alert.get("mission", {}).get("node", "Unknown Node")
                m_type = alert.get("mission", {}).get("type", "Unknown Type")
                recommendations.append(
                    Recommendation(
                        action=f"Complete Alert: {node} ({m_type})",
                        reason=f"Time-sensitive live alert! Reward: {reward}. Remaining time: {alert.get('eta', 'N/A')}",
                        power_gain=85.0,
                        account_progress=90.0,
                        time_efficiency=95.0,
                        category="PROGRESSION"
                    )
                )

            # Archon Hunt
            archon = world_state.get("archonHunt")
            if archon and stage in ("mid_game", "late_game", "end_game"):
                boss = archon.get("boss", "Unknown Boss")
                faction = archon.get("faction", "Unknown Faction")
                recommendations.append(
                    Recommendation(
                        action=f"Complete Weekly Archon Hunt: {boss}",
                        reason=f"Time-sensitive weekly Hunt! Defeat the Archon to acquire an Archon Shard. Faction: {faction}",
                        power_gain=98.0,
                        account_progress=90.0,
                        time_efficiency=80.0,
                        category="ENDGAME"
                    )
                )

            # Baro Ki'Teer
            void_trader = world_state.get("voidTrader")
            if void_trader and void_trader.get("active"):
                loc = void_trader.get("location", "Unknown Location")
                recommendations.append(
                    Recommendation(
                        action=f"Visit Baro Ki'Teer at {loc}",
                        reason="Void Trader is currently active! Exchange Prime parts for Ducats to purchase rare Mods, Weapons, and Cosmetics.",
                        power_gain=90.0,
                        account_progress=80.0,
                        time_efficiency=90.0,
                        category="PROGRESSION"
                    )
                )

            # Void Fissures
            fissures = world_state.get("fissures", [])
            if fissures and stage in ("early_game", "mid_game"):
                for f in fissures[:2]:
                    node = f.get('node', 'Unknown')
                    tier = f.get('tier', 'Unknown')
                    m_type = f.get('missionType', 'Unknown')
                    recommendations.append(
                        Recommendation(
                            action=f"Run Void Fissure: {node} ({tier})",
                            reason=f"Open relics in active {tier} {m_type} fissure to acquire Prime blueprints and parts.",
                            power_gain=75.0,
                            account_progress=80.0,
                            time_efficiency=85.0,
                            category="PROGRESSION"
                        )
                    )
        except Exception as e:
            from src.utils.logger import logger
            logger.warning("Failed to integrate live world state into recommendations: %s", e)

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