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

@app.get("/sim")
def get_projection_simulation() -> dict:
    """Runs a future projection simulation on readiness outcomes."""
    player = context.player_service.get_player()
    return projection_engine.simulate(player)
