@echo off

REM *** SETUP THIS COPY OF TOPOGRAPHICA FOR MAKING A BINARY INSTALLATION ***
REM *** BE SURE YOU MEAN TO DO THIS TO YOUR COPY! ***

REM    - copies setup.py to root directory
REM    - cleans files that aren't needed for the binary version


REM Put the setup script into {topographica} 
copy ..\setup.py ..\..\..\


REM Clean this copy of Topographica...

REM ** root directory

cd ..\..\..
rmdir /Q /S CVS\
del /Q /F .cvsignore
del /Q /F Makefile
del /Q /F ChangeLog.txt
del /Q /F topographica
del /Q /F topographica.bat
del /Q /F setup.bat

REM ** external\

cd external\
rmdir /Q /S CVS\
del /Q /F *
rmdir /Q /S win32

cd mswin\
rmdir /Q /S CVS\
rmdir /Q /S util\
del /Q /F *


REM ** doc\
cd ..\..\
REM CEBHACKALERT: it would be good to get the built doc files in here!


REM ** etc\
cd etc\
rmdir /Q /S CVS
del /Q /F .cvsignore
cd ..


REM ** examples\
cd examples\
rmdir /Q /S CVS
del /Q /F .cvsignore
cd ..

REM ** topo\
cd topo\
rmdir /Q /S CVS
del /Q /F .cvsignore
cd ..

REM CEBHACKALERT: how on Windows does one recursively delete?
REM We need to remove all pyc files plus the CVS files
