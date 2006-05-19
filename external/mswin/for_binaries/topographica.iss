; You will need to adjust the source paths (i.e. those currently beginning
; 'd:\program files\topographica') to wherever is the copy of Topographica
; that's being used to create the setup file.


[Setup]
AppName=Topographica
AppVerName=Topographica 0.8.3alpha
AppPublisher=Topographica development team
AppPublisherURL=http://www.topographica.org
AppSupportURL=http://www.topographica.org
AppUpdatesURL=http://www.topographica.org
ChangesAssociations=Yes
DefaultDirName={pf}\Topographica
DefaultGroupName=Topographica
LicenseFile=D:\Program Files\topographica\COPYING.txt
InfoBeforeFile=D:\Program Files\topographica\README.txt
OutputBaseFilename=setup
;; set to none when testing or you will be here a long time
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: desktopicon; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "D:\Program Files\topographica\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Topographica"; Filename: "{app}\topographica.bat"; WorkingDir: "{app}"; Parameters: "-g"; IconFilename: "{app}\topographica.ico"
Name: "{group}\Uninstall Topographica"; Filename: "{uninstallexe}"
Name: "{userdesktop}\Topographica"; Filename: "{app}\topographica.bat"; Parameters: "-g"; Tasks: desktopicon; IconFilename: "{app}\topographica.ico"


[Registry]
; ".myp" is the extension we're associating. "MyProgramFile" is the internal name for the file type as stored
; in the registry. Make sure you use a unique name for this so you don't inadvertently overwrite another
; application's registry key.
Root: HKCR; Subkey: ".ty"; ValueType: string; ValueName: ""; ValueData: "TopographicaScript"; Flags: uninsdeletevalue

;"My Program File" is the name for the file type as shown in Explorer.
Root: HKCR; Subkey: "TopographicaScript"; ValueType: string; ValueName: ""; ValueData: "Topographica Script"; Flags: uninsdeletekey

;"DefaultIcon" is the registry key that specifies the filename containing the icon to associate with the file type.
Root: HKCR; Subkey: "TopographicaScript\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\topographica.ico"

;"shell\open\command" is the registry key that specifies the program to execute when a file of the type is double-clicked in Explorer.
;The surrounding quotes are in the command line so it handles long filenames correctly.
Root: HKCR; Subkey: "TopographicaScript\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\topographica.bat"" -g ""%1"""



[Run]
; Run the python script to create 'topographica' python script and topographica.bat
Filename: "{app}\python_topo\python.exe"; Parameters: "setup.py ""{app}"""; WorkingDir: "{app}"; Flags: runhidden

; User gets to choose to run Topographica after installation
Filename: "{app}\topographica.bat"; Parameters: "-g"; Description: "{cm:LaunchProgram,Topographica}"; Flags: shellexec postinstall skipifsilent



[UninstallDelete]
; Files that get created outside this installation script (e.g. by setup.py)
; that we don't want to leave around after uninstallation.
;
; User-created files do not get removed.
; (CEBHACKALERT this includes leaving behind .pyc files.)
Type: filesandordirs; Name: "{app}\python_topo"
Type: files; Name: "{app}\topographica"
Type: files; Name: "{app}\topographica.bat"
