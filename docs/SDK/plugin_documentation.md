# Plugins Development Guidelines

Plugins allow you to extend the database of weapons, custom element builds, and even add new interactive command palette callbacks.

## Directory Structure
To register a plugin, create a folder under `src/plugins/` containing:
```
src/plugins/my_custom_plugin/
    ├── manifest.json   (Required: metadata, versions, dependencies)
    ├── weapons.json    (Optional: array of custom weapons)
    ├── builds.json     (Optional: array of custom builds)
    └── commands.py     (Optional: dynamic Python commands)
```

## manifest.json
```json
{
    "id": "sample_custom_arsenal",
    "name": "Sample Custom Arsenal",
    "version": "1.0.0",
    "min_app_version": "6.0.0",
    "description": "Adds custom experimental weapons.",
    "dependencies": []
}
```

## commands.py Callbacks
Define a `register_plugin(registry)` function inside `commands.py` to register custom commands dynamically:
```python
def register_plugin(registry):
    # Adds command visible in Ctrl+P command palette
    registry.register_command(
        "Run Custom Plugin Task",
        lambda: print("Custom command executed successfully!")
    )
```
