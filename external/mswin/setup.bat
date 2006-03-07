@echo off

REM Note that this script assumes it's starting two levels 
REM above the topographica directory.

echo.
echo Topographica installation script
echo --------------------------------
echo.

set installed="False"

REM get directories
set startdir=%CD%
cd ..\..
set instdir=%CD%
cd %startdir%

REM check user wants to go ahead
 :start
echo This script will: 
echo - install Topographica to %instdir%,
echo - associate '.ty' files with Topographica.
echo.
set choice=
set /p choice=Enter '1' to proceeed or '2' to quit:
if not '%choice%'=='' set choice=%choice:~0,1%
if '%choice%'=='1' goto install
if '%choice%'=='2' goto end
echo "%choice%" is not valid; please enter '1' or '2'
echo.
goto start


:install
REM unzip and untar, leaving original gz file alone
echo.
echo Unpacking and installing Python...
util\gunzip -c python_topo.tar.gz > python_topo.tar
util\tar xvf python_topo.tar
del /F python_topo.tar

REM move the python stuff to the topographica directory
move /Y python_topo ..\..\

REM create startup scripts for Topographica
echo.
echo Creating startup scripts and file association...
..\..\python_topo\python.exe setup.py "%instdir%"
set installed="True"
goto end


:end
echo.
echo Topographica setup script finished.
echo.
if %installed%=="False" goto exit
cd ..\..
echo To start, type 'topographica' at a command prompt,
echo or 'topographica -g' to get a graphical interface.
echo.
echo Alternatively, double click on one of the 
echo networks in the examples directory.
echo.
echo.

:exit
echo.
pause
echo.
