from __future__ import annotations
import json
import sys
from pathlib import Path

def validate_plugin(plugin_path: Path) -> bool:
    if not plugin_path.exists() or not plugin_path.is_dir():
        print(f"Plugin path does not exist or is not a directory: {plugin_path}")
        return False
        
    manifest_path = plugin_path / "manifest.json"
    if not manifest_path.exists():
        print("  - [FAIL] Missing manifest.json")
        return False
        
    try:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            
        required = ["id", "name", "author", "version"]
        missing = [k for k in required if k not in data]
        if missing:
            print(f"  - [FAIL] manifest.json is missing keys: {', '.join(missing)}")
            return False
            
        print(f"  - [PASS] manifest.json ('{data['name']}' v{data['version']})")
    except Exception as e:
        print(f"  - [FAIL] Failed to parse manifest.json: {e}")
        return False

    # Check for optional parts
    print("  - Checked files:")
    for f in ["weapons.json", "builds.json", "routes.json", "commands.py"]:
        status = "present" if (plugin_path / f).exists() else "absent"
        print(f"    * {f}: {status}")
        
    return True

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    sample = root / "plugin_examples" / "sample_plugin_v3"
    print(f"Validating sample plugin at {sample}...")
    validate_plugin(sample)
