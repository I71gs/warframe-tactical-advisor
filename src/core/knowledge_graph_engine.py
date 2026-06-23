from __future__ import annotations
from typing import Any

class KnowledgeGraphEngine:
    """Connects weapons, mods, arcanes, frames, resources, quests, and achievements into an offline semantic network."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, str]] = []
        self._build_graph()

    def _build_graph(self) -> None:
        # 1. Define Nodes
        self.nodes = {
            "Phenmor": {"type": "WEAPON", "desc": "Incarnon evolving primary rifle."},
            "Laetum": {"type": "WEAPON", "desc": "Incarnon evolving secondary pistol."},
            "Torid": {"type": "WEAPON", "desc": "AoE beam weapon scaling with Incarnon adapter."},
            "Galvanized Chamber": {"type": "MOD", "desc": "Arbitration rifle multishot mod."},
            "Galvanized Aptitude": {"type": "MOD", "desc": "Arbitration status damage mod."},
            "Primary Merciless": {"type": "ARCANE", "desc": "Steel Path rifle damage arcane."},
            "Wisp": {"type": "WARFRAME", "desc": "Haste support Warframe scaling Incarnon rates."},
            "Saryn": {"type": "WARFRAME", "desc": "Status spreading spores Warframe."},
            "Voidplumes": {"type": "RESOURCE", "desc": "Zariman rank standing item."},
            "Entrati Lanthorn": {"type": "RESOURCE", "desc": "Rare Zariman building component."},
            "Vitus Essence": {"type": "RESOURCE", "desc": "Arbitration drop token."},
            "Steel Essence": {"type": "RESOURCE", "desc": "Steel Path reward token."},
            "The New War": {"type": "QUEST", "desc": "Cinematic endgame prelude story quest."},
            "Angels of Zariman": {"type": "QUEST", "desc": "Zariman Chrysalith story quest."},
            "Steel Path": {"type": "UNLOCK", "desc": "High difficulty star chart mirror."},
            "Arbitrations": {"type": "MISSION", "desc": "Normal star chart completion missions."},
            "Story Master": {"type": "ACHIEVEMENT", "desc": "Complete main story badge."}
        }

        # 2. Define Edges
        self._add_edge("Phenmor", "Entrati Lanthorn", "REQUIRES")
        self._add_edge("Phenmor", "Voidplumes", "REQUIRES")
        self._add_edge("Phenmor", "Angels of Zariman", "UNLOCKED_BY")
        
        self._add_edge("Laetum", "Entrati Lanthorn", "REQUIRES")
        self._add_edge("Laetum", "Voidplumes", "REQUIRES")
        self._add_edge("Laetum", "Angels of Zariman", "UNLOCKED_BY")
        
        self._add_edge("Galvanized Chamber", "Arbitrations", "DROPS_IN")
        self._add_edge("Galvanized Chamber", "Vitus Essence", "COSTS")
        
        self._add_edge("Galvanized Aptitude", "Arbitrations", "DROPS_IN")
        self._add_edge("Galvanized Aptitude", "Vitus Essence", "COSTS")
        
        self._add_edge("Primary Merciless", "Steel Path", "UNLOCKED_BY")
        self._add_edge("Primary Merciless", "Steel Essence", "COSTS")
        
        self._add_edge("Wisp", "Phenmor", "SYNERGIZES_WITH")
        self._add_edge("Saryn", "Torid", "SYNERGIZES_WITH")
        
        self._add_edge("Angels of Zariman", "The New War", "REQUIRES")
        
        self._add_edge("Steel Path", "Arbitrations", "REQUIRES")
        
        self._add_edge("Story Master", "The New War", "REQUIRES")
        self._add_edge("Story Master", "Angels of Zariman", "REQUIRES")

    def _add_edge(self, source: str, target: str, relationship: str) -> None:
        self.edges.append({
            "source": source,
            "target": target,
            "relationship": relationship
        })

    def get_neighbors(self, node_name: str) -> list[dict[str, str]]:
        """Returns all adjacent nodes and their semantic relationships."""
        results = []
        name_lower = node_name.strip().lower()
        
        # Search direct out-edges and in-edges
        for edge in self.edges:
            if edge["source"].lower() == name_lower:
                results.append({
                    "node": edge["target"],
                    "relationship": edge["relationship"],
                    "direction": "outgoing"
                })
            elif edge["target"].lower() == name_lower:
                results.append({
                    "node": edge["source"],
                    "relationship": edge["relationship"],
                    "direction": "incoming"
                })
        return results

    def find_path(self, start: str, end: str) -> list[str] | None:
        """Simple breadth-first search path finder between two nodes in the graph."""
        if start not in self.nodes or end not in self.nodes:
            return None
            
        queue: list[list[str]] = [[start]]
        visited = {start}
        
        while queue:
            path = queue.pop(0)
            node = path[-1]
            
            if node == end:
                return path
                
            # Get adjacent node targets
            neighbors = [edge["target"] for edge in self.edges if edge["source"] == node] + \
                        [edge["source"] for edge in self.edges if edge["target"] == node]
                        
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)
        return None
