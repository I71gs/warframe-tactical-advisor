# FAQ & Troubleshooting Guide — Warframe Tactical Advisor

Welcome to the FAQ & Troubleshooting guide. This document helps resolve issues relating to application setup, in-game overlay mode, profile account settings, and dependencies.

---

## 🛠️ Installation & Setup Issues

### Q: Why does the application fail to start or import `PySide6`?
- **Symptom**: Startup crashes with `ImportError: DLL load failed` or `ModuleNotFoundError: No module named 'PySide6'`.
- **Solution**:
  1. Ensure you have installed the exact dependencies in `requirements.txt`:
     ```bash
     pip install -r requirements.txt
     ```
  2. If on Windows, ensure your Python installation matches your architecture (64-bit Python for 64-bit Windows) and that you are running Python 3.11+.
  3. Ensure graphics drivers are updated, as PySide6 utilizes hardware acceleration for rendering widgets and themes.

### Q: How do I run the first-time onboarding Setup Wizard again?
- **Symptom**: You completed the wizard but want to reset your default Mastery Rank (MR) and Steel Path milestones.
- **Solution**: The setup wizard only triggers if no player profile is found in the database. To force it to launch, close the application, delete `player.db` from the root directory, and launch the application again.

### Q: PyInstaller package output immediately closes on launch.
- **Symptom**: Running the executable in `dist/WarframeTacticalAdvisor/WarframeTacticalAdvisor.exe` crashes immediately.
- **Solution**: Run the executable from PowerShell or command prompt to inspect the terminal crash logs. Ensure you have copied the `assets` folder, `src/resources/data`, `src/resources/themes`, and `src/resources/routes` next to the executable, as PyInstaller builds require these resource directories to render properly.

---

## 👥 Profile & Account Management

### Q: How do I switch between default and alternate accounts?
- **Option 1**: Go to the **Settings** tab in the main sidebar navigation, choose **Alt Account** or **Default Account** from the Active Account Profile dropdown, and click **Save Settings**.
- **Option 2**: Press `Ctrl+P` to open the VSCode-style Command Palette, type `Command: Switch Account to Alt` (or `Default`), and press Enter.

### Q: Why does the UI not update immediately when I switch profiles?
- **Solution**: Profile switches now automatically broadcast the `ACCOUNT_SWITCHED` event. This clears the thread-safe `QueryCache` layer and refreshes all active tabs instantly. If data appears stale, press `Ctrl+R` to force-refresh all dashboards.

---

## 🎮 Overlay HUD Mode

### Q: How do I open and close the overlay HUD?
- **Toggle ON**: Press `Ctrl+O` when the application is focused, or select **Overlay Mode (Ctrl+O)** from the **Windows** menu. The main window will hide and launch the overlay HUD in the top-right corner.
- **Toggle OFF/Restore**: Press `Ctrl+O`, `Esc`, or click the **Restore** button in the HUD header. This hides the overlay and restores the main companion window.

### Q: Can I move the overlay window?
- **Solution**: Yes. Click and hold the header bar containing the text `WARFRAME HUD ADVISOR` and drag it anywhere on your screen. This allows you to position it cleanly over your game window (configured in borderless windowed mode).

### Q: Why does the overlay show "World State unavailable"?
- **Solution**: The overlay requests Cetus cycles, fissures, and alerts from `api.warframestat.us`. If your PC is offline, or if the API is experiencing outages, it will gracefully show this warning. Ensure your internet connection is active.
