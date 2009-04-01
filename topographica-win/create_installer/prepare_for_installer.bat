@echo off


REM check user wants to go ahead
 :start
echo This script will turn this copy of Topographica into one
echo suitable for binary distribution. 
echo
echo ** ENSURE YOU HAVE READ THE CONTENTS OF README.txt **
echo.
echo.
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

REM Put the setup script, Topographica icon, and installation
REM script file into the topographica directory (for use while 
REM creating setup.exe file)
copy ..\common\setup.py ..\..
copy ..\common\topographica.ico ..\..
copy ..\create_installer\topographica.iss ..\..


REM Clean this copy of Topographica (beyond what Makefile's clean did)...

cd ..\..

REM not using the makefile...
del /Q /F Makefile

del /Q /F topographica.bat

REM ** delete external/
rmdir /Q /S external

REM ** Finally, remove topographica-win\
REM (includes this file!)
rmdir /Q /S topographica-win


:end