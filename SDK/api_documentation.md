# REST API Reference

The developer platform runs a FastAPI service locally. Run the server using:
```bash
uvicorn src.api.app:app --reload
```

## Endpoints

### 1. Get Player Profile
`GET /profile`
* **Response**: Returns mastery rank, completed quests, and owned items.

### 2. Personal Recommendations
`GET /recommendations`
* **Response**: Returns list of personalized build targets.

### 3. Star Chart Progression
`GET /progression`
* **Response**: Returns aggregate readiness scores and stage descriptors.

### 4. Custom AI Coach
`GET /advisor?q=What should I do tonight?`
* **Response**: Returns task checklist, ETA, and expected power gains.
