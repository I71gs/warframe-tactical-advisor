from src.core.relic_engine import RelicEngine


def test_relic_search_by_item() -> None:
    """search_relics returns relic dicts that contain matching reward items."""
    re = RelicEngine()
    results = re.search_relics("Glaive")
    assert len(results) >= 1
    # Each result is a full relic dict containing a rewards list
    found_glaive = any(
        any("Glaive" in r["item"] for r in relic.get("rewards", []))
        for relic in results
    )
    assert found_glaive, "Expected at least one relic with a Glaive Prime reward"


def test_relic_search_empty_returns_all() -> None:
    re = RelicEngine()
    all_res = re.search_relics("")
    blank_res = re.search_relics("  ")
    assert len(all_res) == len(blank_res)
    assert len(all_res) > 0


def test_get_relics_for_item() -> None:
    """get_relics_for_item returns item-level dicts with rarity and node info."""
    re = RelicEngine()
    results = re.get_relics_for_item("Saryn Prime Blueprint")
    assert len(results) >= 1
    entry = results[0]
    assert "relic_name" in entry
    assert "rarity" in entry
    assert "best_farm_node" in entry
    assert "drop_chance_radiant" in entry


def test_plan_farming_found() -> None:
    """plan_farming returns a full plan for a known item."""
    re = RelicEngine()
    plan = re.plan_farming("Saryn Prime Blueprint")
    assert plan["found"] is True
    assert plan["item"] != ""
    assert plan["expected_runs"] > 0
    assert "recommended_refinement" in plan
    assert plan["best_farm_node"] != ""


def test_plan_farming_not_found() -> None:
    re = RelicEngine()
    plan = re.plan_farming("NonExistentItemXYZ123")
    assert plan["found"] is False
    assert "message" in plan


def test_expected_runs_calculation() -> None:
    re = RelicEngine()
    # 10% drop chance → expect 10 runs
    assert re.calculate_expected_runs(10.0) == 10
    # 100% → 1 run
    assert re.calculate_expected_runs(100.0) == 1
    # 0 or negative → 999
    assert re.calculate_expected_runs(0) == 999
