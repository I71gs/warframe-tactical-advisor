from __future__ import annotations
import pytest
from src.core.snapshot_repository import SnapshotRepository
from src.core.history_engine import HistoryEngine
from src.models.player import Player


def test_history_empty_snapshots(tmp_path) -> None:
    repo = SnapshotRepository(snapshots_dir=tmp_path)
    engine = HistoryEngine(repo=repo)
    trends = engine.get_growth_trends()
    assert len(trends["mr"]) == 0


def test_history_mr_trends(tmp_path) -> None:
    repo = SnapshotRepository(snapshots_dir=tmp_path)
    repo.save_snapshot(Player(mastery_rank=12), "2026-06-20")
    repo.save_snapshot(Player(mastery_rank=15), "2026-06-21")
    engine = HistoryEngine(repo=repo)
    trends = engine.get_growth_trends()
    assert trends["mr"][0]["value"] == 12
    assert trends["mr"][1]["value"] == 15


def test_history_quest_activity_trends(tmp_path) -> None:
    repo = SnapshotRepository(snapshots_dir=tmp_path)
    repo.save_snapshot(Player(mastery_rank=10, completed_quests=["Quest 1"]), "2026-06-20")
    repo.save_snapshot(Player(mastery_rank=10, completed_quests=["Quest 1", "Quest 2"]), "2026-06-21")
    engine = HistoryEngine(repo=repo)
    trends = engine.get_growth_trends()
    assert trends["quest_activity"][0]["value"] == 1
    assert trends["quest_activity"][1]["value"] == 1


def test_history_relic_unlock_trends(tmp_path) -> None:
    repo = SnapshotRepository(snapshots_dir=tmp_path)
    repo.save_snapshot(Player(mastery_rank=10, owned_weapons=["Weap1"]), "2026-06-20")
    repo.save_snapshot(Player(mastery_rank=10, owned_weapons=["Weap1", "Weap2"]), "2026-06-21")
    engine = HistoryEngine(repo=repo)
    trends = engine.get_growth_trends()
    assert trends["relic_unlocks"][0]["value"] == 1
    assert trends["relic_unlocks"][1]["value"] == 1


def test_history_build_crafting_trends(tmp_path) -> None:
    repo = SnapshotRepository(snapshots_dir=tmp_path)
    repo.save_snapshot(Player(mastery_rank=10, owned_mods=["Mod1"]), "2026-06-20")
    repo.save_snapshot(Player(mastery_rank=10, owned_mods=["Mod1", "Mod2"]), "2026-06-21")
    engine = HistoryEngine(repo=repo)
    trends = engine.get_growth_trends()
    assert trends["build_crafting"][0]["value"] == 1
    assert trends["build_crafting"][1]["value"] == 1
