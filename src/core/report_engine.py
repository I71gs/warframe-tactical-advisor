from __future__ import annotations
import json
import csv
from pathlib import Path
from typing import Any
from src.core.player_loader import PlayerLoader
from src.core.resource_engine import ResourceEngine
from src.core.economy_engine import EconomyEngine

class ReportEngine:
    """Compiles progress, stats, and builds into JSON, CSV, and text layouts."""

    def compile_report_data(self) -> dict[str, Any]:
        player = PlayerLoader().load_player()
        res_engine = ResourceEngine()
        econ_engine = EconomyEngine()
        
        owned_resources = res_engine.load_owned_resources()
        economy_plan = econ_engine.get_economy_plan()
        
        return {
            "player_profile": {
                "mastery_rank": player.mastery_rank,
                "steel_path_unlocked": player.steel_path_unlocked,
                "arbitrations_unlocked": player.arbitrations_unlocked,
                "helminth_unlocked": player.helminth_unlocked,
                "completed_quests_count": len(player.completed_quests),
                "owned_mods_count": len(player.owned_mods),
                "owned_arcanes_count": len(player.owned_arcanes),
                "owned_weapons_count": len(player.owned_weapons),
            },
            "inventory": {
                "completed_quests": player.completed_quests,
                "owned_mods": player.owned_mods,
                "owned_arcanes": player.owned_arcanes,
                "owned_weapons": player.owned_weapons,
            },
            "resources": owned_resources,
            "economy_plan": economy_plan
        }

    def export_json(self, filepath: str | Path) -> None:
        data = self.compile_report_data()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def export_csv(self, filepath: str | Path) -> None:
        data = self.compile_report_data()
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Metric", "Value"])
            
            # Profile row
            for k, v in data["player_profile"].items():
                writer.writerow(["Profile", k, v])
                
            # Resource row
            for k, v in data["resources"].items():
                writer.writerow(["Resource", k, v])
                
            # Economy plan row
            for item in data["economy_plan"]:
                writer.writerow([
                    "Economy", 
                    item["currency"], 
                    f"Owned: {item['owned']}, Required: {item['required']}, Missing: {item['missing']}, Farm Hours: {item['farm_hours']}"
                ])

    def export_text(self, filepath: str | Path) -> None:
        data = self.compile_report_data()
        profile = data["player_profile"]
        
        lines = [
            "==================================================",
            "        WARFRAME TACTICAL ADVISOR REPORT          ",
            "==================================================",
            "",
            "PLAYER PROFILE SUMMARY:",
            f"  Mastery Rank:        {profile['mastery_rank']}",
            f"  Steel Path:          {'Unlocked' if profile['steel_path_unlocked'] else 'Locked'}",
            f"  Arbitrations:        {'Unlocked' if profile['arbitrations_unlocked'] else 'Locked'}",
            f"  Helminth:            {'Unlocked' if profile['helminth_unlocked'] else 'Locked'}",
            "",
            "INVENTORY TOTALS:",
            f"  Completed Quests:    {profile['completed_quests_count']}",
            f"  Owned Mods:          {profile['owned_mods_count']}",
            f"  Owned Arcanes:       {profile['owned_arcanes_count']}",
            f"  Owned Weapons:       {profile['owned_weapons_count']}",
            "",
            "RESOURCE STOCKPILE:",
        ]
        for name, qty in data["resources"].items():
            lines.append(f"  {name:<20}: {qty}")
            
        lines.append("")
        lines.append("ECONOMY TARGETS & FARMING FORECAST:")
        lines.append(f"  {'Currency':<20} | {'Owned':<10} | {'Target':<10} | {'Missing':<10} | {'Hours':<8} | {'Primary Source'}")
        lines.append("-" * 80)
        for item in data["economy_plan"]:
            lines.append(
                f"  {item['currency']:<20} | {item['owned']:<10} | {item['required']:<10} | "
                f"{item['missing']:<10} | {item['farm_hours']:<8} | {item['source']}"
            )
        lines.append("")
        lines.append("==================================================")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
