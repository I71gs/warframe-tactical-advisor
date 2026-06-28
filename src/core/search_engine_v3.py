from __future__ import annotations
import json
import difflib
from pathlib import Path
from typing import Any
from src.core.search_engine_v2 import SearchEngineV2
from src.core.app_context import AppContext
from src.core.plugin_registry import PluginRegistry
from src.database.database import DatabaseManager

ROOT = Path(__file__).resolve().parents[2]


class SearchEngineV3(SearchEngineV2):
    """Offline unified search engine 3.0 extending 2.0 to support fuzzy matching,
    search history persistence, bookmark favorites, and tag-based filtering.
    """

    def __init__(self, context: AppContext | None = None) -> None:
        super().__init__(context)
        self.aliases = {}
        self.tags = {}
        self.load_metadata()
        self.db = DatabaseManager()

    def load_metadata(self) -> None:
        try:
            alias_path = ROOT / "src" / "resources" / "data" / "aliases.json"
            if alias_path.exists():
                with open(alias_path, "r", encoding="utf-8") as f:
                    self.aliases = json.load(f)
        except Exception:
            pass

        try:
            tag_path = ROOT / "src" / "resources" / "data" / "tags.json"
            if tag_path.exists():
                with open(tag_path, "r", encoding="utf-8") as f:
                    self.tags = json.load(f)
        except Exception:
            pass

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return []

        # Persist query to SQLite history
        self.db.add_search_history(query)

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

        # Check tags and add associated items
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
                                "relevance": 45,
                                "details": f"Type: {weapon_obj.get('type')} | Source: {weapon_obj.get('acquisition')}",
                                "wiki_url": self.wiki.get_article_url(weapon_obj["name"])
                            })
                        else:
                            mod_obj = next((m for m in self.kb.mods if m.get("name", "").lower() == item_name.lower()), None)
                            if mod_obj:
                                results.append({
                                    "category": "MOD",
                                    "name": mod_obj["name"],
                                    "relevance": 45,
                                    "details": f"Category: {mod_obj.get('category')} | Source: {mod_obj.get('source')}",
                                    "wiki_url": self.wiki.get_article_url(mod_obj["name"])
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

            # Direct keyword boosts
            boost_words = ["phenmor", "steel path", "galvanized chamber", "wisp", "archon"]
            for word in boost_words:
                if word in q:
                    if word in name_lower:
                        boost += 50
                    if word in details_lower:
                        boost += 20

            item["relevance"] += boost

        # Deduplicate
        seen = set()
        dedup_results = []
        for r in results:
            key = (r["category"], r["name"])
            if key not in seen:
                seen.add(key)
                dedup_results.append(r)

        # Fuzzy matching: if few or no results, find close names using SequenceMatcher
        if len(dedup_results) < 5:
            all_candidate_names = []
            from src.core.weapon_database import WEAPONS
            all_candidate_names.extend([(w["name"], "WEAPON", f"Type: {w.get('type')} | Source: {w.get('acquisition')}") for w in WEAPONS])
            all_candidate_names.extend([(m["name"], "MOD", f"Category: {m.get('category')} | Source: {m.get('source')}") for m in self.kb.mods if m.get("name")])

            for name, category, details in all_candidate_names:
                ratio = difflib.SequenceMatcher(None, q, name.lower()).ratio()
                if ratio > 0.65:
                    if not any(r["name"].lower() == name.lower() for r in dedup_results):
                        dedup_results.append({
                            "category": category,
                            "name": name,
                            "relevance": int(ratio * 50),
                            "details": f"Fuzzy match (similarity: {ratio:.0%}) | {details}",
                            "wiki_url": self.wiki.get_article_url(name)
                        })

        # Add Bookmark / Favorite metadata
        bookmarks = self.get_bookmarks()
        for r in dedup_results:
            r["bookmarked"] = r["name"].lower() in bookmarks

        dedup_results.sort(key=lambda r: (-r["relevance"], r["name"].lower()))
        return dedup_results

    # Bookmarks/Favorites System
    def get_bookmarks(self) -> set[str]:
        val = self.db.get_config("search_bookmarks")
        if not val:
            return set()
        try:
            return set(json.loads(val))
        except Exception:
            return set()

    def add_bookmark(self, name: str) -> None:
        b = self.get_bookmarks()
        b.add(name.strip().lower())
        self.db.set_config("search_bookmarks", json.dumps(list(b)))

    def remove_bookmark(self, name: str) -> None:
        b = self.get_bookmarks()
        b.discard(name.strip().lower())
        self.db.set_config("search_bookmarks", json.dumps(list(b)))
