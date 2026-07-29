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

try:
    import rapidfuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

class SearchEngineV3(SearchEngineV2):
    """Offline unified search engine 3.0/4.0 supporting fuzzy matching via rapidfuzz,
    search history persistence, bookmark favorites, and dynamic preview metadata.
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

        # 1. Compile all candidate items from all application data sources
        candidates = []
        
        # Weapons
        from src.core.weapon_database import WEAPONS
        for w in WEAPONS:
            candidates.append({
                "name": w["name"],
                "category": "WEAPON",
                "details": f"Type: {w.get('type', 'Weapon')} | Category: {w.get('category', 'Melee')} | Source: {w.get('acquisition', 'Drops')} | Meta Rating: {w.get('meta_rating', 70)}% | MR Required: {w.get('mastery_required', 10)}",
                "wiki_url": self.wiki.get_article_url(w["name"]),
                "raw_data": w
            })

        # Warframes
        from src.core.collection_engine import CORE_WARFRAMES
        warframes_metadata = {}
        try:
            with open(ROOT / "src" / "resources" / "data" / "warframes.json", encoding="utf-8") as f:
                wf_data = json.load(f)
                warframes_metadata = {w["name"].lower(): w for w in wf_data}
        except Exception:
            pass
            
        for wf in CORE_WARFRAMES:
            meta = warframes_metadata.get(wf.lower(), {})
            details = f"Role: {meta.get('subsumed', 'Warframe')} | Synergies: {meta.get('synergies', 'Loadout buffer')} | Source: {meta.get('acquisition', 'Assassination / Relics')}"
            candidates.append({
                "name": wf,
                "category": "WARFRAME",
                "details": details,
                "wiki_url": self.wiki.get_article_url(wf),
                "raw_data": meta or {"name": wf}
            })

        # Relics
        from src.core.relic_engine import RELIC_DATA
        for r in RELIC_DATA:
            full_name = f"{r.get('era', '')} {r.get('relic_name', '')}".strip()
            drop_preview = ", ".join(rw["item"] for rw in r.get("rewards", [])[:3])
            candidates.append({
                "name": f"{full_name} Relic",
                "category": "RELIC",
                "details": f"Drops: {drop_preview} | Best farm: {r.get('best_farm_node', 'Void Fissures')}",
                "wiki_url": self.wiki.get_article_url(r.get('relic_name', '')),
                "raw_data": r
            })

        # Mods
        for m in self.kb.mods:
            name = m.get("name", "")
            if not name:
                continue
            candidates.append({
                "name": name,
                "category": "MOD",
                "details": f"Category: {m.get('category', 'Mod')} | Source: {m.get('source', 'Missions')} | Importance Score: {m.get('importance', 80)}",
                "wiki_url": self.wiki.get_article_url(name),
                "raw_data": m
            })

        # Arcanes
        from src.core.arcane_database import ARCANES
        for a in ARCANES:
            candidates.append({
                "name": a["name"],
                "category": "ARCANE",
                "details": f"Type: {a.get('type', 'Arcane')} | Source: {a.get('acquisition', 'Drops')} | Importance: {a.get('importance', 80)}",
                "wiki_url": self.wiki.get_article_url(a["name"]),
                "raw_data": a
            })

        # Companions
        from src.core.companion_engine import COMPANIONS
        for c in COMPANIONS:
            name = c.get("name", "")
            candidates.append({
                "name": name,
                "category": "COMPANION",
                "details": f"Synergy: {c.get('synergy')} | Utility: {c.get('utility')} | {c.get('rationale', '')[:50]}...",
                "wiki_url": self.wiki.get_article_url(name),
                "raw_data": c
            })

        # Resources
        resources = [
            {"name": "Voidplumes", "source": "Zariman Bounties / Exploration"},
            {"name": "Entrati Lanthorn", "source": "Zariman missions / Extraction"},
            {"name": "Thrax Plasm", "source": "Thrax enemies / Zariman missions"},
            {"name": "Credits", "source": "Index / Profit-Taker / Dark Sectors"},
            {"name": "Endo", "source": "Arbitrations / Arena / Railjack"},
            {"name": "Forma", "source": "Void Fissures / Relics"}
        ]
        for res in resources:
            candidates.append({
                "name": res["name"],
                "category": "RESOURCE",
                "details": f"Farming Source: {res['source']}",
                "wiki_url": self.wiki.get_article_url(res["name"]),
                "raw_data": res
            })

        # Quests / Missions
        quest_names = [q.get("name") if isinstance(q, dict) else q for q in self.kb.quests]
        for name in quest_names:
            if not name:
                continue
            candidates.append({
                "name": name,
                "category": "QUEST",
                "details": "Main story quest node.",
                "wiki_url": self.wiki.get_article_url(name),
                "raw_data": {"name": name}
            })

        # Daily Tasks
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
            candidates.append({
                "name": task,
                "category": "DAILY TASK",
                "details": "Daily progression checklist objective.",
                "wiki_url": "",
                "raw_data": {"name": task}
            })

        # Goals
        goals = ["Unlock Steel Path", "Become Archon Ready", "Reach Endgame", "Finish Main Story"]
        for goal in goals:
            candidates.append({
                "name": goal,
                "category": "GOAL",
                "details": "Progression milestone roadmap.",
                "wiki_url": "",
                "raw_data": {"name": goal}
            })

        # Achievements
        try:
            from src.core.achievement_engine import AchievementEngine
            ae = AchievementEngine()
            player = self.context.player_service.get_player()
            for badge in ae.get_badges(player):
                candidates.append({
                    "name": badge.get("name", ""),
                    "category": "ACHIEVEMENT",
                    "details": f"Status: {'Unlocked' if badge.get('unlocked') else 'Locked'} | {badge.get('description', '')}",
                    "wiki_url": "",
                    "raw_data": badge
                })
        except Exception:
            pass

        # 2. Expand queries using aliases (e.g. "sp" expands to "steel path")
        expanded_queries = [q]
        for alias_key, target_list in self.aliases.items():
            if q == alias_key:
                expanded_queries.extend([t.lower() for t in target_list])
            elif alias_key in q:
                for target in target_list:
                    expanded_queries.append(q.replace(alias_key, target.lower()))

        # 3. Match candidates using exact and fuzzy matching
        results = []
        for eq in set(expanded_queries):
            for c in candidates:
                name_lower = c["name"].lower()
                details_lower = c["details"].lower()
                relevance = 0

                # Check substring/exact matches
                if eq == name_lower:
                    relevance = 100
                elif name_lower.startswith(eq):
                    relevance = 85
                elif eq in name_lower:
                    relevance = 70
                elif eq in details_lower:
                    relevance = 40
                else:
                    # Apply typo-tolerant fuzzy matching
                    if HAS_RAPIDFUZZ:
                        ratio = rapidfuzz.fuzz.WRatio(eq, name_lower)
                        if ratio > 65:
                            relevance = int(ratio * 0.75)
                    else:
                        ratio = difflib.SequenceMatcher(None, eq, name_lower).ratio()
                        if ratio > 0.65:
                            relevance = int(ratio * 50)

                if relevance > 0:
                    item_copy = c.copy()
                    item_copy["relevance"] = relevance
                    results.append(item_copy)

        # Check tags and add associated items
        for tag_name, items_list in self.tags.items():
            if q == tag_name or tag_name in q:
                for item_name in items_list:
                    if not any(r["name"].lower() == item_name.lower() for r in results):
                        cand = next((c for c in candidates if c["name"].lower() == item_name.lower()), None)
                        if cand:
                            item_copy = cand.copy()
                            item_copy["relevance"] = 45
                            results.append(item_copy)

        # 4. Include custom routes registered by plugins
        try:
            pr = PluginRegistry()
            for r in pr.routes:
                target = r.get("weapon") or r.get("item") or ""
                source = r.get("source") or ""
                max_relevance = 0
                for eq in set(expanded_queries):
                    relevance = 0
                    full_route_name = f"{target} Route".lower()
                    if eq == full_route_name:
                        relevance = 100
                    elif full_route_name.startswith(eq):
                        relevance = 85
                    elif eq in full_route_name:
                        relevance = 70
                    elif eq in source.lower():
                        relevance = 40
                    if relevance > max_relevance:
                        max_relevance = relevance
                if max_relevance > 0:
                    results.append({
                        "category": "ROUTE",
                        "name": f"{target} Route",
                        "relevance": max_relevance,
                        "details": f"Farming Route: Farm {target} at {source} (Est: {r.get('estimated_time')})",
                        "wiki_url": self.wiki.get_article_url(target),
                        "raw_data": r
                    })
        except Exception:
            pass

        # 5. Apply tag boosts and direct boosts
        for item in results:
            name_lower = item["name"].lower()
            details_lower = item["details"].lower()
            boost = 0

            # Tag boosts
            for tag_name, items_list in self.tags.items():
                if q == tag_name or tag_name in q:
                    if any(it.lower() in name_lower or it.lower() in details_lower for it in items_list):
                        boost += 40

            # Direct word boosts
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
