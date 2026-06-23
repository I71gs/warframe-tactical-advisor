from __future__ import annotations
from typing import Any
from src.core.player_loader import PlayerLoader
from src.models.player import Player

class SessionEngine:
    """Generates 30m, 1h, and 2h customized mission itineraries based on player progression."""

    def generate_itinerary(self, duration_minutes: int) -> list[dict[str, Any]]:
        player = PlayerLoader().load_player()
        itinerary = []
        completed_quests = {q.lower() for q in player.completed_quests}

        if duration_minutes <= 30:
            # 30-minute quick session
            if "angels of the zariman" not in completed_quests:
                itinerary.append({
                    "activity": "Progression: Angels of Zariman Quest",
                    "duration": 20,
                    "location": "Zariman Chrysalith",
                    "reward": "Quest progress & Chrysalith access",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Resource Farm: Entrati Lanthorn / Plumes",
                    "duration": 10,
                    "location": "Zariman Halako Perimeter",
                    "reward": "Lanthorns, Gyromag Systems",
                    "completed": False
                })
            elif not player.steel_path_unlocked:
                itinerary.append({
                    "activity": "Clear Star Chart Junctions & Nodes",
                    "duration": 20,
                    "location": "Sedna / Eris Nodes",
                    "reward": "Junction completion, SP unlock prep",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Endo Farm: Weekly Maroo's Bazaar Ayatan",
                    "duration": 10,
                    "location": "Maroo's Bazaar",
                    "reward": "Ayatan Sculpture (~1500 Endo)",
                    "completed": False
                })
            else:
                itinerary.append({
                    "activity": "Steel Path Incursion Quick Runs",
                    "duration": 15,
                    "location": "Daily SP Incursion Nodes",
                    "reward": "5x Steel Essence, Acolyte Arcanes",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Relic Run: Capture/Rescue Fissures",
                    "duration": 15,
                    "location": "Void Fissures",
                    "reward": "Prime parts, Void Traces",
                    "completed": False
                })
        elif duration_minutes <= 60:
            # 1-hour session
            if "angels of the zariman" not in completed_quests:
                itinerary.append({
                    "activity": "Progression: Zariman Quest Line",
                    "duration": 30,
                    "location": "Zariman Chrysalith",
                    "reward": "Quest progress",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Bounty Farm: Voidplume Pinions",
                    "duration": 20,
                    "location": "Zariman Bounties",
                    "reward": "Voidplumes (Entrati Standing)",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Credit Booster: Index Run",
                    "duration": 10,
                    "location": "The Index (Neptune)",
                    "reward": "250,000 Credits",
                    "completed": False
                })
            elif not player.steel_path_unlocked:
                itinerary.append({
                    "activity": "Node Clearing: Remaining Quests & Nodes",
                    "duration": 30,
                    "location": "Various Planets",
                    "reward": "Arbitrations/SP unlock requirement",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Arbitration: Survival or Defense",
                    "duration": 20,
                    "location": "Active Arbitration Node",
                    "reward": "Vitus Essence, Galvanized Mods",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Credit Farm: The Index",
                    "duration": 10,
                    "location": "The Index (Neptune)",
                    "reward": "250,000 Credits",
                    "completed": False
                })
            else:
                itinerary.append({
                    "activity": "Steel Path Incursions (3 runs)",
                    "duration": 25,
                    "location": "Active SP Incursion Nodes",
                    "reward": "15x Steel Essence, Acolyte drops",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Duviri Circuit: Steel Path Evolution",
                    "duration": 25,
                    "location": "The Undercroft",
                    "reward": "Incarnon Adapters, path progress",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Void Fissures: Radshare Runs",
                    "duration": 10,
                    "location": "Lith/Meso/Neo/Axi",
                    "reward": "Rare Prime Parts",
                    "completed": False
                })
        else:
            # 2-hour session
            if "angels of the zariman" not in completed_quests:
                itinerary.append({
                    "activity": "Quest Progression: Zariman & Whispers in the Walls",
                    "duration": 50,
                    "location": "Zariman / Necralisk",
                    "reward": "Story Progression",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Zariman Bounties (Tier 3-4)",
                    "duration": 40,
                    "location": "Zariman Chrysalith",
                    "reward": "Entrati Lanthorns, Thrax Plasm",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Credit Farming: High Index (2 Rounds)",
                    "duration": 20,
                    "location": "The Index (Neptune)",
                    "reward": "500,000 Credits",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Fissure Cracking: Prime Junk / Formas",
                    "duration": 10,
                    "location": "Capture Fissures",
                    "reward": "Forma Blueprints, Prime Parts",
                    "completed": False
                })
            elif not player.steel_path_unlocked:
                itinerary.append({
                    "activity": "Star Chart Completion: Harder Nodes",
                    "duration": 50,
                    "location": "Eris / Sedna / Void",
                    "reward": "Unlock Arbitrations & Steel Path",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Arbitration Farming: Vitus Essence & Endo",
                    "duration": 45,
                    "location": "Arbitration Node",
                    "reward": "10,000+ Endo, Vitus Essence",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Index Credit Farm (2 Rounds)",
                    "duration": 15,
                    "location": "The Index (Neptune)",
                    "reward": "500,000 Credits",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Farming Resource: Voidplumes on Zariman",
                    "duration": 10,
                    "location": "Chrysalith Bounties",
                    "reward": "Voidplume Crests/Quills",
                    "completed": False
                })
            else:
                itinerary.append({
                    "activity": "Full Steel Path Incursion Set (5 runs)",
                    "duration": 40,
                    "location": "Daily SP Incursion Nodes",
                    "reward": "25x Steel Essence, Acolyte Arcanes",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Steel Path Circuit: Target Rank 5/10",
                    "duration": 40,
                    "location": "Duviri Undercroft",
                    "reward": "Incarnon Geneses",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Duviri Experience: Pathos Clamps Run",
                    "duration": 25,
                    "location": "Duviri Landscape",
                    "reward": "15x Pathos Clamps (Kullervo/Genesis)",
                    "completed": False
                })
                itinerary.append({
                    "activity": "Void Fissures: Axi Radshares",
                    "duration": 15,
                    "location": "Axi Fissure",
                    "reward": "Rare Prime weapon parts",
                    "completed": False
                })
        return itinerary
