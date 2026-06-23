from pathlib import Path
from src.core.report_engine import ReportEngine

def test_report_engine(tmp_path: Path) -> None:
    re = ReportEngine()
    data = re.compile_report_data()
    assert "player_profile" in data
    assert "resources" in data
    assert "economy_plan" in data

    # Test file writing
    json_path = tmp_path / "report.json"
    csv_path = tmp_path / "report.csv"
    txt_path = tmp_path / "report.txt"

    re.export_json(json_path)
    assert json_path.exists()
    assert json_path.stat().st_size > 0

    re.export_csv(csv_path)
    assert csv_path.exists()
    assert csv_path.stat().st_size > 0

    re.export_text(txt_path)
    assert txt_path.exists()
    assert txt_path.stat().st_size > 0
