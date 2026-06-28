# Product Roadmap — Version 1.x Transition Strategy

This document outlines the transition of the Warframe Tactical Advisor from major system additions into a focused **v1.x maintenance, polish, and iteration loop**. Future development prioritizes stability, community-driven usability, performance, and keeping data in sync with live Warframe updates.

---

## 🚫 Out of Scope (What We Will NOT Build)
To preserve application performance and maintainability, we will avoid adding redundant system complexities:
- ❌ New planner tabs
- ❌ Additional analytics or simulation engines
- ❌ Parallel recommendation rules
- ❌ Generic statistics counters
- ❌ External AI integrations

---

## 📅 Roadmap Phases

### Phase A — Public Release (Highest Priority)
1. **GitHub Polish**:
   - High-quality professional `README.md`
   - UI Feature GIFs and Screenshots
   - Clear architectural diagrams
   - FAQ, Troubleshooting, and standard bug report templates
2. **Release Assets**:
   - `WarframeTacticalAdvisor_v1.0.0_Setup.exe` (Windows Installer)
   - `WarframeTacticalAdvisor_Portable.zip` (Standalone portable package)
   - `SHA256.txt` (Integrity hashes)
   - `Release Notes.pdf`
3. **GitHub Release (v1.0.0)**:
   - Create official release tag highlighting: **Overlay HUD**, **Progression Coach**, **Collection Tracker**, **World State**, **Build Simulator**, and **Plugin SDK**.
4. **Single-Page Landing Website**:
   - Hero copy, core features, UI screenshots, downloads link, documentation index, and Discord / GitHub links.

### Phase B — Professional Polish
- **Empty States**: Replace blank screens with actionable guides (e.g. `No Profile Found. Import your profile to begin tracking progression. [Import Profile]`).
- **Loading Indicators**: Replace freezing screens with async loaders showing step-by-step progress (e.g. `Loading Mods`, `Loading Weapons`, `Loading World State`).
- **Micro-Animations**: Add subtle visual transitions (fades, sidebar sliding, progress bar fills, notification toasts, and chart updates).
- **Custom Iconography**: Swap out standard system/Qt icons with a curated, cohesive icon set matching the Cosmic Twilight navy and violet aesthetic.

### Phase C — User Experience (UX) Observational Audits
- Conduct UX audits watching real users navigate the companion.
- Identify hidden buttons, confusing labels, and high-click count workflows to simplify user layouts.

### Phase D — Performance Optimizations
Aim for the following telemetry targets:
- **Startup Latency**: < 2.0 seconds
- **Fuzzy Search Latency**: < 50 milliseconds
- **Theme Switching**: < 100 milliseconds
- **SQLite Latency**: Minimize database round-trips via QueryCache.

### Phase E — Community Engagement
- Launch dedicated community hubs: Discord server and GitHub Discussions.
- Provide structured bug templates and feature request formats to triage community feedback.

### Phase F — Live Warframe Content Updates (Long-Term maintenance)
Implement standard data syncs for new game updates:
- New weapons & Warframes
- New quests & resources
- New Incarnon evolutions
- Balance changes and seasonal event databases
