from __future__ import annotations
from typing import Any
from src.core.weapon_database import WEAPONS
from src.core.arcane_database import ARCANES
from src.core.knowledge_base import KnowledgeBase
from src.core.wiki_service import WikiService
from src.core.goal_planner import GoalPlanner

class SearchEngine:
    """Offline search engine indexing and categorizing weapons, mods, arcanes, quests, and goals."""

    def __init__(self) -> None:
        self.wiki = WikiService()
        self.kb = KnowledgeBase()
        self.gp = GoalPlanner()

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return []

        results = []

        # 1. Search Weapons
        for w in WEAPONS:
            name = w["name"]
            category = w.get("category", "")
            acq = w.get("acquisition", "")
            
            relevance = self._calc_relevance(q, name, category, acq)
            if relevance > 0:
                results.append({
                    "category": "WEAPON",
                    "name": name,
                    "relevance": relevance,
                    "details": f"Type: {w.get('type')} | Category: {category} | Source: {acq} | Meta Rating: {w.get('meta_rating')}",
                    "wiki_url": self.wiki.get_article_url(name)
                })

        # 2. Search Mods
        for m in self.kb.mods:
            name = m.get("name", "")
            cat = m.get("category", "")
            src = m.get("source", "")
            
            relevance = self._calc_relevance(q, name, cat, src)
            if relevance > 0:
                results.append({
                    "category": "MOD",
                    "name": name,
                    "relevance": relevance,
                    "details": f"Category: {cat} | Source: {src} | Importance Score: {m.get('importance')}",
                    "wiki_url": self.wiki.get_article_url(name)
                })

        # 3. Search Arcanes
        for a in ARCANES:
            name = a["name"]
            acq = a.get("acquisition", "")
            type_str = a.get("type", "")
            
            relevance = self._calc_relevance(q, name, type_str, acq)
            if relevance > 0:
                results.append({
                    "category": "ARCANE",
                    "name": name,
                    "relevance": relevance,
                    "details": f"Type: {type_str} | Source: {acq} | Importance Score: {a.get('importance')}",
                    "wiki_url": self.wiki.get_article_url(name)
                })

        # 4. Search Quests
        quest_names = [q.get("name") if isinstance(q, dict) else q for q in self.kb.quests]
        for name in quest_names:
            if not name:
                continue
            relevance = self._calc_relevance(q, name)
            if relevance > 0:
                results.append({
                    "category": "QUEST",
                    "name": name,
                    "relevance": relevance,
                    "details": f"Main story quest node.",
                    "wiki_url": self.wiki.get_article_url(name)
                })

        # 5. Search Goals
        goals = ["Unlock Steel Path", "Become Archon Ready", "Reach Endgame", "Finish Main Story"]
        for goal in goals:
            relevance = self._calc_relevance(q, goal)
            if relevance > 0:
                results.append({
                    "category": "GOAL",
                    "name": goal,
                    "relevance": relevance,
                    "details": "Progression milestone roadmap.",
                    "wiki_url": ""
                })

        # Sort results by relevance descending, then alphabetically by name
        results.sort(key=lambda r: (-r["relevance"], r["name"].lower()))
        return results

    def _calc_relevance(self, query: str, name: str, *extra_fields: str) -> int:
        name_lower = name.lower()
        if query == name_lower:
            return 100
        if name_lower.startswith(query):
            return 80
        if query in name_lower:
            return 50
            
        # Check extra description fields
        for field in extra_fields:
            if field and query in field.lower():
                return 30
                
        return 0
