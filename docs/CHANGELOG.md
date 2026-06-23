# Changelog

All notable changes to this project will be documented in this file.

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
