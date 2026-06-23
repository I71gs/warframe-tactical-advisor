# WARFRAME TACTICAL ADVISOR – Stage 2: Intelligent Progression Coach & Multi-Platform Ecosystem

An advanced progression assistant, tactical coach, and optimization suite for Warframe players. The application guides players from early game to endgame using prioritized recommendations, quest dependency graphing, optimized farming routes, and build analysis.

---

## 🌟 Stage 2 Features

### 🧠 Intelligent Progression Coach
- **Goal Planner**: Generates step-by-step custom roadmaps for major game milestones:
  - *Finish Main Story*
  - *Unlock Steel Path*
  - *Become Archon Ready*
  - *Reach Endgame*
- **Dependency Engine**: Dynamically analyzes and visualizes prerequisites for items, weapons, and quests (e.g., Mastery Rank, story progress, node unlocking).
- **Farming Routes Planner**: Recommends mathematically optimized progression loops and farming order to minimize grinding efficiency gaps.
- **Intelligent Build Analysis**: Highlights missing core mods/arcanes and outlines upgrade priorities.

### 🎨 Premium Visual Theme System
- **Real-Time Theme Engine**: Compiles and updates stylesheet parameters on the fly without restarts.
- **Built-in Styling presets**:
  - `Dark` (Standard dark mode)
  - `Light` (High-contrast light mode)
  - `Lotus` (Royal magenta & purple tones)
  - `Corpus` (Deep space blue & amber accents)
  - `Orokin` (Elegant marble white & gold filigree)
  - `Zariman` (Dark emerald & void-teal glow)
- **Custom Theme Extensibility**: Supports loading a customized palette definition file at `themes/custom_theme.json`.

### 🌐 Multi-Platform & Extensibility Ecosystem
- **Local REST API**: Hosted at `src/api/app.py` for integration with external tools and third-party dashboards.
- **Web App Interface**: Web client skeleton located in `web/index.html`.
- **Mobile Frontend**: Flutter-based mobile layout in `mobile/lib/main.dart`.
- **Extensible Plugin SDK**: Write custom plugins, add custom weapon/build data, or register custom command scripts using the template folder in `SDK/examples/sample_plugin/`. Refer to documentation in `SDK/`.

---

## 📂 Project Structure

- `src/` — Python application source modules
  - `src/core/` — Core calculation engines (Goal Planner, Dependency, Theme, Relics, etc.)
  - `src/gui/` — Rich PySide6 graphical user interface tabs and custom widgets
  - `src/api/` — Local Flask/FastAPI backend API interface
  - `src/services/` — Middleware & orchestrator services (LLM, Cache, Notification, Player context)
  - `src/database/` — SQLite connectivity layer
- `SDK/` — Development kit containing plugin manifests, examples, and API guides
- `mobile/` — Flutter-based mobile configuration and source scripts
- `web/` — Web application components
- `data/` — Local JSON databases for offline weapons, mods, arcanes, and progression metrics
- `tests/` — Automated test suite with 60+ test cases covering the entire coaching ecosystem

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

To run with summary reports:
```bash
python -m pytest -v
```

---

## 📜 Release Notes & Spec
- Refer to [project_spec.md](file:///d:/Shubham/Code/Python/Project/warframe-tactical-advisor/docs/project_spec.md) for full architectural guidelines.
- Refer to [CHANGELOG.md](file:///d:/Shubham/Code/Python/Project/warframe-tactical-advisor/CHANGELOG.md) for details on recent releases.
