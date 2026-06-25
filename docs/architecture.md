# Architecture Specifications (v8.0)

## Overview
Warframe Tactical Advisor is structured as an offline-first desktop application built on top of the PySide6 (Qt) framework. The system coordinates real-time progression scoring, custom plugin expansions, local SQLite database transactions, timeline playback replays, and unified search logic.

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
- `src/core/`: Calculators and engines (Scoring, Replays, Snapshots, StatisticsEngineV2, SessionAnalytics, EconomyEngine, WindowManager).
- `src/gui/`: Application main view window, detached sub-window frames, and modular tab widgets.
- `src/services/`: Services orchestrator coordinating middleware actions (ImportExportService, DataVersionService).
- `src/api/`: Local FastAPI service hosting REST API endpoints.
- `plugins/`: Directory holding third-party plugins.
- `themes/`: Preset theme templates (Lotus, Corpus, Orokin, Zariman).
- `mobile/`: Flutter companion stub for mobile connectivity.
- `docs/`: Product architecture, guides, and specifications.

## Application Lifecycle & Analytics Pipeline
1. **Bootstrap**: Exception handlers are registered, settings are loaded, and the `AppContext` singleton is instantiated.
2. **Data Integrity Check**: `DataVersionService` validates SQLite datasets and runs schema migrations.
3. **Worker Pool (Dynamic Plugin Scanning)**: Background `PluginWorker` scans `plugins/` directories to load custom commands, tab extensions, themes, and builds.
4. **UI Generation**: The main `MainWindow` setup instantiates standard tabs, detached sub-window controls via `WindowManager`, and dynamically registers plugin tabs.
5. **Periodic Optimization & Profiling**: A loop refresh timer runs every 3 minutes, executing tab refreshes, tracking execution latency in `Profiler`, and saving performance telemetry.
6. **Shutdown**: On `closeEvent`, the application window settings are saved, and the `SnapshotRepository` automatically creates a daily state snapshot.
