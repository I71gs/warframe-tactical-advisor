from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ANALYTICS_FILE = ROOT / 'cache' / 'analytics_data.json'
ANALYTICS_FILE.parent.mkdir(parents=True, exist_ok=True)

class AnalyticsService:
    """Manages anonymous, local-only usage statistics, tab metrics, and bottlenecks."""

    def __init__(self, filepath: Path | str | None = None) -> None:
        self.filepath = Path(filepath) if filepath else ANALYTICS_FILE
        self.data: dict[str, Any] = {
            "tab_views": {},
            "search_queries": {},
            "bottlenecks": {},
            "readiness_history": []
        }
        self.load_analytics()

    def load_analytics(self) -> None:
        """Loads metrics from local file."""
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        # Merge defaults
                        for k in self.data:
                            if k in loaded:
                                self.data[k] = loaded[k]
            except Exception:
                pass

    def save_analytics(self) -> None:
        """Saves current telemetry data to disk."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
        except Exception:
            pass

    def track_tab_view(self, tab_name: str) -> None:
        """Logs viewing hit count on a given tab."""
        views = self.data["tab_views"]
        views[tab_name] = views.get(tab_name, 0) + 1
        self.save_analytics()

    def track_search(self, query: str) -> None:
        """Logs search string query occurrences."""
        queries = self.data["search_queries"]
        queries[query] = queries.get(query, 0) + 1
        self.save_analytics()

    def track_bottleneck(self, bottleneck: str) -> None:
        """Logs common bottlenecks encountered by player state."""
        bottlenecks = self.data["bottlenecks"]
        bottlenecks[bottleneck] = bottlenecks.get(bottleneck, 0) + 1
        self.save_analytics()

    def track_readiness_score(self, score: float) -> None:
        """Appends the latest readiness score checkpoint."""
        history = self.data["readiness_history"]
        history.append(score)
        # Cap list at last 50 entries
        if len(history) > 50:
            history.pop(0)
        self.save_analytics()

    def get_metrics(self) -> dict[str, Any]:
        """Returns standard metrics summary."""
        return self.data

    def clear(self) -> None:
        """Resets telemetry state."""
        self.data = {
            "tab_views": {},
            "search_queries": {},
            "bottlenecks": {},
            "readiness_history": []
        }
        self.save_analytics()
