; build_installer.iss — Inno Setup script
[Setup]
AppName=SOS Button
AppVersion=1.0.0
AppPublisher=Intamia LLC
DefaultDirName={pf}\SOS Button
DefaultGroupName=SOS Button
UninstallDisplayIcon={app}\SOS_Button_App.exe
OutputDir=dist\installer
OutputBaseFilename=SOS_Button_Installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=assets\sos_icon.ico
WizardStyle=modern

[Files]
Source: "dist\SOS_Button_App\SOS_Button_App.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "_validation\*"; DestDir: "{app}\_validation"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\SOS Button"; Filename: "{app}\SOS_Button_App.exe"
Name: "{autodesktop}\SOS Button"; Filename: "{app}\SOS_Button_App.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional Icons:"

[Run]
Filename: "{app}\SOS_Button_App.exe"; Description: "Launch SOS Button"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{sys}\taskkill.exe"; Parameters: "/IM SOS_Button_App.exe /F"; Flags: runhidden
