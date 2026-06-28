; Inno Setup Script for Warframe Tactical Advisor v1.0
[Setup]
AppName=Warframe Tactical Advisor
AppVersion=1.0.0

DefaultDirName={autopf}\Warframe Tactical Advisor
DefaultGroupName=Warframe Tactical Advisor
UninstallDisplayIcon={app}\WarframeTacticalAdvisor.exe
Compression=lzma2
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=Warframe Tactical Advisor Setup
SetupIconFile=assets\icon.ico
WizardStyle=modern

[Files]
Source: "dist\WarframeTacticalAdvisor.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "src\resources\data\*"; DestDir: "{app}\src\resources\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "src\resources\themes\*"; DestDir: "{app}\src\resources\themes"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "src\resources\routes\*"; DestDir: "{app}\src\resources\routes"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "build_library\*"; DestDir: "{app}\build_library"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "plugins\examples\*"; DestDir: "{app}\plugins\examples"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "src\resources\packs\*"; DestDir: "{app}\src\resources\packs"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Warframe Tactical Advisor"; Filename: "{app}\WarframeTacticalAdvisor.exe"; IconFilename: "{app}\assets\icon.ico"
Name: "{autodesktop}\Warframe Tactical Advisor"; Filename: "{app}\WarframeTacticalAdvisor.exe"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
Filename: "{app}\WarframeTacticalAdvisor.exe"; Description: "{cm:LaunchProgram,Warframe Tactical Advisor}"; Flags: nowait postinstall skipifsilent
