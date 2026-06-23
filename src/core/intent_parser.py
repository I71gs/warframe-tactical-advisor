from __future__ import annotations

class IntentParser:
    """Parses natural language questions into discrete tactical intents."""

    def parse_intent(self, query: str) -> dict[str, str]:
        """Maps natural language input to execution intent categories."""
        q = query.strip().lower()
        
        if any(kw in q for kw in ["tonight", "session", "do now", "what should i do", "today", "schedule"]):
            return {"intent": "RECOMMEND_DAILY_SESSION", "query": query}
            
        if "steel path" in q:
            return {"intent": "UNLOCK_STEEL_PATH", "query": query}
            
        if any(kw in q for kw in ["power gain", "biggest gain", "power boost", "upgrade", "increase damage", "better"]):
            return {"intent": "POWER_GAIN", "query": query}
            
        return {"intent": "GENERAL_QUERY", "query": query}
