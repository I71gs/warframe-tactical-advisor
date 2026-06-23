from src.core.session_engine import SessionEngine

def test_session_planner() -> None:
    se = SessionEngine()
    
    # 30 minute session
    check_30 = se.generate_itinerary(30)
    assert len(check_30) > 0
    total_time_30 = sum(item["duration"] for item in check_30)
    assert total_time_30 <= 30

    # 1 hour session
    check_60 = se.generate_itinerary(60)
    assert len(check_60) > 0
    total_time_60 = sum(item["duration"] for item in check_60)
    assert total_time_60 <= 60

    # 2 hour session
    check_120 = se.generate_itinerary(120)
    assert len(check_120) > 0
    total_time_120 = sum(item["duration"] for item in check_120)
    assert total_time_120 <= 120

    for item in check_30:
        assert "activity" in item
        assert "duration" in item
        assert "location" in item
        assert "reward" in item
        assert "completed" in item
