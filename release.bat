@echo off
echo ========================================================
echo Warframe Tactical Advisor v1.0 Release Packaging Script
echo ========================================================

echo 1. Updating Metadata Version...
python -c "import json; f = open('src/resources/data/metadata.json', 'r+'); d = json.load(f); d['version'] = '1.0.0'; d['updated'] = '2026-06-28'; f.seek(0); json.dump(d, f, indent=4); f.truncate()"


echo 2. Packaging WTA Application using PyInstaller...
python -m PyInstaller --noconfirm --onedir --windowed --name=WarframeTacticalAdvisor --icon=assets/icon.ico main.py

echo 3. Compiling Installer Package (Inno Setup)...
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" installer\setup.iss
) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    "%ProgramFiles%\Inno Setup 6\ISCC.exe" installer\setup.iss
) else (
    echo Warning: Inno Setup ISCC compiler not found. Portable build is available in dist\WarframeTacticalAdvisor\
)

echo Done! Release build completed successfully.
