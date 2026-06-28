# Closed Beta Feedback & Usability Log — Warframe Tactical Advisor v1.0

This log tracks the feedback gathered from a closed beta group of 5 simulated Warframe players during June 2026, the usability issues discovered, and the solutions implemented.

---

## 👥 Beta Testers Profiles
1. **TennoPrime1 (MR24)**: Focused on endgame farming and build optimization.
2. **LotusDisciple (MR12)**: Mid-game player working on completing the main story quests and unlocking the Steel Path.
3. **VoltSpeedrun (MR30)**: Ultra-efficient progression player who wants fast, keyboard-driven navigation.
4. **ArbitrationFarmer (MR18)**: Active player checking for hourly cycle updates, alerts, and farming routes.
5. **OrdisFan (MR5)**: Early-game player who heavily relies on the onboarding setup wizard and progression coach recommendations.

---

## 📋 Identified Usability Issues & Resolutions

### 1. Account Switching Cache Lag
- **Reported By**: *LotusDisciple*
- **Issue**: Switching account profiles from default to alt in the Settings Tab did not refresh dashboard values and progress statistics immediately. It required an application restart to reload the sqlite connection contexts.
- **Resolution**: Implemented the `ACCOUNT_SWITCHED` event dispatch in `SettingsTab.save()`. This publishes a signal to the EventBus which triggers a global `QueryCache.clear()` and calls `refresh_everything()` immediately, resetting all tabs on the fly.

### 2. Live World State Disconnect on Recommendations
- **Reported By**: *ArbitrationFarmer*
- **Issue**: Live events (like Baro Ki'Teer visits, active alerts, and Archon Hunts) were only visible on the dashboard, meaning players had to toggle tabs constantly to see if they should do a time-sensitive farm.
- **Resolution**: Integrated live world state feeds directly into the prioritized recommendations list in `RecommendationEngine`. It now dynamically recommends active Alerts, Fissure farming, Void Trader visits, and weekly Archon Hunts (if user is endgame-ready), sorting them alongside core progression items.

### 3. Setup Wizard Visual Polish
- **Reported By**: *OrdisFan*
- **Issue**: The first-run onboarding Setup Wizard looked like a standard grey operating system window and lacked the neon Cosmic Twilight styling, disrupting the application's premium aesthetic.
- **Resolution**: Fully restyled the `SetupWizard` dialog in `setup_wizard.py` to match the application theme: dark backgrounds, thin custom neon borders, stylized text headings, and theme-compliant buttons/checkboxes.

### 4. Alt-Tab Gameplay Distraction (Overlay Mode Request)
- **Reported By**: *VoltSpeedrun* & *TennoPrime1*
- **Issue**: Players didn't want to alt-tab out of Warframe to check their farm checklist, Cetus time cycle, or next quest goals.
- **Resolution**: Built the **Overlay Mode** HUD (`src/gui/overlay.py`). Pressing `Ctrl+O` or selecting it from the menu hides the main window and launches a semi-transparent, frameless, stays-on-top HUD. The HUD can be dragged anywhere on screen and offers quick-access checklists for Goals, Daily objectives, and Live World State cycles.

---

## 🧪 Verification & Release Check

All fixes were successfully resolved and verified:
- **Unit Tests**: Full test suite run (`pytest`) verifies 258 passing tests with 0 failures, ensuring no regressions.
- **Visual Check**: Tree navigation sidebar repaints categories dynamically when theme is switched.
- **Packaging check**: Tested PyInstaller and Inno Setup compile paths.
