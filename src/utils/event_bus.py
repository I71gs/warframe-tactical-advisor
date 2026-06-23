from __future__ import annotations
from typing import Any, Callable
from PySide6.QtCore import QObject, Signal, Slot
from src.utils.logger import logger

class EventBusSignal(QObject):
    event_fired = Signal(str, dict)

class EventBus:
    """Thread-safe publish-subscribe Event Bus utilizing PySide6 signal mechanics."""
    _instance: EventBus | None = None

    def __new__(cls) -> EventBus:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_bus()
        return cls._instance

    def _init_bus(self) -> None:
        self.notifier = EventBusSignal()
        self.subscribers: dict[str, list[Callable[[dict[str, Any]], None]]] = {}
        self.notifier.event_fired.connect(self._dispatch)

    def subscribe(self, event_type: str, callback: Callable[[dict[str, Any]], None]) -> None:
        """Register a callback for a specific event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.debug("Subscribed to event: %s", event_type)

    def publish(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        """Publish an event to the bus. Safe to invoke from background threads."""
        payload = data or {}
        self.notifier.event_fired.emit(event_type, payload)

    @Slot(str, dict)
    def _dispatch(self, event_type: str, data: dict[str, Any]) -> None:
        """Internal dispatcher executed on the UI main thread."""
        callbacks = self.subscribers.get(event_type, [])
        for cb in callbacks:
            try:
                cb(data)
            except Exception as exc:
                logger.error("Error executing callback for event %s: %s", event_type, exc)
