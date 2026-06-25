# Service Layer Specifications (v8.0)

## Overview
The middleware services orchestrate logic between calculation engines, event notifications, import/export interfaces, and data integrity controllers.

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

### 4. `PlayerService`
- Manages the active profile loading, creation, and synchronization.

### 5. `ProgressionService`
- Evaluates account status progression tiers and primary goal indicators.

### 6. `DataVersionService`
- Manages database schema migrations and validates dataset JSON integrity on startup.
- Verifies files compatibility requirements.

### 7. `ImportExportService`
- Direct exports of profile models to JSON and CSV formats.
- Performs profile merge/union calculations and database restorations.
