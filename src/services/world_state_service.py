from __future__ import annotations
import json
import urllib.request
import urllib.parse
from typing import Any, TYPE_CHECKING
from src.utils.logger import logger

if TYPE_CHECKING:
    from src.core.app_context import AppContext

class WorldStateService:
    """Service to fetch and cache live Warframe game-state and alerts."""

    def __init__(self, context: AppContext) -> None:
        self.context = context
        self.cached_state: dict[str, Any] = {}
        self.last_fetch_time = 0.0
        self.ttl = 60.0  # 60 seconds TTL

    def get_world_state(self) -> dict[str, Any]:
        """Fetch world state from api.warframestat.us or return cached data."""
        import time
        now = time.time()
        if now - self.last_fetch_time < self.ttl and self.cached_state:
            return self.cached_state

        try:
            state = self._fetch_live_state()
            self.cached_state = state
            self.last_fetch_time = now
            logger.info("World state successfully updated from API.")
        except Exception as exc:
            logger.error("Failed to fetch live world state: %s. Using fallback data.", exc)
            if not self.cached_state:
                self.cached_state = self._get_fallback_state()
        
        return self.cached_state

    def _fetch_live_state(self) -> dict[str, Any]:
        headers = {"User-Agent": "WarframeTacticalAdvisor/1.0 (contact: admin@wta.local)"}
        
        # Cetus Cycle
        cetus_req = urllib.request.Request("https://api.warframestat.us/pc/cetusCycle", headers=headers)
        with urllib.request.urlopen(cetus_req, timeout=5) as resp:
            cetus = json.loads(resp.read().decode("utf-8"))

        # Vallis Cycle
        vallis_req = urllib.request.Request("https://api.warframestat.us/pc/vallisCycle", headers=headers)
        with urllib.request.urlopen(vallis_req, timeout=5) as resp:
            vallis = json.loads(resp.read().decode("utf-8"))

        # Zariman Cycle
        zariman_req = urllib.request.Request("https://api.warframestat.us/pc/zarimanCycle", headers=headers)
        with urllib.request.urlopen(zariman_req, timeout=5) as resp:
            zariman = json.loads(resp.read().decode("utf-8"))

        # Fissures
        fissures_req = urllib.request.Request("https://api.warframestat.us/pc/fissures", headers=headers)
        with urllib.request.urlopen(fissures_req, timeout=5) as resp:
            fissures = json.loads(resp.read().decode("utf-8"))

        # Alerts
        alerts_req = urllib.request.Request("https://api.warframestat.us/pc/alerts", headers=headers)
        with urllib.request.urlopen(alerts_req, timeout=5) as resp:
            alerts = json.loads(resp.read().decode("utf-8"))

        return {
            "cetus": {
                "isDay": cetus.get("isDay", True),
                "timeLeft": cetus.get("timeLeft", "0m"),
                "shortString": cetus.get("shortString", "Day")
            },
            "vallis": {
                "isWarm": vallis.get("isWarm", True),
                "timeLeft": vallis.get("timeLeft", "0m"),
                "shortString": vallis.get("shortString", "Warm")
            },
            "zariman": {
                "state": zariman.get("state", "corpus"),
                "timeLeft": zariman.get("timeLeft", "0m")
            },
            "fissures": [
                {
                    "node": f.get("node", "Unknown"),
                    "missionType": f.get("missionType", "Unknown"),
                    "tier": f.get("tier", "Unknown"),
                    "enemy": f.get("enemy", "Unknown"),
                    "eta": f.get("eta", "Unknown")
                } for f in fissures
            ][:10], # Limit to top 10
            "alerts": [
                {
                    "mission": {
                        "node": a.get("mission", {}).get("node", "Unknown"),
                        "type": a.get("mission", {}).get("type", "Unknown")
                    },
                    "eta": a.get("eta", "Unknown"),
                    "reward": a.get("mission", {}).get("reward", {}).get("asString", "Unknown")
                } for a in alerts
            ][:5]
        }

    def _get_fallback_state(self) -> dict[str, Any]:
        return {
            "cetus": {"isDay": True, "timeLeft": "50m", "shortString": "50m to Night"},
            "vallis": {"isWarm": False, "timeLeft": "10m", "shortString": "10m to Warm"},
            "zariman": {"state": "corpus", "timeLeft": "1h 20m"},
            "fissures": [
                {"node": "E Prime (Earth)", "missionType": "Extermination", "tier": "Lith", "enemy": "Grineer", "eta": "20m"},
                {"node": "Taranis (Void)", "missionType": "Defense", "tier": "Meso", "enemy": "Corrupted", "eta": "45m"}
            ],
            "alerts": [
                {"mission": {"node": "Gaia (Earth)", "type": "Capture"}, "eta": "1h", "reward": "15000cr + 1x Orokin Cell"}
            ]
        }
