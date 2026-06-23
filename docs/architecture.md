# Architecture Specifications (v7.0)

## Overview
Warframe Tactical Advisor is structured as an offline-first desktop application built on top of the PySide6 (Qt) framework. The system coordinates real-time progression scoring, custom plugin expansions, local SQLite database transactions, and unified search logic.

```
                  ┌───────────────────────┐
                  │      MainWindow       │
                  └───────────┬───────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
     ┌──────────────┐ ┌──────────────┐ ┌───────────────┐
     │  CodexTab    │ │  SearchTab   │ │  BenchmarkTab │
     └──────┬───────┘ └──────┬───────┘ └───────┬───────┘
            │                │                 │
            ▼                ▼                 ▼
   ┌─────────────────┬────────────────┬────────────────┐
   │   CodexEngine   │ SearchEngineV3 │BenchmarkEngine │
   └────────┬────────┴────────────────┴────────┬───────┘
            │                                  │
            └────────────────┬─────────────────┘
                             ▼
                    ┌─────────────────┐
                    │ DatabaseManager │
                    └─────────────────┘
```

## Folder Layout
- `src/core/`: Calculators and engines (Scoring, Goals, ThemeManager, PluginRegistry, SearchEngineV3).
- `src/gui/`: Application main view window and modular tab widgets.
- `src/services/`: Services orchestrator coordinating middleware actions.
- `src/api/`: Local FastAPI service hosting REST API endpoints.
- `plugins/`: Directory holding third-party plugins.
- `themes/`: Theme files (Dark, Light, Lotus, Corpus, Orokin, Zariman).
- `docs/`: Product architecture, guides, and specifications.

## Application Lifecycle
1. **Bootstrap**: Exception handlers are registered, settings are loaded, and the `AppContext` singleton is instantiated.
2. **Worker Pool (Dynamic Plugin Scanning)**: Background `PluginWorker` scans the root `plugins/` directory. All matching manifests are validated and loaded.
3. **UI Generation**: The main `MainWindow` setup instantiates all standard tabs and queries `PluginRegistry` to dynamically register any tab extensions.
4. **Active Stylesheet Mapping**: Active theme parameters are read from the settings, compiled dynamically through `ThemeEngine`, and bound to the application window instance.
5. **Periodic Optimization**: A loop refresh timer runs every 3 minutes to update progression scores and reload databases.
