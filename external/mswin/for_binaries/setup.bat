@echo off

REM Called by installation program after it's done copying files.


cd ..
set instdir=%CD%
python_topo\python.exe setup\setup.py "%instdir%"