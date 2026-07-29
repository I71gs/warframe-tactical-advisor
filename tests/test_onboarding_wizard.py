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

def test_onboarding_wizard_import_parsing() -> None:
    """Verify that entering a username parses it and dynamically populates core profile data."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    wizard = OnboardingWizard()
    
    # Test for beginner name
    wizard.username_input.setText("NewTenno")
    wizard.advance_import_progress()
    
    assert wizard.mr_spin.value() >= 2
    assert not wizard.sp_check.isChecked()
    
    # Test for endgame name
    wizard.username_input.setText("EndgameGod26")
    wizard.advance_import_progress()
    
    assert wizard.mr_spin.value() == 26
    assert wizard.sp_check.isChecked()
    assert wizard.helminth_check.isChecked()
    
    # Check that quests/warframes/mods were selected based on MR 26
    assert wizard.quest_checks["The New War"].isChecked()
    assert wizard.frame_checks["Volt Prime"].isChecked()
    assert wizard.mod_checks["Galvanized Chamber"].isChecked()

def test_onboarding_wizard_database_saving() -> None:
    """Verify that finishing onboarding correctly writes choices to settings and database."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    wizard = OnboardingWizard()
    wizard.username_input.setText("EndgameGod26")
    wizard.advance_import_progress()
    
    # Manually change MR and some check boxes to verify review adjustments
    wizard.mr_spin.setValue(18)
    wizard.sp_check.setChecked(True)
    wizard.quest_checks["The Sacrifice"].setChecked(True)
    wizard.quest_checks["The New War"].setChecked(False) # Turn off to test manual edit
    
    wizard.select_goal_path("Endgame")
    
    # Execute save
    wizard.finish_onboarding()
    
    # Check Settings
    settings = SettingsManager()
    assert settings.get('onboarding_completed')
    assert settings.get('onboarding_path') == "Endgame"
    assert settings.get('priority_level') == "power"
    assert "STORY" in settings.get('recommendation_filters')
    
    # Check Database
    from src.database.database import DatabaseManager
    db = DatabaseManager()
    player = db.get_player()
    assert player is not None
    assert player[0] == 18 # Mastery Rank
    assert player[1] == 1  # Steel Path
    
    quests = db.get_completed_quests()
    assert "The Sacrifice" in quests
    assert "The New War" not in quests
