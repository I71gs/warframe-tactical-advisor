import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from src.gui.window_manager import WindowManager, ChildWindow

class MockWidget(QWidget):
    pass

def test_window_manager_single_instance() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    parent = QMainWindow()
    
    manager = WindowManager(parent)
    assert len(manager.active_windows) == 0
    
    # Open window first time
    manager.open_window("Test Window", MockWidget)
    assert "Test Window" in manager.active_windows
    win1 = manager.active_windows["Test Window"]
    
    # Open window second time -> should not duplicate, should return same window object
    manager.open_window("Test Window", MockWidget)
    assert len(manager.active_windows) == 1
    assert manager.active_windows["Test Window"] is win1
    
    # Close window -> should delete from active registry
    win1.close()
    assert "Test Window" not in manager.active_windows

def test_window_manager_multiple_closing() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    parent = QMainWindow()
    manager = WindowManager(parent)
    
    manager.open_window("Win A", MockWidget)
    manager.open_window("Win B", MockWidget)
    assert len(manager.active_windows) == 2
    
    manager.active_windows["Win A"].close()
    assert len(manager.active_windows) == 1
    assert "Win A" not in manager.active_windows
    assert "Win B" in manager.active_windows
    
    manager.active_windows["Win B"].close()
    assert len(manager.active_windows) == 0

