# WARFRAME TACTICAL ADVISOR v1.0 Offline Edition

A desktop advisor for Warframe progression, build recommendations, and resource planning.
This project is built in Python using PySide6 and ships with offline JSON game data.

## Features

- Offline Warframe, weapon, mod, quest, and arcane data
- Profile persistence with SQLite
- Quest planning, progression advice, and readiness analysis
- Build and loadout recommendations
- Settings persistence and database backup support
- About dialog and menu-driven application shell

## Installation

1. Install Python 3.11+.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running the app

```bash
python main.py
```

or as package:

```bash
python -m src
```

## Testing

A small `pytest`-based verification test suite is included.

```bash
python -m pip install pytest
python -m pytest -q
```

## Project structure

- `src/` — application source modules
- `data/` — offline game data JSON files
- `player.db` — local SQLite database storage
- `backups/` — database backups
- `docs/` — architecture and project specification

## Release notes

See `CHANGELOG.md` for the current release summary.
