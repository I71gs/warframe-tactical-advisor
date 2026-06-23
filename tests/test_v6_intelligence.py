from __future__ import annotations
import sys
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication
from src.models.player import Player
from src.core.intent_parser import IntentParser
from src.core.expert_system import ExpertSystem
from src.core.future_projection_engine import FutureProjectionEngine
from src.core.timeline_replay_engine import TimelineReplayEngine
from src.core.session_optimizer import SessionOptimizer
from src.core.knowledge_graph_engine import KnowledgeGraphEngine
from src.services.analytics_service import AnalyticsService
from src.core.profiler import Profiler
from src.core.plugin_registry import PluginRegistry
from src.core.advisor_ai import AdvisorAI
from src.api.app import get_profile, get_progression, get_advisor_advice, get_projection_simulation

def test_intent_parser() -> None:
    ip = IntentParser()
    
    # 1. Tonight / session intent
    res1 = ip.parse_intent("What should I do tonight?")
    assert res1["intent"] == "RECOMMEND_DAILY_SESSION"
    
    # 2. Steel path intent
    res2 = ip.parse_intent("How do I unlock steel path fastest?")
    assert res2["intent"] == "UNLOCK_STEEL_PATH"
    
    # 3. Power gain intent
    res3 = ip.parse_intent("What is my biggest power gain?")
    assert res3["intent"] == "POWER_GAIN"
    
    # 4. Fallback general intent
    res4 = ip.parse_intent("Phenmor builds")
    assert res4["intent"] == "GENERAL_QUERY"

def test_expert_system_and_advisor() -> None:
    player = Player(
        mastery_rank=8,
        completed_quests=["The Second Dream"],
        steel_path_unlocked=False,
        arbitrations_unlocked=False,
        owned_mods=[],
        owned_arcanes=[],
        owned_weapons=[]
    )
    
    es = ExpertSystem()
    advice = es.evaluate(player)
    
    # Needs to complete New War and MR14
    assert any(a["rule_name"] == "New War Quest" for a in advice)
    assert any(a["rule_name"] == "Mastery Rank 14 Target" for a in advice)
    
    ai = AdvisorAI()
    # Check tonight advice returns checklist task
    tonight_advice = ai.get_advice("What should I do tonight?")
    assert "task" in tonight_advice
    assert "eta" in tonight_advice
    assert "power_gain" in tonight_advice

def test_future_projection_engine() -> None:
    player = Player(
        mastery_rank=10,
        completed_quests=["The Second Dream", "The War Within", "The Sacrifice", "The New War"],
        steel_path_unlocked=False,
        arbitrations_unlocked=False,
        owned_mods=["Galvanized Chamber"],
        owned_arcanes=[],
        owned_weapons=[]
    )
    
    fpe = FutureProjectionEngine()
    res = fpe.simulate(player)
    
    assert "current_readiness" in res
    assert "projections" in res
    assert len(res["projections"]) == 3
    
    # Ensure gain calculations are present
    for proj in res["projections"]:
        assert "scenario" in proj
        assert "readiness" in proj
        assert "gain" in proj

def test_timeline_replay_engine() -> None:
    player = Player(mastery_rank=14)
    tre = TimelineReplayEngine()
    steps = tre.get_replay_data(player)
    
    assert len(steps) >= 5
    assert steps[0]["step_name"] == "Day 1 (Initiate)"
    for s in steps:
        assert "mastery_rank" in s
        assert "readiness" in s
        assert "milestone" in s

def test_session_optimizer() -> None:
    player = Player(
        mastery_rank=14,
        completed_quests=["The Second Dream", "The New War"],
        steel_path_unlocked=True,
        arbitrations_unlocked=True,
        owned_mods=[],
        owned_arcanes=[],
        owned_weapons=[]
    )
    so = SessionOptimizer()
    opt = so.optimize_session(player, 60)
    
    assert opt["duration"] == 60
    assert len(opt["sequence"]) > 0
    assert "power_gain_per_hour" in opt
    assert "resource_gain_per_hour" in opt

def test_knowledge_graph_engine() -> None:
    kge = KnowledgeGraphEngine()
    
    # Lookup node neighbors
    neighbors = kge.get_neighbors("Phenmor")
    assert len(neighbors) > 0
    assert any(n["node"] == "Angels of Zariman" for n in neighbors)
    
    # BFS Path Finder: Phenmor -> The New War
    path = kge.find_path("Phenmor", "The New War")
    assert path is not None
    assert "Angels of Zariman" in path
    
    # Invalid node path returns None
    assert kge.find_path("Phenmor", "InvalidNode") is None

def test_analytics_and_profiler(tmp_path: Path) -> None:
    analytics_file = tmp_path / "analytics.json"
    aserv = AnalyticsService(filepath=analytics_file)
    
    aserv.track_tab_view("Dashboard")
    aserv.track_search("Phenmor")
    aserv.track_bottleneck("Locked Steel Path")
    aserv.track_readiness_score(72.5)
    
    # Reload and verify
    aserv2 = AnalyticsService(filepath=analytics_file)
    metrics = aserv2.get_metrics()
    
    assert metrics["tab_views"]["Dashboard"] == 1
    assert metrics["search_queries"]["Phenmor"] == 1
    assert metrics["bottlenecks"]["Locked Steel Path"] == 1
    assert metrics["readiness_history"][-1] == 72.5
    
    # Profiler test
    prof = Profiler()
    report = prof.run_profiling()
    assert "startup_time_ms" in report
    assert "database_latency_ms" in report
    assert "memory_usage_mb" in report
    
    assert Path("performance_report.json").exists()

def test_marketplace_plugins_registry(tmp_path: Path) -> None:
    registry = PluginRegistry()
    registry.clear()
    
    # Set up temp plugin directory structure
    plugin_dir = tmp_path / "sample_plugin"
    plugin_dir.mkdir()
    
    manifest = {
        "id": "test_plugin",
        "name": "Test Plugin",
        "version": "1.0.0",
        "min_app_version": "6.0.0",
        "dependencies": []
    }
    with open(plugin_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f)
        
    weapons = [{"name": "Test SDK Weapon", "type": "Primary", "meta_rating": 80}]
    with open(plugin_dir / "weapons.json", 'w') as f:
        json.dump(weapons, f)
        
    commands_code = """
def register_plugin(registry):
    registry.register_command("Test Command", lambda: None)
"""
    (plugin_dir / "commands.py").write_text(commands_code)
    
    success = registry.load_plugin_from_directory(plugin_dir)
    assert success is True
    
    assert any(w["name"] == "Test SDK Weapon" for w in registry.weapons)
    assert len(registry.commands) == 1
    assert registry.commands[0]["label"] == "Test Command"

def test_fastapi_endpoints() -> None:
    # 1. Profile Endpoint
    profile = get_profile()
    assert "mastery_rank" in profile
    assert "completed_quests" in profile
    
    # 2. Progression Endpoint
    prog = get_progression()
    assert "readiness_score" in prog
    assert "stage" in prog
    
    # 3. Advisor Endpoint
    advice = get_advisor_advice("What should I do tonight?")
    assert "task" in advice
    assert "eta" in advice
    
    # 4. Simulation Endpoint
    sim = get_projection_simulation()
    assert "current_readiness" in sim
    assert "projections" in sim
