; Takes the topographica directory and makes a setup.exe out of it, as well
; as setting up file associations, uninstall information, etc.
;
; INSTRUCTIONS
; (1) copy msvcp71.dll & msvcr71.dl from the windows system32 dir (e.g c:\windows\system32\)
;     into the distribution's python_topo\ directory
; (1) adjust the paths marked *** to match those on your system
; (2) for testing, change 'lzma' to 'none' (unless you are really patient)
; (3) choose 'compile' from the 'build' menu
; (4) you should get a setup.exe file in a newly created 'Output' directory at the same level as topographica.iss.
; (5) test setup.exe on another copy of Windows (or lots of other copies...)
; (6) change 'lzma' back to 'none', repeat (3)
; (7) rename the resulting setup.exe to topographica-X.exe, where X is the version number
; (8) upload to sf.net
; (9) update sf.net Windows download page so that the primary file is the new version


[Setup]
AppName=Topographica
AppVerName=Topographica 0.9.7
AppPublisher=Topographica development team
AppPublisherURL=http://www.topographica.org
AppSupportURL=http://www.topographica.org
AppUpdatesURL=http://www.topographica.org
ChangesAssociations=Yes
DefaultDirName={pf}\Topographica
DefaultGroupName=Topographica
; ***
LicenseFile=C:\topographica.exe\topographica-0.9.6\distributions\topographica-0.9.6\COPYING.txt
; ***
InfoBeforeFile=C:\topographica.exe\topographica-0.9.6\distributions\topographica-0.9.6\README.txt
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
Source: "C:\topographica.exe\topographica-0.9.6\distributions\topographica-0.9.6\python_topo\msvcp71.dll"; DestDir: "{sys}"; Flags: onlyifdoesntexist uninsneveruninstall sharedfile
; ***
Source: "C:\topographica.exe\topographica-0.9.6\distributions\topographica-0.9.6\python_topo\msvcr71.dll"; DestDir: "{sys}"; Flags: onlyifdoesntexist uninsneveruninstall sharedfile
; ***
Source: "C:\topographica.exe\topographica-0.9.6\distributions\topographica-0.9.6\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Topographica"; Filename: "{app}\topographica.bat"; WorkingDir: "{app}"; Parameters: "-g"; IconFilename: "{app}\topographica.ico"
Name: "{group}\Uninstall Topographica"; Filename: "{uninstallexe}"
Name: "{userdesktop}\Topographica"; Filename: "{app}\topographica.bat"; WorkingDir: "{app}"; Parameters: "-g"; Tasks: desktopicon; IconFilename: "{app}\topographica.ico"


[Code]
// runs BEFORE anything else
function InitializeSetup(): Boolean;
begin
  // if msvcr71.dll and msvcp71.dll are missing, and user isn't admin/power, abort installation
  Result := FileExists(ExpandConstant('{sys}\msvcr71.dll')) AND FileExists(ExpandConstant('{sys}\msvcp71.dll'));
  if Result = False then
    if IsAdminLoggedOn() or IsPowerUserLoggedOn() then
      Result := True
      
  if Result = False then
    MsgBox('Your system is missing some Windows system files required for Topographica; for these to be added, the installation must be run as a Power User or Administrator.' #13#13 'Please re-run the Topographica installation as a user with sufficient privileges.', mbError, MB_OK);
end;


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
