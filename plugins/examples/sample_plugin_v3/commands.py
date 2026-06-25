from __future__ import annotations
from typing import Any

def register_plugin(registry: Any) -> None:
    # Register a custom menu using new SDK v3 API
    registry.register_menu("Sample Plugin V3 Menu", [
        {"label": "Test Plugin Command", "action": lambda: print("Sample Command Executed!")}
    ])
    
    # Register a custom settings section using new SDK v3 API
    registry.register_settings_section("Sample Plugin V3 Settings", {
        "enabled": "bool",
        "custom_rate": "int"
    })
    
    # Register a context hook callback
    def pre_load_hook(context_data: Any) -> Any:
        print("Pre-load callback hook activated")
        return context_data
        
    registry.register_context_hook("PRE_LOAD_PROFILE", pre_load_hook)
