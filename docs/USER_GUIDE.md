# Warframe Tactical Advisor — User Guide

Welcome to the Warframe Tactical Advisor v11.0 Companion Platform.

## Core Features

- **Modern Navigation**: Navigate tabs using the clean left sidebar list.
- **Unified Command Palette (Ctrl+K)**: Toggle the floating dialog to search all weapons, mods, arcanes, quests, and run setup tasks.
- **Build Planner & Simulator**: Simulate mods placement, view estimated sustained DPS, check missing upgrade requirements, and optimize polarities.
- **Relic & Economy Planners**: Calculate drops, trace resource farming nodes, and set booster alerts.

---

## Global Keyboard Shortcuts

| Shortcut | Action Description |
|---|---|
| `Ctrl+K` or `Ctrl+P` | Opens Unified Command Palette search dialog |
| `Ctrl+R` | Reloads / Refreshes all active dashboard panels |
| `Ctrl+S` | Saves current profile modifications |
| `Ctrl+I` | Opens Import Profile dialog wizard |
| `Ctrl+E` | Exports current profile to backup JSON |
| `Ctrl+F` | Focuses quest input field inside Profile tab |

---

## Troubleshooting FAQ

### How do I switch accounts?
- Open the Command Palette (`Ctrl+P`) and type `Command: Switch Account to Alt` or `Command: Switch Account to Default`.

### Where are SQLite databases and backups saved?
- Profiles are saved locally to `warframe.db`. Creating backups publishes backup paths to the status bar (e.g., `backup_yyyyMMdd.db`).
