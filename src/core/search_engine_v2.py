from __future__ import annotations
from typing import Any
from pathlib import Path
from src.core.search_engine import SearchEngine
from src.core.weapon_database import WEAPONS
from src.core.arcane_database import ARCANES
from src.core.build_database import BUILDS
from src.core.relic_engine import RELIC_DATA
from src.core.companion_engine import COMPANIONS
from src.core.collection_engine import CORE_WARFRAMES
from src.core.achievement_engine import AchievementEngine
from src.core.app_context import AppContext
from src.core.plugin_manager import PLUGINS_DIR

class SearchEngineV2(SearchEngine):
    """Offline unified search engine 2.0 extending standard search to include
    warframes, builds, relics, resources, milestones, achievements, companions,
    daily tasks, and plugins.
    """
    def __init__(self, context: AppContext | None = None) -> None:
        super().__init__()
        self.context = context or AppContext()

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return []

        # Get results from base search (Weapons, Mods, Arcanes, Quests, Goals)
        results = super().search(query)

        # Get player for dynamic checks
        player = self.context.player_service.get_player()

        # Add Warframes if not already matched
        for wf in CORE_WARFRAMES:
            relevance = self._calc_relevance(q, wf)
            if relevance > 0:
                if not any(r["category"] == "WARFRAME" and r["name"] == wf for r in results):
                    results.append({
                        "category": "WARFRAME",
                        "name": wf,
                        "relevance": relevance,
                        "details": "Core Warframe for loadout compositions.",
                        "wiki_url": self.wiki.get_article_url(wf)
                    })

        # Add Builds
        for b in BUILDS:
            wp_name = b.get("weapon", "")
            elem = b.get("element", "")
            relevance = self._calc_relevance(q, f"{wp_name} Build", wp_name, elem)
            if relevance > 0:
                results.append({
                    "category": "BUILD",
                    "name": f"{wp_name} Build",
                    "relevance": relevance,
                    "details": f"Element: {elem} | Meta Rating: {b.get('rating')}% | Mods: {', '.join(b.get('mods', []))}",
                    "wiki_url": self.wiki.get_article_url(wp_name)
                })

        # Add Relics
        for r in RELIC_DATA:
            item = r.get("item", "")
            relic = r.get("relic", "")
            relevance = self._calc_relevance(q, f"{relic} Relic", item, relic)
            if relevance > 0:
                results.append({
                    "category": "RELIC",
                    "name": f"{relic} Relic",
                    "relevance": relevance,
                    "details": f"Drops: {item} ({r.get('rarity')}) | Best farm: {r.get('best_farm')}",
                    "wiki_url": self.wiki.get_article_url(relic)
                })

        # Add Resources
        resources = [
            {"name": "Voidplumes", "source": "Zariman Bounties / Exploration"},
            {"name": "Entrati Lanthorn", "source": "Zariman missions / Extraction"},
            {"name": "Thrax Plasm", "source": "Thrax enemies / Zariman missions"},
            {"name": "Credits", "source": "Index / Profit-Taker / Dark Sectors"},
            {"name": "Endo", "source": "Arbitrations / Arena / Railjack"},
            {"name": "Forma", "source": "Void Fissures / Relics"}
        ]
        for res in resources:
            name = res["name"]
            source = res["source"]
            relevance = self._calc_relevance(q, name, source)
            if relevance > 0:
                results.append({
                    "category": "RESOURCE",
                    "name": name,
                    "relevance": relevance,
                    "details": f"Farming Source: {source}",
                    "wiki_url": self.wiki.get_article_url(name)
                })

        # Add Achievements
        ae = AchievementEngine()
        for badge in ae.get_badges(player):
            name = badge.get("name", "")
            desc = badge.get("description", "")
            relevance = self._calc_relevance(q, name, desc)
            if relevance > 0:
                unlocked_str = "Unlocked" if badge.get("unlocked") else "Locked"
                results.append({
                    "category": "ACHIEVEMENT",
                    "name": name,
                    "relevance": relevance,
                    "details": f"Status: {unlocked_str} | {desc}",
                    "wiki_url": ""
                })

        # Add Companions
        for comp in COMPANIONS:
            name = comp.get("name", "")
            rat = comp.get("rationale", "")
            relevance = self._calc_relevance(q, name, rat)
            if relevance > 0:
                results.append({
                    "category": "COMPANION",
                    "name": name,
                    "relevance": relevance,
                    "details": f"Synergy: {comp.get('synergy')} | Utility: {comp.get('utility')} | {rat[:60]}...",
                    "wiki_url": self.wiki.get_article_url(name)
                })

        # Add Daily tasks
        daily_tasks = [
            "Unlock Arbitrations: Complete all Star Chart nodes",
            "Farm Arbitrations for Galvanized Chamber mod",
            "Farm Arbitrations for Galvanized Aptitude mod",
            "Unlock Steel Path: Talk to Teshin at any Relay",
            "Farm Steel Path Acolytes for Primary Merciless",
            "Run Zariman Bounties to acquire Phenmor",
            "Run Zariman Bounties to acquire Laetum",
            "Complete a Daily Steel Path Incursion",
            "Complete 3 Syndicate Missions for Standing",
            "Run Void Fissures to open 3 Relics",
            "Perform 3 Helminth Invigorations / Feeds"
        ]
        for task in daily_tasks:
            relevance = self._calc_relevance(q, task)
            if relevance > 0:
                results.append({
                    "category": "DAILY TASK",
                    "name": task,
                    "relevance": relevance,
                    "details": "Daily progression checklist objective.",
                    "wiki_url": ""
                })

        # Add Plugins
        if PLUGINS_DIR.exists():
            for p_file in PLUGINS_DIR.glob("*.json"):
                name = p_file.name
                relevance = self._calc_relevance(q, name)
                if relevance > 0:
                    results.append({
                        "category": "PLUGIN",
                        "name": name,
                        "relevance": relevance,
                        "details": f"Custom plugin definition file: {p_file.name}",
                        "wiki_url": ""
                    })

        # Deduplicate and sort results by relevance descending, then alphabetically by name
        seen = set()
        dedup_results = []
        for r in results:
            key = (r["category"], r["name"])
            if key not in seen:
                seen.add(key)
                dedup_results.append(r)

        dedup_results.sort(key=lambda r: (-r["relevance"], r["name"].lower()))
        return dedup_results
