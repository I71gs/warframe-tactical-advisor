# Service Layer Specifications (v7.0)

## Overview
The middleware services orchestrate logic between calculation engines, natural language helpers, event notifications, and persistence.

## Core Services

### 1. `NotificationService`
- Manages real-time visual banners and UI feedback messages.
- Subscribes to the `"NOTIFICATION"` topic and runs custom toast alerts via `show_toast`.
- Exposes `notify(message, level)` helper.

### 2. `AnalyticsService`
- Tracks session interactions such as tab views (`track_tab_view`) and goal adjustments.
- Outputs analytics records locally for diagnostic analysis.

### 3. `CacheService`
- In-memory data cache backed by a JSON file (`app_cache.json`).
- Supports time-to-live (TTL) expiration limits for queries.
- Evicts volatile cache items upon receiving the `"PROFILE_UPDATED"` event.

### 4. `LLMService`
- Interfaces with local Ollama endpoints (default model: `gemma:2b`).
- Dynamically injects context (MR level, owned items, completed quests) into query prompts before execution.

### 5. `PlayerService`
- Manages the active profile loading, creation, and synchronization.

### 6. `ProgressionService`
- Evaluates account status progression tiers and primary goal indicators.
