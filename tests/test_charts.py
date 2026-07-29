from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine
from src.gui.charts_tab import ChartsTab
from src.gui.widgets.custom_charts import CircularProgress, RadarChartWidget, LineChartWidget, PieChartWidget, BarChartWidget

# Ensure a QApplication instance exists
app = QApplication.instance() or QApplication([])

def test_custom_charts_widgets() -> None:
    # 1. CircularProgress
    prog = CircularProgress(color="#00a3cc", thickness=10, min_size=80, label="Test", subtitle="Subtitle")
    prog.set_value(75.5)
    assert prog.target_value == 75.5
    assert prog.thickness == 10
    
    # 2. RadarChartWidget
    radar = RadarChartWidget()
    radar.set_data(
        categories=["Story", "Mods", "Arcanes"],
        series=[{"name": "P1", "values": [50.0, 75.0, 100.0], "color": "#00a3cc"}]
    )
    assert radar.categories == ["Story", "Mods", "Arcanes"]
    assert len(radar.series) == 1
    
    # 3. LineChartWidget
    line = LineChartWidget()
    line.set_data(
        x_labels=["Day 1", "Day 2"],
        series=[{"name": "Readiness", "values": [40.0, 80.0], "color": "#caa3ff"}]
    )
    assert line.x_labels == ["Day 1", "Day 2"]
    assert len(line.series) == 1
    
    # 4. PieChartWidget
    pie = PieChartWidget()
    pie.set_data(["A", "B"], [10.0, 20.0])
    assert pie.labels == ["A", "B"]
    assert pie.values == [10.0, 20.0]
    
    # 5. BarChartWidget
    bar = BarChartWidget()
    bar.set_data(["A", "B"], [5.0, 15.0])
    assert bar.x_labels == ["A", "B"]
    assert bar.values == [5.0, 15.0]

def test_charts_tab_selections() -> None:
    tab = ChartsTab()
    assert tab is not None
    
    # Test switching through all selector items
    for idx in range(tab.chart_selector.count()):
        text = tab.chart_selector.itemText(idx)
        tab.chart_selector.setCurrentIndex(idx)
        
        # Verify a widget was successfully added to the canvas layout
        assert tab.canvas_layout.count() > 0
        w = tab.canvas_layout.itemAt(0).widget()
        assert w is not None
