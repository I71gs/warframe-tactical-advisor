from __future__ import annotations
import json
import pytest
from src.core.route_engine import RouteEngine
from src.models.player import Player


def test_route_engine_load_routes(tmp_path) -> None:
    with open(tmp_path / "r1.json", "w", encoding="utf-8") as f:
        json.dump({"name": "Route 1", "zone": "Zariman"}, f)
    engine = RouteEngine(routes_dir=tmp_path)
    assert len(engine.load_routes()) == 1


def test_route_engine_unlocked_evaluation(tmp_path) -> None:
    with open(tmp_path / "r1.json", "w", encoding="utf-8") as f:
        json.dump({
            "name": "Route 1", "zone": "Zariman",
            "requirements": {"mastery_rank": 5, "completed_quests": ["Quest A"]}
        }, f)
    engine = RouteEngine(routes_dir=tmp_path)
    # Use named parameters to prevent list being mapped to steel_path_unlocked
    p = Player(mastery_rank=10, completed_quests=["Quest A"])
    evaluated = engine.evaluate_routes(p)
    assert evaluated[0]["unlocked"] is True


def test_route_engine_locked_mr_evaluation(tmp_path) -> None:
    with open(tmp_path / "r1.json", "w", encoding="utf-8") as f:
        json.dump({
            "name": "Route 1", "zone": "Zariman",
            "requirements": {"mastery_rank": 15}
        }, f)
    engine = RouteEngine(routes_dir=tmp_path)
    p = Player(mastery_rank=10)
    evaluated = engine.evaluate_routes(p)
    assert evaluated[0]["unlocked"] is False


def test_route_engine_locked_quest_evaluation(tmp_path) -> None:
    with open(tmp_path / "r1.json", "w", encoding="utf-8") as f:
        json.dump({
            "name": "Route 1", "zone": "Zariman",
            "requirements": {"completed_quests": ["Quest A"]}
        }, f)
    engine = RouteEngine(routes_dir=tmp_path)
    p = Player(mastery_rank=10, completed_quests=[])
    evaluated = engine.evaluate_routes(p)
    assert evaluated[0]["unlocked"] is False
