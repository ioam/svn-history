@echo off

REM Called by installation program after it's done copying files.


cd ..
set instdir=%CD%
python_topo\python.exe setup\setup.py "%instdir%"

del /Q /F create_shortcut.vbs
rmdir /Q /S setup\