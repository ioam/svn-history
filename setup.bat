@ECHO OFF
ECHO This will install Topographica and its package dependencies.

REM Developer's Note: Install Python then call the setup.py script
REM inside the external/win32 directory.
REM $Id: setup.bat,v 1.4 2004/06/30 14:57:55 judah Exp $

external\win32\util\Y_OR_N /Q /A "Do you wish to continue? [Y/n]"

IF ERRORLEVEL 3 GOTO :INSTALL
IF ERRORLEVEL 2 GOTO :EXIT
IF ERRORLEVEL 1 GOTO :INSTALL


:INSTALL
ftype Python.File | findstr "Python.File="
IF ERRORLEVEL 1 GOTO :INSTALL_PYTHON
IF ERRORLEVEL 0 GOTO :RUN_SETUP


:INSTALL_PYTHON
ECHO Python file associations not detected: Installing Python 2.3
start /wait external/win32/Python-2.3.4.exe


:RUN_SETUP
cd external/win32
start /wait setup.py configure
start /wait setup.py install
cd ../..
copy topographica-script.py topographica.py

:EXIT
ECHO Install Complete
