# Warframe Tactical Advisor – Project Overview

Warframe Tactical Advisor is a desktop application built in Python using PySide6 that acts as a personalized progression assistant for the game Warframe.

The purpose of the project is to help players understand what they should do next, what they are missing, and how to efficiently progress from early game to endgame.

## Core Philosophy

Instead of simply storing player data, the application behaves like a tactical coach:

* Analyze the player's account.
* Determine current progression stage.
* Detect missing quests, mods, arcanes, and weapons.
* Prioritize recommendations.
* Generate step-by-step goals.
* Guide the player toward endgame readiness.

Everything works offline using local JSON databases and SQLite, with optional Warframe Wiki links for additional information.

---

# Technology Stack

* Python
* PySide6 GUI
* SQLite
* JSON knowledge bases
* PyInstaller executable packaging
* Git + GitHub version control

---

# Current Features

### Profile System
Stores:
* Mastery Rank
* Completed quests
* Owned mods
* Owned arcanes
* Owned weapons
* Steel Path status

### Recommendation Engine
Generates prioritized recommendations based on:
* Story progression
* Missing mods
* Missing arcanes
* Missing weapons
* Current account stage

Categories:
* STORY
* MOD
* ARCANE
* WEAPON
* ENDGAME
* PROGRESSION

---

### Progression Engine
Determines:
* Early Game
* Mid Game
* Late Game
* End Game

Calculates:
* Story completion %
* Mod completion %
* Arcane completion %
* Weapon completion %
* Overall readiness score

---

### Quest Planner
Shows:
* Current story path
* Next available quests
* Recommended roadmap

---

### Readiness Analyzer
Checks readiness for:
* The New War
* Steel Path
* Archon Hunts

Reports missing requirements.

---

### Build Advisor
Suggests builds and evaluates account strength.

---

### Loadout Advisor
Analyzes owned weapons and selects:
* Best Primary
* Best Secondary
* Best Melee

Shows strengths and weaknesses.

---

### Dashboard
Displays:
* Account stage
* Readiness score
* Story completion
* Mod completion
* Arcane completion
* Weapon completion
* Top recommendation

---

### Knowledge Base
Searchable databases for:
* Weapons
* Mods
* Arcanes

Includes wiki links.

---

### Statistics
Shows:
* Collection totals
* Completion percentages
* Account progress

---

### Settings System
Supports:
* Dark theme
* Auto refresh
* Window persistence
* Selected tab persistence
* Backups

---

### Data Persistence
Uses:
* SQLite database
* JSON files
* Automatic backups
* Settings manager

---

### Executable Distribution
Packaged with PyInstaller into a standalone Windows executable.

---

# Stage 1 Status
Stage 1 is complete and stable.
The application functions as an offline tactical progression assistant.

---

# Stage 2 Goal
Transform the application from a recommendation viewer into an intelligent progression planner.

New systems being developed:

### Goal Planner
Generate step-by-step plans for goals such as:
* Finish Main Story
* Unlock Steel Path
* Become Archon Ready
* Reach Endgame

### Dependency Engine
Show prerequisites for recommendations.
Example:
`Acquire Phenmor` requires:
* Angels of Zariman
* MR14
* Zariman access

### Farming Planner
Generate optimized farming paths.
Example:
* Goal: `Steel Path Ready`
* Farm Order:
  1. Arbitrations → Galvanized Mods
  2. Steel Path → Primary Merciless
  3. Zariman → Phenmor

### Intelligent Build Analysis
Show:
* Missing mods
* Missing arcanes
* Potential weapon power
* Upgrade priorities

### Account Coach
Eventually the application should function like an AI companion for Warframe that continuously answers:
> "Given my account, what should I do next and why?"

---

**In one sentence:**
> Warframe Tactical Advisor is a Python + PySide6 desktop application that acts as a personalized Warframe progression coach, analyzing a player's account and generating intelligent recommendations, roadmaps, and endgame preparation plans.
