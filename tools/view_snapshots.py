from __future__ import annotations
import json
from pathlib import Path

def view_snapshots() -> None:
    root = Path(__file__).resolve().parents[1]
    snapshots_dir = root / "snapshots"
    if not snapshots_dir.exists():
        print("No snapshots directory found.")
        return
    
    files = sorted(list(snapshots_dir.glob("*.json")))
    print(f"Found {len(files)} snapshots under {snapshots_dir}:")
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                player = data.get("player", {})
                print(f"  - {f.name}: MR={player.get('mastery_rank')}, Quests={len(player.get('completed_quests', []))}, Weapons={len(player.get('owned_weapons', []))}")
        except Exception as e:
            print(f"  - Error reading {f.name}: {e}")

if __name__ == "__main__":
    view_snapshots()
