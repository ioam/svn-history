@ECHO OFF
ECHO This will install Topographica and its package dependencies.

REM Developer's Note: Install Python then call the setup.py script
REM inside the external/win32 directory.
REM $Id: setup.bat,v 1.6 2004/06/30 15:43:59 judah Exp $

external\win32\util\Y_OR_N /Q /A "Do you wish to continue? [Y/n]"

IF ERRORLEVEL 3 GOTO :INSTALL
IF ERRORLEVEL 2 GOTO :EXIT
IF ERRORLEVEL 1 GOTO :INSTALL


:INSTALL
ftype Python.File | findstr "Python.File="
IF ERRORLEVEL 1 GOTO :INSTALL_PYTHON
IF ERRORLEVEL 0 GOTO :RUN_SETUP


:INSTALL_PYTHON
ECHO Python file associations not detected: Installing Python 2.4
start /wait external\win32\python-2.4.msi


:RUN_SETUP
cd external\win32
cd
start /wait setup.py configure
start /wait setup.py install

:EXIT
ECHO Install Complete
