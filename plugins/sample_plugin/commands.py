from __future__ import annotations
import PySide6.QtWidgets as QtWidgets

def register_plugin(registry) -> None:
    """Invoked by the PluginRegistry script loader to execute commands and tabs registration."""
    def hello_action() -> None:
        print("Hello from Sample Plugin command!")

    registry.register_command("Sample Plugin: Say Hello", hello_action)

    # Register a dynamic custom tab
    class SamplePluginTab(QtWidgets.QWidget):
        def __init__(self) -> None:
            super().__init__()
            layout = QtWidgets.QVBoxLayout(self)
            label = QtWidgets.QLabel("This is a dynamic tab registered by the Sample Plugin SDK 2.0!", self)
            layout.addWidget(label)

    registry.register_tab(SamplePluginTab, "Sample Plugin Tab")
