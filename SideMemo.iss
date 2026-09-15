[Setup]
AppName=SideMemo
AppVersion=1.0.3
DefaultDirName={autopf}\SideMemo
DefaultGroupName=SideMemo
OutputDir=installer
OutputBaseFilename=SideMemo-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=app.ico
UninstallDisplayIcon={app}\SideMemo.exe

[Tasks]
Name: "desktopicon"; Description: "바탕 화면 바로가기 만들기"; GroupDescription: "추가 바로가기:"

[Files]
; PyInstaller one-folder build: preserve the EXE and its _internal runtime folder.
Source: "dist\SideMemo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SideMemo"; Filename: "{app}\SideMemo.exe"
Name: "{autodesktop}\SideMemo"; Filename: "{app}\SideMemo.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SideMemo.exe"; Description: "SideMemo 실행"; Flags: nowait postinstall skipifsilent
