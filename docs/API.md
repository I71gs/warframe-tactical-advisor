# Local REST API Specifications (v7.0)

## Overview
The application hosts a local developer-friendly FastAPI backend endpoint to query player profile states, check recommendations, and trigger commands.

- **Execution Script**: `python src/api/app.py`
- **Default Port**: `http://localhost:8000`
- **Auto-generated Docs**: Swagger UI available at `http://localhost:8000/docs`

## Endpoints

### 1. `GET /profile`
Returns the active player's profile data, mastery level, and owned items inventory.
- **Response Schema**:
  ```json
  {
    "mastery_rank": 12,
    "completed_quests": ["The Second Dream"],
    "owned_mods": ["Serration"],
    "owned_arcanes": [],
    "owned_weapons": ["Laetum"],
    "steel_path_unlocked": false,
    "arbitrations_unlocked": false,
    "helminth_unlocked": false
  }
  ```

### 2. `GET /recommendations`
Returns dynamic recommendations for weapon builds and loadouts.

### 3. `GET /progression`
Returns aggregate readiness scores and primary goal milestone indicators.

### 4. `GET /builds`
Returns all cached meta builds. Optional query filter `?weapon=Phenmor`.

### 5. `GET /search`
Performs global database search filtering by string.
- **Parameters**: `q` (string, required)

### 6. `GET /resources`
Returns owned resource stockpiles from `resource_state.json`.

### 7. `GET /advisor`
Returns custom progress coaching advice.
- **Parameters**: `q` (string, required)

### 8. `GET /sim`
Runs future projection simulations.
