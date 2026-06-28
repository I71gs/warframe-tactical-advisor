from typing import Any
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from src.core.app_context import AppContext
from src.core.search_engine_v2 import SearchEngineV2
from src.core.advisor_ai import AdvisorAI
from src.core.future_projection_engine import FutureProjectionEngine

app = FastAPI(
    title="Warframe Tactical Advisor Developer API",
    description="Local web service layer exposing profile stats, simulated projections, and AI advisor offline.",
    version="6.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

context = AppContext()
search_engine = SearchEngineV2(context)
advisor = AdvisorAI(context)
projection_engine = FutureProjectionEngine()

@app.get("/profile")
def get_profile() -> dict:
    """Returns the current player's profile progression, inventory, and unlock state."""
    player = context.player_service.get_player()
    return {
        "mastery_rank": player.mastery_rank,
        "completed_quests": player.completed_quests,
        "owned_mods": player.owned_mods,
        "owned_arcanes": player.owned_arcanes,
        "owned_weapons": player.owned_weapons,
        "steel_path_unlocked": player.steel_path_unlocked,
        "arbitrations_unlocked": player.arbitrations_unlocked,
        "helminth_unlocked": player.helminth_unlocked
    }

@app.get("/recommendations")
def get_recommendations() -> list:
    """Returns dynamic recommendations for weapon builds and loadouts."""
    return context.build_service.get_recommendations()

@app.get("/progression")
def get_progression() -> dict:
    """Returns aggregate readiness scores and primary roadmap targets."""
    return {
        "stage": context.progression_service.get_stage(),
        "primary_goal": context.progression_service.get_primary_goal(),
        "story_score": context.progression_service.get_story_score(),
        "readiness_score": context.progression_service.get_readiness_score()
    }

@app.get("/builds")
def get_builds(weapon: str | None = None) -> Any:
    """Returns all cached meta builds, or filters by a specific weapon."""
    if weapon:
        return context.build_service.get_build_for_weapon(weapon)
    return context.build_service.get_all_builds()

@app.get("/search")
def run_search(q: str = Query(..., description="Query keyword to filter database")) -> list:
    """Performs global search across items, milestones, relics, and plugins."""
    return search_engine.search(q)

@app.get("/resources")
def get_resources() -> dict:
    """Returns currently owned resource stockpiles."""
    return context.resource_service.get_owned_resources()

@app.get("/advisor")
def get_advisor_advice(q: str = Query(..., description="Natural language query")) -> dict:
    """Returns parsed intent and custom progress coaching advice."""
    return advisor.get_advice(q)

@app.get("/worldstate")
def get_world_state() -> dict:
    """Returns live Cetus, Vallis, Zariman cycle statuses, active alerts, and fissures."""
    return context.world_state_service.get_world_state()

@app.get("/sim")
def get_projection_simulation() -> dict:
    """Runs a future projection simulation on readiness outcomes."""
    player = context.player_service.get_player()
    return projection_engine.simulate(player)

@app.get("/charts")
def get_charts_data() -> dict:
    """Returns the historical growth timeline data and radar categories."""
    from src.core.statistics_engine_v2 import StatisticsEngineV2
    stats_engine = StatisticsEngineV2()
    player = context.player_service.get_player()
    return {
        "growth_data": stats_engine.get_growth_data(player),
        "radar_categories": ['Story', 'Mods', 'Arcanes', 'Weapons', 'Mastery', 'Unlocks', 'Builds']
    }

@app.get("/codex")
def get_codex_data() -> dict:
    """Returns lists of weapons, arcanes, and warframes in the advisor database."""
    from src.core.weapon_database import WEAPONS
    from src.core.arcane_database import ARCANES
    from src.core.collection_engine import CORE_WARFRAMES
    return {
        "weapons": WEAPONS,
        "arcanes": ARCANES,
        "warframes": CORE_WARFRAMES
    }

@app.get("/statistics")
def get_statistics_data() -> dict:
    """Returns clearance statistics and progress score breakdowns."""
    from src.core.statistics_engine_v2 import StatisticsEngineV2
    stats_engine = StatisticsEngineV2()
    player = context.player_service.get_player()
    return {
        "clearance": stats_engine.get_clearance_statistics(player),
        "scores_breakdown": stats_engine.get_scores_breakdown(player)
    }

@app.get("/packs")
def get_packs() -> dict:
    """Returns all data packs list and unmet dependencies metadata."""
    from src.core.pack_manager import PackManager
    pm = PackManager()
    return {
        "packs": pm.get_all_packs(),
        "unmet_dependencies": pm.validate_dependencies()
    }

@app.post("/packs/{pack_id}/toggle")
def toggle_pack(pack_id: str, enabled: bool) -> dict:
    """Enable or disable a specific data pack."""
    from src.core.pack_manager import PackManager
    pm = PackManager()
    success = pm.set_pack_enabled(pack_id, enabled)
    return {"success": success, "pack_id": pack_id, "enabled": enabled}

@app.get("/inventory/weapons")
def get_inventory_weapons() -> list:
    """Returns detailed weapons inventory (rank, forma count, catalyst state)."""
    return context.player_service.get_weapon_inventory()

@app.post("/inventory/weapons")
def update_inventory_weapon(
    name: str,
    rank: int = 30,
    forma_count: int = 0,
    has_catalyst: bool = False
) -> dict:
    """Add or update detailed weapon stats in inventory."""
    context.player_service.update_weapon_details(name, rank, forma_count, has_catalyst)
    return {"success": True, "weapon": name}

@app.delete("/inventory/weapons")
def delete_inventory_weapon(name: str) -> dict:
    """Delete weapon from detailed inventory."""
    context.player_service.remove_weapon_detailed(name)
    return {"success": True, "weapon": name}

@app.get("/inventory/mods")
def get_inventory_mods() -> list:
    """Returns detailed mods inventory (mod name, rank, max rank)."""
    return context.player_service.get_mod_inventory()

@app.post("/inventory/mods")
def update_inventory_mod(
    name: str,
    rank: int = 10,
    max_rank: int = 10
) -> dict:
    """Add or update detailed mod stats in inventory."""
    context.player_service.update_mod_details(name, rank, max_rank)
    return {"success": True, "mod": name}

@app.delete("/inventory/mods")
def delete_inventory_mod(name: str) -> dict:
    """Delete mod from detailed inventory."""
    context.player_service.remove_mod_detailed(name)
    return {"success": True, "mod": name}


