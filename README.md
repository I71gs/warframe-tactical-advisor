# WARFRAME TACTICAL ADVISOR – Stage 2: Intelligent Progression Coach & Multi-Platform Ecosystem

An advanced progression assistant, tactical coach, and optimization suite for Warframe players. The application guides players from early game to endgame using prioritized recommendations, quest dependency graphing, optimized farming routes, and build analysis.

---

## 🌟 Key Features

### 🧠 Intelligent Progression Coach
- **Goal Planner**: Generates step-by-step custom roadmaps for major game milestones (e.g., *Finish Main Story*, *Unlock Steel Path*, *Become Archon Ready*, *Reach Endgame*).
- **Dependency Engine**: Dynamically analyzes and visualizes prerequisites for items, weapons, and quests (e.g., Mastery Rank, story progress, node unlocking).
- **Farming Routes Planner**: Recommends mathematically optimized progression loops and farming order to minimize grinding efficiency gaps.
- **Intelligent Build Analysis**: Highlights missing core mods/arcanes and outlines upgrade priorities.

### 🎨 Premium Visual Theme System
- **Real-Time Theme Engine**: Compiles and updates stylesheet parameters on the fly without restarts.
- **Cosmic Twilight Default**: Features a gorgeous, high-contrast twilight navy and cosmic violet theme designed for 24/7 visual comfort and high legibility.
- **Built-in Styling Presets**:
  - `Cosmic Twilight` (Default space-violet layout)
  - `Dark` (Standard dark mode)
  - `Light` (High-contrast light mode)
  - `Lotus` (Royal magenta & purple tones)
  - `Corpus` (Deep space blue & amber accents)
  - `Orokin` (Elegant marble white & gold filigree)
  - `Zariman` (Dark emerald & void-teal glow)
- **Custom Theme Extensibility**: Supports loading a customized palette definition file at `src/resources/themes/custom_theme.json`.

### 🩺 Enterprise-Grade Design Polish
- **Healthcare-Grade Sidebar**: Fully redesigned left navigation panel with professional status icons and high-contrast clinical spacing.
- **Enhanced Circular Progress Indicators**: Upgraded radial widgets supporting nested status labels (`READINESS`, `MR XP`) and customizable thickness and color.
- **Clean Visual Hierarchy**: Cohesive card layouts (`QGroupBox`), border rules, spacing, and unified starlight color palettes that elevate the desktop experience.

### 🔄 Live Wiki Database Synchronization
- **Live Sync Engine (`tools/sync_wiki.py`)**: Fetches stats, classifications, passive text, and Helminth skills from live Fandom Wiki Scribunto Lua data modules (`Module:Weapons/data`, `Module:Mods/data`, `Module:Warframes/data`, `Module:Companions/data`).
- **HTML Acquisition Scraper**: Dynamically scans Fandom page parsed HTML for quests, warframes, companions, arcanes, and weapons to verify and import exact drop locations.
- **Background GUI Worker**: Integrates "Sync Database with Wiki" controls in the desktop app's Settings Tab using `QThread` async signals to prevent UI freezes.

### 🌐 Multi-Platform & Extensibility Ecosystem
- **Local REST API**: Hosted at `src/api/app.py` for integration with external tools and third-party dashboards.
- **Web App Interface**: Web client skeleton located in `frontend/web/index.html`.
- **Mobile Frontend**: Flutter-based mobile layout in `frontend/mobile/lib/main.dart`.
- **Extensible Plugin SDK**: Write custom plugins, add custom weapon/build data, or register custom command scripts using the template folder in `plugins/examples/sample_plugin_v3/`. Refer to documentation in `docs/SDK/`.

---

## 📂 Project Structure

- `src/` — Python application source modules
  - `src/core/` — Core calculation engines (Goal Planner, Dependency, Theme, Relics, etc.)
  - `src/gui/` — Rich PySide6 graphical user interface tabs and custom widgets
  - `src/api/` — Local Flask/FastAPI backend API interface
  - `src/services/` — Middleware & orchestrator services (LLM, Cache, Notification, Player context)
  - `src/database/` — SQLite connectivity layer
  - `src/resources/` — Consolidated application resources
    - `src/resources/data/` — Local JSON databases for offline weapons, mods, arcanes, warframes, and quests
    - `src/resources/packs/` — Core progression gear packs
    - `src/resources/routes/` — Farming routes definition JSONs
    - `src/resources/themes/` — Styling JSON stylesheets
- `docs/` — Documentation site and SDK guides
  - `docs/SDK/` — Development kit containing plugin manifests, examples, and API guides
- `frontend/` — Frontend companions
  - `frontend/mobile/` — Flutter-based mobile configuration and source scripts
  - `frontend/web/` — Web application components
- `plugins/` — Custom plugin implementations and templates
  - `plugins/examples/` — Consolidated example plugin files
- `tests/` — Automated test suite with 250+ test cases covering the entire coaching ecosystem
- `tools/` — Developer CLI tools (Wiki Sync engine, theme checkers, build helpers)

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.11+
- Pip package manager

### Installation
1. Clone the repository.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the PySide6 Desktop GUI
```bash
python main.py
```
*or directly as a module:*
```bash
python -m src
```

### 🎮 Overlay HUD Mode
The advisor includes a stays-on-top gameplay HUD overlay designed to stay visible during play.
- **Toggle Overlay**: Press `Ctrl+O` or select **Overlay Mode** from the **Windows** menu to enter Overlay Mode.
- **Drag HUD**: Click and drag the top header bar of the overlay to move it anywhere on the screen.
- **Exit Overlay**: Press `Ctrl+O`, `Esc`, or click the **Restore** button on the overlay to return to the main dashboard.

### Running the API Service
To host the local API endpoint:
```bash
python src/api/app.py
```

### Running Tests
To execute the test verification suite:
```bash
python -m pytest
```

---

## 🧪 Testing Coverage
A complete test suite is available under `tests/` to guarantee execution correctness across:
- Build recommender and simulator systems
- Relic, economy, and weekly objective planners
- Theme manager stylesheet compilation
- Gap analyzers, milestones, and achievements
- MediaWiki queries and sync engine mocking

To run with summary reports:
```bash
python -m pytest -v
```

---

## 📜 Release Notes & Spec
- Refer to [project_spec.md](file:///d:/Shubham/Code/Python/Project/warframe-tactical-advisor/docs/project_spec.md) for full architectural guidelines.
- Refer to [CHANGELOG.md](file:///d:/Shubham/Code/Python/Project/warframe-tactical-advisor/CHANGELOG.md) for details on recent releases.
