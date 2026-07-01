; Inno Setup script for Inventory Beta
; Download Inno Setup from https://jrsoftware.org/isdl.php
; To compile: right-click this file -> "Compile" (or run: iscc installer.iss)

#define MyAppName "Inventory Beta"
#define MyAppVersion "1.4.0"
#define MyAppPublisher "Inventory Pro"
#define MyAppURL ""
#define MyAppExeName "Inventory_Beta.exe"

[Setup]
AppId={{B8A3C2E1-4D5F-4A6B-9C7D-8E2F1A3B4C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Use the project's icon for the installer
SetupIconFile=assets\icons\app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
OutputDir=dist
OutputBaseFilename=Inventory_Beta_Setup
; The app stores data in {app}\data\ so we need write access
DisableDirPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce

[Files]
; Main executable
Source: "dist\Inventory_Beta\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Internal dependencies (PyInstaller bundle)
Source: "dist\Inventory_Beta\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
; Logs directory
Source: "dist\Inventory_Beta\logs\*"; DestDir: "{app}\logs"; Flags: ignoreversion recursesubdirs createallsubdirs
; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; Ensure data directory exists and is writable
Name: "{app}\data"; Permissions: users-modify
Name: "{app}\logs"; Permissions: users-modify

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
; Launch app after install (optional)
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Registry]
; Store install path so the app can find its data directory
Root: "HKCU"; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
