from src.core.relic_engine import RelicEngine

def test_relic_search() -> None:
    re = RelicEngine()
    # Query with something that matches
    res = re.search_relics("Glaive")
    assert len(res) >= 1
    assert res[0]["item"] == "Glaive Prime Blueprint"

    # Query with empty string
    all_res = re.search_relics("")
    assert len(all_res) == len(re.search_relics(" "))
