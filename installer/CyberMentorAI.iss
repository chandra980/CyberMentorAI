#define MyAppName "CyberMentor AI"
#define MyAppVersion "3.1.0"
#define MyAppPublisher "Chandra Kumar Yadav"
#define MyAppExeName "CyberMentorAI.exe"

[Setup]
AppId={{B707C7C5-04BD-4A11-A8FA-2E3E3C2A6D9E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/chandra980/CyberMentorAI
AppSupportURL=https://github.com/chandra980/CyberMentorAI/issues
AppUpdatesURL=https://github.com/chandra980/CyberMentorAI/releases/latest
DefaultDirName={autopf}\CyberMentor AI
DefaultGroupName=CyberMentor AI
OutputDir=output
OutputBaseFilename=CyberMentorAI-Setup-Windows
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
WizardStyle=modern
SetupIconFile=..\assets\CyberMentorAI.ico
UninstallDisplayName=CyberMentor AI
SetupLogging=yes

[Files]
Source: "..\dist\CyberMentorAI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\cybermentor.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\cybermentor-backend.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\CyberMentor AI"; Filename: "{app}\CyberMentorAI.exe"
Name: "{autodesktop}\CyberMentor AI"; Filename: "{app}\CyberMentorAI.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\CyberMentorAI.exe"; Description: "Launch CyberMentor AI"; Flags: nowait postinstall skipifsilent
