from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from src.core.search_engine_v2 import SearchEngineV2
from src.core.app_context import AppContext
from src.core.plugin_registry import PluginRegistry

ROOT = Path(__file__).resolve().parents[2]

class SearchEngineV3(SearchEngineV2):
    """Offline unified search engine 3.0 extending 2.0 to improve search ranking
    and relevance for core milestones and terms using aliases and tags.
    """
    def __init__(self, context: AppContext | None = None) -> None:
        super().__init__(context)
        self.aliases = {}
        self.tags = {}
        self.load_metadata()

    def load_metadata(self) -> None:
        try:
            alias_path = ROOT / "data" / "aliases.json"
            if alias_path.exists():
                with open(alias_path, "r", encoding="utf-8") as f:
                    self.aliases = json.load(f)
        except Exception:
            pass
            
        try:
            tag_path = ROOT / "data" / "tags.json"
            if tag_path.exists():
                with open(tag_path, "r", encoding="utf-8") as f:
                    self.tags = json.load(f)
        except Exception:
            pass

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return []

        expanded_queries = [q]
        # Expand query based on aliases
        for alias_key, target_list in self.aliases.items():
            if q == alias_key:
                expanded_queries.extend([t.lower() for t in target_list])
            elif alias_key in q:
                for target in target_list:
                    expanded_queries.append(q.replace(alias_key, target.lower()))

        results = []
        for eq in set(expanded_queries):
            results.extend(super().search(eq))

        # Check tags and add any items associated with that tag if not already in the search results
        for tag_name, items_list in self.tags.items():
            if q == tag_name or tag_name in q:
                for item_name in items_list:
                    if not any(r["name"].lower() == item_name.lower() for r in results):
                        from src.core.weapon_database import WEAPONS
                        weapon_obj = next((w for w in WEAPONS if w["name"].lower() == item_name.lower()), None)
                        if weapon_obj:
                            results.append({
                                "category": "WEAPON",
                                "name": weapon_obj["name"],
                                "relevance": 40,
                                "details": f"Type: {weapon_obj.get('type')} | Source: {weapon_obj.get('acquisition')}",
                                "wiki_url": self.wiki.get_article_url(weapon_obj["name"])
                            })
                        else:
                            mod_obj = next((m for m in self.kb.mods if m.get("name", "").lower() == item_name.lower()), None)
                            if mod_obj:
                                results.append({
                                    "category": "MOD",
                                    "name": mod_obj["name"],
                                    "relevance": 40,
                                    "details": f"Category: {mod_obj.get('category')} | Source: {mod_obj.get('source')}",
                                    "wiki_url": self.wiki.get_article_url(mod_obj["name"])
                                })
                            else:
                                results.append({
                                    "category": "ITEM",
                                    "name": item_name,
                                    "relevance": 40,
                                    "details": f"Tagged under {tag_name}",
                                    "wiki_url": self.wiki.get_article_url(item_name)
                                })

        # Include custom routes registered by plugins
        pr = PluginRegistry()
        for r in pr.routes:
            target = r.get("weapon") or r.get("item") or ""
            source = r.get("source") or ""
            
            max_relevance = 0
            for eq in set(expanded_queries):
                relevance = self._calc_relevance(eq, f"{target} Route", target, source)
                if relevance > max_relevance:
                    max_relevance = relevance
                    
            if max_relevance > 0:
                results.append({
                    "category": "ROUTE",
                    "name": f"{target} Route",
                    "relevance": max_relevance,
                    "details": f"Farming Route: Farm {target} at {source} (Est: {r.get('estimated_time')})",
                    "wiki_url": self.wiki.get_article_url(target)
                })

        # Apply specific relevance boosts and tags boosts
        for item in results:
            name_lower = item["name"].lower()
            details_lower = item["details"].lower()

            boost = 0
            
            # Tag-based boosts
            for tag_name, items_list in self.tags.items():
                if q == tag_name or tag_name in q:
                    if any(it.lower() in name_lower or it.lower() in details_lower for it in items_list):
                        boost += 40

            # Direct keyword matches
            for eq in set(expanded_queries):
                if "phenmor" in eq:
                    if "phenmor" in name_lower:
                        boost += 50
                    if "phenmor" in details_lower:
                        boost += 20
                if "steel path" in eq:
                    if "steel path" in name_lower:
                        boost += 50
                    if "steel path" in details_lower:
                        boost += 20
                if "galvanized chamber" in eq:
                    if "galvanized chamber" in name_lower:
                        boost += 50
                    if "galvanized chamber" in details_lower:
                        boost += 20
                if "wisp" in eq:
                    if "wisp" in name_lower:
                        boost += 50
                    if "wisp" in details_lower:
                        boost += 20
                if "archon" in eq or "archons" in eq:
                    if "archon" in name_lower:
                        boost += 50
                    if "archon" in details_lower:
                        boost += 20

            item["relevance"] += boost

        # Deduplicate and sort by relevance descending, then by name alphabetically
        seen = set()
        dedup_results = []
        for r in results:
            key = (r["category"], r["name"])
            if key not in seen:
                seen.add(key)
                dedup_results.append(r)

        dedup_results.sort(key=lambda r: (-r["relevance"], r["name"].lower()))
        return dedup_results
