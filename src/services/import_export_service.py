from __future__ import annotations
import json
import csv
from pathlib import Path
from typing import Any
from src.core.player_loader import PlayerLoader
from src.database.database import DatabaseManager
from src.models.player import Player
from src.utils.logger import logger

class ImportExportService:
    """Manages profile exports (JSON, CSV), data restores, and profile merging."""

    def __init__(self, context: Any = None) -> None:
        self.context = context

    def export_to_json(self, destination: str | Path) -> None:
        """Export current profile state to a JSON file."""
        player = PlayerLoader().load_player()
        data = {
            "version": "8.0",
            "profile": {
                "mastery_rank": player.mastery_rank,
                "steel_path_unlocked": player.steel_path_unlocked,
                "arbitrations_unlocked": player.arbitrations_unlocked,
                "helminth_unlocked": player.helminth_unlocked,
                "completed_quests": player.completed_quests,
                "owned_mods": player.owned_mods,
                "owned_arcanes": player.owned_arcanes,
                "owned_weapons": player.owned_weapons,
            }
        }
        with open(destination, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info("Profile successfully exported to JSON: %s", destination)

    def export_to_csv(self, destination: str | Path) -> None:
        """Export current profile state to a CSV file."""
        player = PlayerLoader().load_player()
        with open(destination, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Name", "Value"])
            
            # Attributes
            writer.writerow(["Attribute", "mastery_rank", str(player.mastery_rank)])
            writer.writerow(["Attribute", "steel_path_unlocked", str(player.steel_path_unlocked)])
            writer.writerow(["Attribute", "arbitrations_unlocked", str(player.arbitrations_unlocked)])
            writer.writerow(["Attribute", "helminth_unlocked", str(player.helminth_unlocked)])
            
            # Lists
            for q in player.completed_quests:
                writer.writerow(["Quest", q, "Completed"])
            for m in player.owned_mods:
                writer.writerow(["Mod", m, "Owned"])
            for a in player.owned_arcanes:
                writer.writerow(["Arcane", a, "Owned"])
            for w in player.owned_weapons:
                writer.writerow(["Weapon", w, "Owned"])
        logger.info("Profile successfully exported to CSV: %s", destination)

    def import_from_json(self, source: str | Path) -> Player:
        """Loads and returns a Player object from JSON without saving it to DB yet."""
        with open(source, "r", encoding="utf-8") as f:
            data = json.load(f)
        profile = data.get("profile", data) if "profile" in data else data
        return Player(
            mastery_rank=profile.get("mastery_rank", 1),
            steel_path_unlocked=bool(profile.get("steel_path_unlocked", False)),
            arbitrations_unlocked=bool(profile.get("arbitrations_unlocked", False)),
            helminth_unlocked=bool(profile.get("helminth_unlocked", False)),
            completed_quests=profile.get("completed_quests", []),
            owned_mods=profile.get("owned_mods", []),
            owned_arcanes=profile.get("owned_arcanes", []),
            owned_weapons=profile.get("owned_weapons", [])
        )

    def import_from_csv(self, source: str | Path) -> Player:
        """Loads and returns a Player object from CSV without saving it to DB yet."""
        mastery_rank = 1
        steel_path_unlocked = False
        arbitrations_unlocked = False
        helminth_unlocked = False
        completed_quests = []
        owned_mods = []
        owned_arcanes = []
        owned_weapons = []

        with open(source, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if not row or len(row) < 3:
                    continue
                rtype, rname, rval = row[0], row[1], row[2]
                if rtype == "Attribute":
                    if rname == "mastery_rank":
                        mastery_rank = int(rval)
                    elif rname == "steel_path_unlocked":
                        steel_path_unlocked = (rval.lower() == "true")
                    elif rname == "arbitrations_unlocked":
                        arbitrations_unlocked = (rval.lower() == "true")
                    elif rname == "helminth_unlocked":
                        helminth_unlocked = (rval.lower() == "true")
                elif rtype == "Quest":
                    completed_quests.append(rname)
                elif rtype == "Mod":
                    owned_mods.append(rname)
                elif rtype == "Arcane":
                    owned_arcanes.append(rname)
                elif rtype == "Weapon":
                    owned_weapons.append(rname)

        return Player(
            mastery_rank=mastery_rank,
            steel_path_unlocked=steel_path_unlocked,
            arbitrations_unlocked=arbitrations_unlocked,
            helminth_unlocked=helminth_unlocked,
            completed_quests=completed_quests,
            owned_mods=owned_mods,
            owned_arcanes=owned_arcanes,
            owned_weapons=owned_weapons
        )

    def restore_profile(self, player: Player) -> None:
        """Overwrites the database with the provided player model."""
        db = DatabaseManager()
        db.cursor.execute("DELETE FROM players")
        db.cursor.execute("DELETE FROM completed_quests")
        db.cursor.execute("DELETE FROM owned_mods")
        db.cursor.execute("DELETE FROM owned_arcanes")
        db.cursor.execute("DELETE FROM owned_weapons")
        db.connection.commit()
        
        db.save_player(
            player.mastery_rank,
            player.steel_path_unlocked,
            player.arbitrations_unlocked,
            player.helminth_unlocked
        )
        for q in player.completed_quests:
            db.add_completed_quest(q)
        for m in player.owned_mods:
            db.add_owned_mod(m)
        for a in player.owned_arcanes:
            db.add_owned_arcane(a)
        for w in player.owned_weapons:
            db.add_owned_weapon(w)
        logger.info("Database successfully restored with player profile.")

    def merge_profiles(self, other_player: Player) -> None:
        """Merges another player profile's unlocked items/quests into the current profile."""
        current = PlayerLoader().load_player()
        
        merged_mr = max(current.mastery_rank, other_player.mastery_rank)
        merged_sp = current.steel_path_unlocked or other_player.steel_path_unlocked
        merged_arbi = current.arbitrations_unlocked or other_player.arbitrations_unlocked
        merged_helm = current.helminth_unlocked or other_player.helminth_unlocked
        
        # Merge lists by taking union
        merged_quests = sorted(list(set(current.completed_quests).union(set(other_player.completed_quests))))
        merged_mods = sorted(list(set(current.owned_mods).union(set(other_player.owned_mods))))
        merged_arcanes = sorted(list(set(current.owned_arcanes).union(set(other_player.owned_arcanes))))
        merged_weapons = sorted(list(set(current.owned_weapons).union(set(other_player.owned_weapons))))
        
        merged_player = Player(
            mastery_rank=merged_mr,
            steel_path_unlocked=merged_sp,
            arbitrations_unlocked=merged_arbi,
            helminth_unlocked=merged_helm,
            completed_quests=merged_quests,
            owned_mods=merged_mods,
            owned_arcanes=merged_arcanes,
            owned_weapons=merged_weapons
        )
        
        self.restore_profile(merged_player)
        logger.info("Successfully merged profiles.")
