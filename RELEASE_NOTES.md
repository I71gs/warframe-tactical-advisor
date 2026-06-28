# Release Notes — Warframe Tactical Advisor v1.0.0

Welcome to the official **v1.0.0** stable release of the Warframe Tactical Advisor companion dashboard platform. This companion provides progression coaching, live world feeds, modding simulations, and an in-game HUD overlay to help optimize your Tenno operations.

---

## 🌟 Feature Highlights

### 🎮 Overlay HUD Mode
Press `Ctrl+O` or select **Overlay Mode** from the Windows menu to trigger the translucent stays-on-top HUD. Keep track of Cetus time cycles, active fissure drop paths, daily objectives, and progression recommendations without having to alt-tab out of Warframe.

### 🧭 Progression Coach & Recommender
Recovers your account's mastery progress and automatically displays critical milestones. The coach recommends:
- Missing junction quest chains and requirements.
- Daily/Weekly objectives sorted by efficiency.
- Time-sensitive operations (weekly Archon Hunts, alerts, visiting traders).

### 📦 Collection Tracker
Track items in your inventory:
- Weapons, Warframes, and Arcanes mastery status.
- Blueprint crafting requirements.
- Automatic MediaWiki synchronization matching standard stats databases.

### 📊 Build Simulator & Mod Library
Simulate mod slots and weapon polarities before spending Forma. Features:
- Mod placement checks.
- Real-time sustained/burst damage per second (DPS) projections.
- Upgrade material checklists.

### 🔌 Extensible Plugin SDK (v3)
Integrate custom tabs and logic easily with the updated Plugin SDK. Build custom extensions in Python and load them dynamically into the sidebar on launch.

---

## 🔧 Resolved Issues in v1.0.0
- **Dynamic CSS Compilation**: Consolidated all sidebar list styles into a dynamic compiler to support dynamic, cohesive color updates when switching visual themes.
- **Settings Defaults**: Added `'use_wiki_gg': True` to the default settings schema.
- **Account Switch event**: Broadcast the `ACCOUNT_SWITCHED` event on Settings Tab save, clearing thread-safe query caches and refreshing data immediately without app restarts.
- **Dashboard Service Crash**: Resolved world state service errors on the main dashboard tab by querying singleton app instances properly.

---

## 📝 Known Issues & Future Plans
- **Windows Installer Compilation**: Built-in ISCC compiler requires Inno Setup 6 to compile `.exe` setup files; otherwise, the application launches as a standalone portable folder under `dist/WarframeTacticalAdvisor/`.
- **Platform Support**: Stable binary compilation is currently tested on Windows 11. Support for Linux/Steam Deck app configurations will follow in future updates.
