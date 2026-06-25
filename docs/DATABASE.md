# Database Schema & Storage (v8.0)

## Overview
All player profile progression, owned items, completed quests, system settings, history snapshots, and session productivity records are stored offline locally. 
Database files are located at the root of the workspace directory.

## File Mappings
- **Active Database**: `player.db` (or `player_{profile}.db` for custom profile names).
- **Settings Store**: `settings.json`.
- **Resource Inventory**: `resource_state.json`.
- **Daily snapshots directory**: `snapshots/YYYY-MM-DD.json`
- **Session Logs**: `snapshots/session_logs.json`
- **Dataset metadata**: `data/metadata.json`

## SQLite Schema Details

### 1. `players`
Stores overall player flags and levels.
- `id` (INTEGER, Primary Key)
- `mastery_rank` (INTEGER)
- `steel_path_unlocked` (INTEGER - Boolean 0/1)
- `arbitrations_unlocked` (INTEGER - Boolean 0/1)
- `helminth_unlocked` (INTEGER - Boolean 0/1)

### 2. `completed_quests`
- `id` (INTEGER, Primary Key)
- `quest_name` (TEXT, Unique)

### 3. `owned_mods`
- `id` (INTEGER, Primary Key)
- `mod_name` (TEXT, Unique)

### 4. `owned_arcanes`
- `id` (INTEGER, Primary Key)
- `arcane_name` (TEXT, Unique)

### 5. `owned_weapons`
- `id` (INTEGER, Primary Key)
- `weapon_name` (TEXT, Unique)

### 6. `metadata`
Key-value storage for schema configurations.
- `key` (TEXT, Primary Key)
- `value` (TEXT)

## Database Backups & Snapshots
- **Backups**: Automatically saved under `backups/` directory. File naming format: `player_backup_YYYYMMDD_HHMMSS.sqlite`.
- **Progress Snapshots**: Daily state captures are recorded in the `snapshots/` folder in structured JSON formatting, supporting historical timeline reconstructs and progress comparisons.
