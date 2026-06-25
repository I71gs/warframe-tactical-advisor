from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SDK_DIR = ROOT / "docs" / "SDK"

README_CONTENT = """# Warframe Tactical Advisor Developer SDK

Welcome to the Developer SDK for Warframe Tactical Advisor v6.0. This SDK contains the tools, examples, and documentation required to build custom plugins, integrate external apps using our REST API layer, and extend the progression advice systems.

## Architecture Topology

```mermaid
graph TD
    UI[PySide6 UI Views] -->|Events/Queries| Core[Core Advisor Engine]
    FastAPI[FastAPI REST API Server] -->|Queries| Core
    Core -->|Service calls| Services[Services Layer: Player, Build, Resource]
    Services -->|Inference checks| ExpertSystem[Expert System Inference Engine]
    Services -->|Semantic links| KnowledgeGraph[Knowledge Graph Adjacency Net]
    Services -->|Local LLM| Ollama[Local Ollama REST API]
    Core -->|Dynamic loaders| Plugins[Third-Party Plugins Registry]
```

## Contents
* [plugin_documentation.md](plugin_documentation.md) - Learn how to build directory-structured marketplace plugins.
* [api_documentation.md](api_documentation.md) - Integration documentation for the local REST API server.
* `examples/sample_plugin` - A complete sample plugin implementing custom weapons, builds, and commands.
"""

PLUGIN_DOCS = """# Plugins Development Guidelines

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
"""

API_DOCS = """# REST API Reference

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
"""

SAMPLE_MANIFEST = {
    "id": "sample_ext_arsenal",
    "name": "Sample Extended Arsenal",
    "version": "1.0.0",
    "min_app_version": "6.0.0",
    "description": "Developer SDK sample weapons and command hooks.",
    "dependencies": []
}

SAMPLE_WEAPONS = [
    {
        "name": "Soma Prime",
        "type": "Primary",
        "acquisition": "Relics / Prime Vault",
        "meta_rating": 80,
        "category": "Rifle"
    }
]

SAMPLE_BUILDS = [
    {
        "weapon": "Soma Prime",
        "mods": ["Serration", "Split Chamber", "Point Strike", "Vital Sense", "Hunter Munitions"],
        "arcane": "Primary Merciless",
        "element": "Slash Viral",
        "rating": 82
    }
]

SAMPLE_COMMANDS = """def register_plugin(registry):
    def test_cmd():
        print("SDK Sample command triggered!")
        
    registry.register_command("Developer SDK: Trigger Test", test_cmd)
"""

class SDKGenerator:
    """Generates a complete developer SDK kit and plugin examples."""

    def generate_sdk(self) -> None:
        """Create directories and populate template code files."""
        SDK_DIR.mkdir(parents=True, exist_ok=True)
        
        # Write markdown documentations
        (SDK_DIR / "README.md").write_text(README_CONTENT, encoding="utf-8")
        (SDK_DIR / "plugin_documentation.md").write_text(PLUGIN_DOCS, encoding="utf-8")
        (SDK_DIR / "api_documentation.md").write_text(API_DOCS, encoding="utf-8")
        
        # Write sample plugin
        sample_dir = SDK_DIR / "examples" / "sample_plugin"
        sample_dir.mkdir(parents=True, exist_ok=True)
        
        with open(sample_dir / "manifest.json", 'w', encoding='utf-8') as f:
            json.dump(SAMPLE_MANIFEST, f, indent=4)
            
        with open(sample_dir / "weapons.json", 'w', encoding='utf-8') as f:
            json.dump(SAMPLE_WEAPONS, f, indent=4)
            
        with open(sample_dir / "builds.json", 'w', encoding='utf-8') as f:
            json.dump(SAMPLE_BUILDS, f, indent=4)
            
        (sample_dir / "commands.py").write_text(SAMPLE_COMMANDS, encoding="utf-8")

if __name__ == "__main__":
    SDKGenerator().generate_sdk()
    print("SDK directory successfully generated.")
