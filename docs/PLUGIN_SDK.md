# Plugin SDK Developer Guide (v7.0)

## Overview
The WTA Plugin SDK 2.0 allows developers to extend the application's capabilities by writing plugins located under the root `plugins/` folder.

## Folder Directory Structure
```
plugins/
└── my_custom_plugin/
    ├── manifest.json
    ├── weapons.json
    ├── builds.json
    ├── routes.json
    ├── theme.json
    └── commands.py
```

## Specification Configuration

### 1. `manifest.json`
Specifies name, author, version, dependencies, and target compatibility limits.
```json
{
  "name": "My Custom Plugin",
  "author": "Developer Name",
  "version": "1.0.0",
  "dependencies": [],
  "minimum_wta_version": "7.0"
}
```

### 2. `weapons.json`
Specifies a list of custom weapons.
```json
[
  {
    "name": "Custom Sword",
    "type": "Melee",
    "acquisition": "Assassination Node",
    "meta_rating": 80,
    "category": "Sword"
  }
]
```

### 3. `builds.json`
Specifies a list of custom modding builds.
```json
[
  {
    "weapon": "Custom Sword",
    "mods": ["Serration", "Organ Shatter"],
    "arcane": "None",
    "element": "Slash",
    "rating": 85
  }
]
```

### 4. `routes.json`
Specifies a list of custom farming routes.
```json
[
  {
    "weapon": "Custom Sword",
    "source": "Neptune Assassination",
    "estimated_time": "2 hours"
  }
]
```

### 5. `theme.json`
Defines a custom theme.
```json
{
  "name": "My Custom Theme Colors",
  "PRIMARY": "#050e14",
  "SECONDARY": "#0b1822",
  "ACCENT": "#00ffcc",
  "TEXT": "#e2f1f5",
  "MUTED": "#61889c",
  "CARD": "#102534"
}
```

### 6. `commands.py`
Executes Python scripts. Must contain a `register_plugin(registry)` callback function.
```python
import PySide6.QtWidgets as QtWidgets

def register_plugin(registry) -> None:
    # Register custom action command in VSCode command palette
    def my_action():
        print("Hello from plugin script!")
    registry.register_command("Custom: Run Plugin Script", my_action)

    # Register a new custom GUI tab
    class CustomTab(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()
            QtWidgets.QLabel("Sample Custom Tab Widget", self)
    registry.register_tab(CustomTab, "My Plugin Tab")
```
