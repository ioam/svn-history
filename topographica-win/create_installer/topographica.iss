; Takes the topographica directory and makes a setup.exe out of it, as well
; as setting up file associations etc.
; Also adds uninstall information.
;
; See readme.txt for how to use.
;
; adjust items marked with *** to match your setup

[Setup]
AppName=Topographica
AppVerName=Topographica 0.9.0
AppPublisher=Topographica development team
AppPublisherURL=http://www.topographica.org
AppSupportURL=http://www.topographica.org
AppUpdatesURL=http://www.topographica.org
ChangesAssociations=Yes
DefaultDirName={pf}\Topographica
DefaultGroupName=Topographica
; ***
LicenseFile=D:\Program Files\topographica\COPYING.txt
; ***
InfoBeforeFile=D:\Program Files\topographica\README.txt
OutputBaseFilename=setup
; set to none when testing or you will be here a long time
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: desktopicon; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; ***
Source: "D:\Program Files\topographica\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Topographica"; Filename: "{app}\topographica.bat"; WorkingDir: "{app}"; Parameters: "-g"; IconFilename: "{app}\topographica.ico"
Name: "{group}\Uninstall Topographica"; Filename: "{uninstallexe}"
Name: "{userdesktop}\Topographica"; Filename: "{app}\topographica.bat"; Parameters: "-g"; Tasks: desktopicon; IconFilename: "{app}\topographica.ico"


[Registry]
; add the .ty file type to the registry as TopographicaScript
Root: HKCR; Subkey: ".ty"; ValueType: string; ValueName: ""; ValueData: "TopographicaScript"; Flags: uninsdeletevalue

; TopographicaScript will display as "Topographica Script" to users
Root: HKCR; Subkey: "TopographicaScript"; ValueType: string; ValueName: ""; ValueData: "Topographica Script"; Flags: uninsdeletekey

; a TopographicaScript is associated with the topographica icon
Root: HKCR; Subkey: "TopographicaScript\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\topographica.ico"

; when a TopographicaScript is double clicked etc, this is what gets run
Root: HKCR; Subkey: "TopographicaScript\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\topographica.bat"" -g ""%1"""

; CEBHACKALERT: it would be nice also to associate the icon topographica.ico with topographica.bat, but I don't know
; how to do this.


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
; CEBHACKALERT: shouldn't delete any files modified by user.
Type: filesandordirs; Name: "{app}\python_topo"
Type: files; Name: "{app}\topographica"
Type: files; Name: "{app}\topographica.bat"
