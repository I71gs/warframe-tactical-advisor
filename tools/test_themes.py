from __future__ import annotations
import json
from pathlib import Path

REQUIRED_KEYS = ["PRIMARY", "SECONDARY", "ACCENT", "TEXT", "MUTED", "CARD"]

def test_themes() -> None:
    root = Path(__file__).resolve().parents[1]
    themes_dir = root / "themes"
    if not themes_dir.exists():
        print("No themes directory found.")
        return
    
    paths = list(themes_dir.glob("*.json"))
    custom_dir = themes_dir / "custom"
    if custom_dir.exists():
        paths.extend(custom_dir.glob("*.json"))

    print(f"Validating {len(paths)} theme files...")
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                name = data.get("name", p.stem)
                missing = [k for k in REQUIRED_KEYS if k not in data]
                if missing:
                    print(f"  - [FAIL] {p.name} ('{name}'): Missing keys: {', '.join(missing)}")
                else:
                    print(f"  - [PASS] {p.name} ('{name}')")
        except Exception as e:
            print(f"  - [FAIL] {p.name}: Failed to read/parse: {e}")

if __name__ == "__main__":
    test_themes()
