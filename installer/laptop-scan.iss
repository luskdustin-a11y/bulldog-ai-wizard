; Standalone installer for the read-only Archie Laptop Scan. Separate from Archie: own AppId, own folder, no shared data.
#ifndef MyAppVersion
#define MyAppVersion "1.0.0"
#endif
[Setup]
AppId={{2AD8F4F4-50F5-490B-A447-7054F67C07E1}
AppName=Archie Laptop Scan
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\Programs\ArchieLaptopScan
DefaultGroupName=Archie Laptop Scan
OutputDir=output
OutputBaseFilename=ArchieLaptopScan-Setup
PrivilegesRequired=lowest
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\ArchieLaptopScan.exe
DisableProgramGroupPage=yes
[Files]
Source: "..\dist\ArchieLaptopScan.exe"; DestDir: "{app}"; Flags: ignoreversion
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked
[Icons]
Name: "{group}\Archie Laptop Scan"; Filename: "{app}\ArchieLaptopScan.exe"
Name: "{userdesktop}\Archie Laptop Scan"; Filename: "{app}\ArchieLaptopScan.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\ArchieLaptopScan.exe"; Description: "Run the scan now"; Flags: postinstall nowait skipifsilent
