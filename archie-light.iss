#define MyAppName "Archie Light"
#define MyAppVersion "0.6.0"
[Setup]
AppId={{B9C1A5E2-4F71-4C35-A4D1-AB51C2E6E060}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\Archie Light
DefaultGroupName=Archie Light
OutputDir=output
OutputBaseFilename=Archie-Light-Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no
UninstallDisplayIcon={app}\ARCHER.exe
[Files]
Source: "installer-stage\ARCHER.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer-stage\ollama\*"; DestDir: "{app}\ollama"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "installer-stage\models\*"; DestDir: "{commonappdata}\BulldawgAI\models"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{autoprograms}\Archie Light"; Filename: "{app}\ARCHER.exe"
Name: "{autodesktop}\Archie Light"; Filename: "{app}\ARCHER.exe"; Tasks: desktopicon
[Tasks]
Name: desktopicon; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"
[Run]
Filename: "{app}\ARCHER.exe"; Description: "Launch Archie Light"; Flags: nowait postinstall skipifsilent
[UninstallDelete]
Type: filesandordirs; Name: "{app}\ollama"
