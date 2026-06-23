import sys
from PySide6.QtWidgets import QApplication
from matplotlib.figure import Figure
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine
from src.gui.charts_tab import ChartsTab

def test_charts_rendering() -> None:
    # Ensure a QApplication instance exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
    player = Player(
        mastery_rank=10,
        completed_quests=[],
        steel_path_unlocked=False,
        arbitrations_unlocked=False,
        owned_mods=[],
        owned_arcanes=[],
        owned_weapons=[]
    )
    pe = ProgressionEngine()
    
    # Instantiate charts tab
    tab = ChartsTab()
    assert tab is not None
    
    # Test individual drawing functions directly to ensure they produce Figures
    fig_radar = tab._draw_radar_chart(player, pe)
    assert isinstance(fig_radar, Figure)
    
    fig_pie = tab._draw_pie_chart(player)
    assert isinstance(fig_pie, Figure)
    
    fig_line = tab._draw_line_chart()
    assert isinstance(fig_line, Figure)
