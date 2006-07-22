@echo off

REM *****************************************************
REM Script to setup a CVS-controlled copy of Topographica
REM *****************************************************

REM Note: this script assumes it's starting two levels 
REM above the topographica directory (currently
REM topographica/topographica-win/setup_cvs_copy/)

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
echo - install Topographica to %instdir%;

REM these could be optional!
echo - associate '.ty' files with Topographica;
echo - put a shortcut to Topographica on your desktop.
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
echo * Unpacking and installing Python...
..\util\gunzip -c ..\common\python_topo.tar.gz > ..\common\python_topo.tar
..\util\tar xvf ..\common\python_topo.tar

REM doesn't work?
del /F ..\common\python_topo.tar
pause

REM move the python stuff to the topographica directory
move /Y python_topo ..\..\

REM copy the icon to the topographica directory
copy ..\common\topographica.ico ..\..

REM create startup scripts for Topographica
echo.
echo * Creating scripts and file association...
..\..\python_topo\python.exe ..\common\setup.py "%instdir%" "create_associations"

set installed="True"
goto end


:end
echo.
echo * Topographica setup script finished
echo.
if %installed%=="False" goto exit
cd ..\..
echo To start, double click the 'Topographica' icon on
echo your desktop, or one of the networks in the examples
echo directory.
echo.
echo Alternatively, type 'topographica' at a command prompt
echo in the Topographica directory (or 'topographica -g' to 
echo get a graphical interface).
echo.
echo.

:exit
echo.
pause
echo.
