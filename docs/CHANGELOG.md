# Changelog

All notable changes to this project will be documented in this file.

## [8.0.0] - Ecosystem, Analytics & Multi-Platform Edition (v8.0)

### Added
- **Data Versioning System**: Integrated `DataVersionService` to manage database schema updates, verify file dependencies, and track data integrity versioning.
- **Progress Snapshotting**: Snapshot repository serialization for saving daily states as JSON; computes differences between historical snapshots.
- **Progression Timeline Replays**: Historical replay engine reconstructing milestones unlock speeds and velocity telemetries.
- **Statistics Engine v2**: Advanced analytics compiling growth curves, story and weapon clearance stats, and mod/build scores.
- **Goal History & Session Analytics**: Logged session durations, task completions, resource yields, and daily productivity efficiency.
- **Search Engine v4**: Custom synonym lookup (`aliases.json`) and category tag index (`tags.json`) integration with relevance rank boosts.
- **Wiki Launcher**: Browser automation opening warframe.wiki.gg and fandom.com entries.
- **Detached Multi-Windows**: `WindowManager` ensuring zero-duplicate sub-window frames for Dashboard, Codex, Charts, and Graphs.
- **Import/Export Service**: Standardized profile data exports to JSON and CSV formats, profile merge/union logic, and db restorations.
- **FastAPI Endpoint Extensions**: Added `/charts`, `/codex`, and `/statistics` REST API routes.
- **Flutter Companion Stub**: Flutter companion skeleton displaying progress metrics, daily checklist tasks, and session duration selections.

## [7.0.0] - Stage 2: Intelligent Progression Coach & Plugins Ecosystem

### Added
- **Intelligent Progression Coach**: Incorporates a step-by-step goal planner, prerequisite dependency engines, and farming routes optimizer.
- **Visual Theme Engine Complete**: Integrates preset presets (Lotus, Corpus, Orokin, Zariman) loaded dynamically from JSON files, and supports user customization templates.
- **Plugin SDK 2.0**: Marketplace layout folder structured at the root `plugins/` path supporting custom commands, tab extensions, themes, builds, weapons, and routes.
- **Search Engine v3**: Relevance scoring logic with specific keywords boosts (Phenmor, Steel Path, Wisp, etc.).
- **Encyclopedia / Codex**: Extensive database tab detail showing variants, incarnons, ability maps, helminth, and farming locations.
- **Interactive Graph Visualizations**: Renders clickable tree layout maps showing quest dependencies.
- **Benchmark Engine**: Evaluation tool comparing stats against MR tiers.
- **Service Telemetry**: Real-time DB latencies, cache metrics, and startup speeds tracked in `performance_report.json`.
- **CI/CD Checks**: Ruff checks, black formatting, type-safety, and coverage limits.
- **Windows Executable Setup**: Inno Setup script to generate installers.
- **Documentation Suite**: Added ARCHITECTURE.md, DATABASE.md, SERVICES.md, PLUGIN_SDK.md, API.md, USER_GUIDE.md, DEVELOPER_GUIDE.md, and ROADMAP.md.

## [1.0.0] - Release
- Initial release with offline game data, profile persistence, dashboard metrics, and settings backup support.
