' Create a link to Topographica
' based on information and sample in "Windows 2000 Scripting Guide"
' http://www.microsoft.com/technet/scriptcenter/guide/sas_wsh_aytf.mspx


Function CreateShortcut(topo_dir)
Set objShell = WScript.CreateObject("WScript.Shell")
strDesktopFolder = objShell.SpecialFolders("Desktop")
Set objShortCut = objShell.CreateShortcut(strDesktopFolder & "\Topographica.lnk")

objShortCut.TargetPath = topo_dir & "\topographica.bat"
objShortCut.Arguments = "-g"
objShortCut.WorkingDirectory = topo_dir
objShortCut.Description = "Run Topographica"
objShortCut.IconLocation = topo_dir & "\topographica.ico"
objShortCut.Save
End Function



CreateShortcut(WScript.Arguments.Item(0))