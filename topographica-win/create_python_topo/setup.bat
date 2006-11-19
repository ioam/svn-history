@echo off
REM assumes we're going to c:\Python24

set startdir=%CD%

..\util\gunzip -c ..\..\external\Pmw.tgz > ..\..\external\Pmw.tar
..\util\tar xvf ..\..\external\Pmw.tar
copy ..\..\external\Pmw .


..\util\gunzip weave.tar.gz
..\util\tar xvf weave.tar
..\util\gunzip scipy_test.tar.gz
..\util\tar xvf scipy_test.tar



cd ..
xcopy /E /I create_python_topo c:\create_python_topo
xcopy /E /I util c:\create_python_topo\util
REM CEBHACKALERT: because the msi won't run from this directory, at least
REM on my PC! Why? Is it a path problem?
c:
cd \
cd create_python_topo


start /w msiexec /i python-2.4.2.msi ALLUSERS=0 TARGETDIR=c:\python24 ADDLOCAL=DefaultFeature,TclTk
start /w Numeric-24.2.win32-py2.4.exe
start /w matplotlib-0.81.win32-py2.4.exe
start /w PIL-1.1.5.win32-py2.4.exe
REM start /w scipy-0.5.1.win32-py2.4.exe

move Pmw c:\python24\Lib\site-packages

REM this is weave that I think I compiled with mingw from
REM scipy 0.3.2, since none was already compiled for 
REM python 2.4 and Numeric 24. The way scipy is organized
REM has changed in later releases (notably weave has changed location; 
REM when topographica
REM switches to use a recent scipy, we should just be able
REM to use the scipy*.exe provided online (as for Numeric, etc).
REM and remove these.
move weave c:\python24\Lib\site-packages
move scipy_test c:\python24\Lib\site-packages


REM ** For fixedpoint, the patched version from unix is used.
REM ** CEBHACKALERT: use the patch executable in utils to create the
REM patch from the diff and fixedpoint.tgz file in external\
move fixedpoint-0.1.2_patched.py c:\python24\Lib\site-packages\fixedpoint.py


xcopy /E /I mingw c:\python24\mingw\
util\gunzip c:\python24\mingw\*.gz 
copy util\tar.exe c:\python24\mingw

cd \python24\mingw
tar xvf "c:\python24\mingw\gcc-core-3.4.2-20040916-1.tar" 
tar xvf "c:\python24\mingw\gcc-g++-3.4.2-20040916-1.tar" 
tar xvf "c:\python24\mingw\gcc-g77-3.4.2-20040916-1.tar" 
tar xvf "c:\python24\mingw\w32api-3.6.tar" 
tar xvf "c:\python24\mingw\mingw-runtime-3.9.tar" 
tar xvf "c:\python24\mingw\binutils-2.15.91-20040904-1.tar" 
del *.tar
del tar.exe

cd ..\..

rmdir /Q /S create_python_topo

echo.
echo.
echo Now test this has worked by renaming c:\Python24 to c:\python_topo 
echo and replacing your copy of Topographica's python_topo with this new one.
echo.
echo If successful, tar.gz this python_topo and add it to cvs at
echo topographica-win\common\python_topo.tar.gz.
echo.
echo.
pause
