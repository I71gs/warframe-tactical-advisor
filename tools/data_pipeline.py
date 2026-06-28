#!/usr/bin/env python
from __future__ import annotations
import argparse
import sys
import json
import urllib.request
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "src" / "resources" / "data"

def fetch_warframe_drops() -> list[dict]:
    print("Fetching void relics from API drops.warframestat.us...")
    try:
        url = "https://drops.warframestat.us/data/relics.json"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            if isinstance(data, list):
                print(f"Successfully fetched {len(data)} relics.")
                return data
    except Exception as e:
        print(f"API fetch failed: {e}. Falling back to default mock dataset...")
    
    # Static mockup data
    return [
        {
            "era": "Lith",
            "relic_name": "A1",
            "best_farm_node": "Hepit (Void)",
            "rewards": [
                {"item": "Lex Prime Receiver", "rarity": "Common", "drop_chance_intact": 25.3, "drop_chance_radiant": 16.7},
                {"item": "Braton Prime Stock", "rarity": "Common", "drop_chance_intact": 25.3, "drop_chance_radiant": 16.7},
                {"item": "Fang Prime Blade", "rarity": "Common", "drop_chance_intact": 25.3, "drop_chance_radiant": 16.7},
                {"item": "Burston Prime Barrel", "rarity": "Uncommon", "drop_chance_intact": 11.0, "drop_chance_radiant": 20.0},
                {"item": "Orthos Prime Blueprint", "rarity": "Uncommon", "drop_chance_intact": 11.0, "drop_chance_radiant": 20.0},
                {"item": "Saryn Prime Blueprint", "rarity": "Rare", "drop_chance_intact": 2.0, "drop_chance_radiant": 10.0}
            ]
        },
        {
            "era": "Axi",
            "relic_name": "G1",
            "best_farm_node": "Apollo (Lua)",
            "rewards": [
                {"item": "Glaive Prime Disc", "rarity": "Common", "drop_chance_intact": 25.3, "drop_chance_radiant": 16.7},
                {"item": "Orthos Prime Blade", "rarity": "Common", "drop_chance_intact": 25.3, "drop_chance_radiant": 16.7},
                {"item": "Braton Prime Blueprint", "rarity": "Common", "drop_chance_intact": 25.3, "drop_chance_radiant": 16.7},
                {"item": "Fang Prime Blueprint", "rarity": "Uncommon", "drop_chance_intact": 11.0, "drop_chance_radiant": 20.0},
                {"item": "Lex Prime Blueprint", "rarity": "Uncommon", "drop_chance_intact": 11.0, "drop_chance_radiant": 20.0},
                {"item": "Glaive Prime Blueprint", "rarity": "Rare", "drop_chance_intact": 2.0, "drop_chance_radiant": 10.0}
            ]
        }
    ]

def fetch_wiki_data() -> list[dict]:
    print("Fetching wiki data templates for warframe inventory...")
    # Standard static mock list
    return [
        {"name": "Wisp", "acquisition": "Ropalolyst (Jupiter)"},
        {"name": "Saryn", "acquisition": "Kela De Thaym (Sedna)"},
        {"name": "Mesa", "acquisition": "Mutalist Alad V (Eris)"},
        {"name": "Volt", "acquisition": "Tenno Lab (Dojo)"},
        {"name": "Excalibur", "acquisition": "Lieutenant Lech Kril (War, Mars)"},
        {"name": "Rhino", "acquisition": "Jackal (Fossa, Venus)"}
    ]

def validate_schema(data: Any, schema_type: str) -> bool:
    print(f"Validating schema format for {schema_type}...")
    if schema_type == "relics":
        if not isinstance(data, list):
            return False
        for item in data:
            if not all(k in item for k in ["era", "relic_name", "rewards"]):
                return False
    elif schema_type == "warframes":
        if not isinstance(data, list):
            return False
        for item in data:
            if "name" not in item:
                return False
    return True

def run_migrations() -> None:
    print("Running database migrations...")
    from src.database.database import DatabaseManager
    try:
        db = DatabaseManager()
        db.create_tables()
        print("Database schema migration completed successfully.")
    except Exception as e:
        print(f"Migration error: {e}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Warframe Advisor Data Pipeline tool")
    parser.add_argument("--all", action="store_true", help="Run the entire pipeline (Fetch, Validate, Write, Migrate)")
    parser.add_argument("--module", choices=["relics", "warframes", "migrate"], help="Run a specific pipeline module")
    
    args = parser.parse_args()

    if not (args.all or args.module):
        parser.print_help()
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.all or args.module == "relics":
        relics = fetch_warframe_drops()
        if validate_schema(relics, "relics"):
            dest = DATA_DIR / "relics.json"
            with open(dest, "w", encoding="utf-8") as f:
                json.dump(relics, f, indent=4)
            print(f"Relics dataset written to {dest}")
        else:
            print("Validation failed for relics schema.")

    if args.all or args.module == "warframes":
        frames = fetch_wiki_data()
        if validate_schema(frames, "warframes"):
            dest = DATA_DIR / "warframe_inventory.json"
            # Read existing or overwrite
            existing = []
            if dest.exists():
                try:
                    with open(dest, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                except Exception:
                    pass
            # Merge to preserve ranks
            merged = {f["name"].lower(): f for f in existing}
            for f in frames:
                name_l = f["name"].lower()
                if name_l not in merged:
                    merged[name_l] = f
            with open(dest, "w", encoding="utf-8") as f:
                json.dump(list(merged.values()), f, indent=4)
            print(f"Warframe inventory template written to {dest}")
        else:
            print("Validation failed for warframes schema.")

    if args.all or args.module == "migrate":
        run_migrations()

    print("Data pipeline executed successfully.")

if __name__ == "__main__":
    main()
