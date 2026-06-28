# Changelog

## [11.0.0] - 2026-06-28

### Added
- **Sidebar Navigation Layout**: Modern vertical split navigation sidebar replacing horizontal tabs.
- **Circular Dashboard Widgets**: PySide6 custom CircleProgress indicators highlighting Mastery XP and Readiness metrics.
- **Fuzzy Search Integration**: CommandPaletteDialog now utilizes SearchEngineV3 for fuzzy matches.
- **Build Planner Upgrades**: Professional 8-slot Mod grid and integrated Arcane / Exilus slots in BuildSimulatorTab.
- **Setup Wizard Dialog**: First-run multi-page guide setup for MR parameters and initial profile imports.
- **Cache Manager Layer**: Thread-safe QueryCache with TTL reducing SQLite database transaction latency.
- **Developer & User Guides**: Dynamic guides detailing architecture diagrams and keyboard shortcut lists.
- **250+ Automated Test Suite**: Parametrized tests raising test suite footprint to 257 passing tests.

## [10.0.0] - 2026-06-28


### Added
- **Multi-Category Collection Tracker**: Integrated 10 new SQLite inventory tables, schema version 2 database migration, and a multi-tabbed interactive collection UI.
- **Relic Planner**: Fully loaded offline drop-table planner with expected-run probability calculations and multi-item planner lists.
- **Resource Deficits & Goal Calculator**: Added dynamic goal costs breakdown (Wisp, Saryn, Voidrig...) and active resource booster tips.
- **4-Column Dashboard Command Center**: Integrated daily objective lists, live world-state feeds, and active economy trackers.
- **Curated Weapon Build Scenarios**: Loaded standard templates side-by-side with user config editors for 6 primary game modes.
- **Double Radar Chart Comparison**: Matplotlib-based profile overlay analyzer mapping 9 dimensions of progression.
- **Version Sniffer & Patch Tracker**: Shows latest Warframe changelogs compared against last seen session version.
- **Fuzzy Search & Bookmarks**: Custom matching using difflib, search history, and favorites list.
- **DevOps Data Pipeline**: Python script utility for reloading, validating, and updating schemas.
- **Automated Actions CI/CD**: Workflow action for packaging with PyInstaller and running tests on tag releases.
- **Structured Telemetry Diagnostics**: Structured JSON format error logs on crash.

## [1.0.0] - Release


### Added

- Application entrypoint via `main.py` and `src/__main__.py`
- Main dashboard, profile, recommendations, progression, readiness, and build advisor UI tabs
- Persistent settings and database backup support
- Offline JSON data loading for Warframes, weapons, mods, arcanes, and quests
- About dialog and help menu integration
- PySide6 desktop application shell
- SQLite schema versioning and profile persistence
- Project documentation and basic test coverage
