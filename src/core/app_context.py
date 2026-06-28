from __future__ import annotations
from src.utils.event_bus import EventBus

class AppContext:
    """Dependency injection container managing service lifetimes."""
    _instance: AppContext | None = None

    def __new__(cls) -> AppContext:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_context()
        return cls._instance

    def _init_context(self) -> None:
        self.event_bus = EventBus()
        
        from src.services.player_service import PlayerService
        from src.services.progression_service import ProgressionService
        from src.services.build_service import BuildService
        from src.services.resource_service import ResourceService
        from src.services.report_service import ReportService
        from src.services.notification_service import NotificationService
        from src.services.cache_service import CacheService
        from src.services.analytics_service import AnalyticsService
        from src.services.llm_service import LLMService
        from src.services.data_version_service import DataVersionService
        from src.services.world_state_service import WorldStateService
        
        self.player_service = PlayerService(self)
        self.progression_service = ProgressionService(self)
        self.build_service = BuildService(self)
        self.resource_service = ResourceService(self)
        self.report_service = ReportService(self)
        self.notification_service = NotificationService(self)
        self.cache_service = CacheService(self)
        self.analytics_service = AnalyticsService()
        self.llm_service = LLMService(self)
        self.data_version_service = DataVersionService(self)
        self.world_state_service = WorldStateService(self)

