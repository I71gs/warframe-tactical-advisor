import sys
from PySide6.QtWidgets import QApplication
from src.gui.widgets.onboarding_wizard import OnboardingWizard
from src.core.settings_manager import SettingsManager

def test_onboarding_wizard_instantiation() -> None:
    """Verify that the onboarding dialog can be created and has correct default configuration options."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    wizard = OnboardingWizard()
    
    assert wizard.windowTitle() == "Advisor Tactical Briefing Onboarding"
    assert wizard.pages.currentIndex() == 0
    assert wizard.selected_path == "New Player"

def test_onboarding_wizard_goal_selection() -> None:
    """Verify selecting different path cards updates the dialog selection state."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    wizard = OnboardingWizard()
    
    # Check default selection
    assert wizard.btn_new.isChecked()
    assert not wizard.btn_mid.isChecked()
    assert not wizard.btn_end.isChecked()

    # Simulate selecting Progressing path
    wizard.select_goal_path("Progressing")
    assert wizard.selected_path == "Progressing"
    assert not wizard.btn_new.isChecked()
    assert wizard.btn_mid.isChecked()
    assert not wizard.btn_end.isChecked()

    # Simulate selecting Endgame path
    wizard.select_goal_path("Endgame")
    assert wizard.selected_path == "Endgame"
    assert not wizard.btn_new.isChecked()
    assert not wizard.btn_mid.isChecked()
    assert wizard.btn_end.isChecked()
