from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING
from src.core.report_engine import ReportEngine

if TYPE_CHECKING:
    from src.core.app_context import AppContext

class ReportService:
    """Manages progression and inventory report compile and export operations."""

    def __init__(self, context: AppContext) -> None:
        self.context = context
        self.engine = ReportEngine()

    def export_json(self, filepath: str | Path) -> None:
        self.engine.export_json(filepath)

    def export_csv(self, filepath: str | Path) -> None:
        self.engine.export_csv(filepath)

    def export_text(self, filepath: str | Path) -> None:
        self.engine.export_text(filepath)
