from __future__ import annotations
from typing import Any
from src.core.search_engine_v2 import SearchEngineV2
from src.core.app_context import AppContext
from src.core.plugin_registry import PluginRegistry

class SearchEngineV3(SearchEngineV2):
    """Offline unified search engine 3.0 extending 2.0 to improve search ranking
    and relevance for core milestones and terms.
    """
    def __init__(self, context: AppContext | None = None) -> None:
        super().__init__(context)

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return []

        # Get results from SearchEngineV2
        results = super().search(query)

        # Include custom routes registered by plugins
        pr = PluginRegistry()
        for r in pr.routes:
            target = r.get("weapon") or r.get("item") or ""
            source = r.get("source") or ""
            relevance = self._calc_relevance(q, f"{target} Route", target, source)
            if relevance > 0:
                results.append({
                    "category": "ROUTE",
                    "name": f"{target} Route",
                    "relevance": relevance,
                    "details": f"Farming Route: Farm {target} at {source} (Est: {r.get('estimated_time')})",
                    "wiki_url": self.wiki.get_article_url(target)
                })

        # Apply specific relevance boosts for requested terms:
        # "phenmor", "steel path", "galvanized chamber", "wisp", "archons"
        for item in results:
            name_lower = item["name"].lower()
            details_lower = item["details"].lower()
            category_lower = item["category"].lower()

            boost = 0
            if "phenmor" in q:
                if "phenmor" in name_lower:
                    boost += 50
                if "phenmor" in details_lower:
                    boost += 20
            if "steel path" in q:
                if "steel path" in name_lower:
                    boost += 50
                if "steel path" in details_lower:
                    boost += 20
            if "galvanized chamber" in q:
                if "galvanized chamber" in name_lower:
                    boost += 50
                if "galvanized chamber" in details_lower:
                    boost += 20
            if "wisp" in q:
                if "wisp" in name_lower:
                    boost += 50
                if "wisp" in details_lower:
                    boost += 20
            if "archon" in q or "archons" in q:
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
