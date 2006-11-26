@echo off


REM check user wants to go ahead
 :start
echo This script will turn this copy of Topographica into one
echo suitable for binary distribution.
echo.
echo ** BE SURE YOU WANT TO DO THIS TO YOUR COPY OF TOPOGRAPHICA **
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

REM - copies setup.py to root directory
REM - cleans files that aren't needed for the binary version

REM Put the setup script, Topographica icon, and installation
REM script file into the topographica directory (for use while 
REM creating setup.exe file)
copy ..\common\setup.py ..\..
copy ..\common\topographica.ico ..\..
copy ..\create_installer\topographica.iss ..\..


REM Clean this copy of Topographica...

cd ..\..

REM not using the makefile...
del /Q /F Makefile

REM delete files created by setup_cvs_copy\setup.bat
del /Q /F topographica
del /Q /F topographica.bat


REM **** Things the Makefile deletes
del /S /Q /F .#* *~ .cvsignore ChangeLog.txt *\.cvsignore *\*\.cvsignore
del etc\topographica.elc ImageSaver*.ppm countalerts* annotate.out
del examples\disparity_energy.ty
del examples\homeostatic.ty
del examples\joublin_bc96.ty
del examples\laminar.ty*
del examples\laminar_lissom.ty
del examples\laminar_nolearning.ty
del examples\leaky_lissom_or.ty
del examples\lissom_oo_od.ty
del examples\lissom_oo_or_dy_photo.ty
del examples\lissom_oo_or_homeomaxent.ty
del examples\lissom_or_homeomaxent.ty
del examples\lissom_or_homeoscale.ty
del examples\lissom_or_noshrinking.ty
del examples\lissom_or_noshrinking_latswitch.ty
del examples\lissom_or_sf.ty
del examples\ohzawa_science90.ty
del examples\sullivan_neurocomputing04.ty
del examples\sullivan_neurocomputing06.ty

rmdir /Q /S tmp\
REM CEBHACKALERT: need to delete CVS/ dirs recursively

rmdir /Q /S CVS
cd examples\
rmdir /Q /S CVS
cd ..
cd etc\
rmdir /Q /S CVS
cd ..
cd topo\
rmdir /Q /S CVS
cd ..
REM **** end things the Makefile deletes


print %cd%
REM ** delete external/
rmdir /Q /S external

REM ** delete .pyc files
del /S /Q /F *.pyc

REM ** Finally, remove topographica-win\
REM (includes this file!)
rmdir /Q /S topographica-win




:end