; You will need to adjust the source paths (i.e. those currently beginning
; 'd:\program files\topographica') to wherever is the copy of Topographica
; that's being used to create the setup file.


[Setup]
AppName=Topographica
AppVerName=Topographica 0.8
AppPublisher=Topographica development team
AppPublisherURL=http://www.topographica.org
AppSupportURL=http://www.topographica.org
AppUpdatesURL=http://www.topographica.org
DefaultDirName={pf}\Topographica
DefaultGroupName=Topographica
LicenseFile=D:\Program Files\topographica\COPYING.txt
InfoBeforeFile=D:\Program Files\topographica\README.txt
InfoAfterFile=D:\Program Files\topographica\ChangeLog.txt
OutputBaseFilename=setup
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "D:\Program Files\topographica\topographica.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\Program Files\topographica\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Topographica"; Filename: "{app}\topographica.ico"
;Name: "{userdesktop}\Topographica"; Filename: "{app}\topographica.bat"; Tasks: desktopicon

[Run]
Filename: "{app}\setup\setup.bat"; WorkingDir: "{app}\setup"; Flags: runhidden
Filename: "{app}\topographica.bat"; Description: "{cm:LaunchProgram,Topographica}"; Flags: shellexec postinstall skipifsilent

