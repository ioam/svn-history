@echo off

REM *** SETUP THIS COPY OF TOPOGRAPHICA FOR MAKING A BINARY INSTALLATION ***
REM *** BE SURE YOU MEAN TO DO THIS TO YOUR COPY! ***

REM    - copies setup.py to root directory
REM    - cleans files that aren't needed for the binary version


REM Put the setup script into {topographica} 
copy ..\setup.py ..\..\..\


REM Clean this copy of Topographica...

cd ..\..\..

REM not using the makefile...
del /Q /F Makefile

REM delete files created by setup
del /Q /F topographica
del /Q /F topographica.bat


REM **** Things the Makefile deletes
del /S /Q /F .#* *~ .cvsignore ChangeLog.txt
del etc/topographica.elc
del ImageSaver*.ppm
del countalerts*
del annotate.out
del examples\disparity_energy.ty
del examples\homeostatic.ty
del examples\joublin_bc96.ty
del examples\laminar.ty*
del examples\laminar_lissom.ty
del examples\laminar_nolearning.ty
del examples\leaky_lissom_or.ty
del examples\lissom_or_sf.ty
del examples\tiny.ty

REM ** remove external\
cd external\
del /Q /F *
rmdir /Q /S win32

REM don't delete all of external\mswin yet!
cd mswin\
rmdir /Q /S util\
del /Q /F *

cd ..\..

del /Q /F setup.bat
REM don't delete topographica.ico
rmdir /Q /S tmp\
REM CEBHACKALERT: need to delete CVS/ dirs automatically

rmdir /Q /S CVS\
cd examples\
rmdir /Q /S CVS\
cd ..
cd etc\
rmdir /Q /S CVS\
cd ..
cd topo\
rmdir /Q /S CVS\
cd ..
REM **** end things the Makefile deletes


REM ** delete .pyc files
del /S /Q /F *.pyc



