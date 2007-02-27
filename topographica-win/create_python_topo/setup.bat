@echo off

REM still to add: libsndfile, pyaudiolab, mlabwrap


REM Assumes we're going to c:\Python24; be careful to update everything if you decide to
REM change this.

set startdir=%CD%


REM ** GRAB PACKAGES IN COMMON WITH topographica\external
REM Pmw
..\util\gunzip -c ..\..\external\Pmw.tgz > ..\..\external\Pmw.tar
..\util\tar xvf ..\..\external\Pmw.tar
copy ..\..\external\Pmw .
REM Gnosis_Utils
..\util\gunzip -c ..\..\external\Gnosis_Utils-1.2.1.tar.gz > ..\..\external\Gnosis_Utils-1.2.1.tar
..\util\tar xvf ..\..\external\Gnosis_Utils-1.2.1.tar
copy ..\..\external\Gnosis_Utils-1.2.1 .
REM REM pyaudiolab
REM ..\util\gunzip -c ..\..\external\pyaudiolab-0.6.6.tar.gz > ..\..\external\pyaudiolab-0.6.6.tar
REM ..\util\tar xvf ..\..\external\pyaudiolab-0.6.6.tar
REM copy ..\..\external\pyaudiolab-0.6.6 .

REM REM CEBALERT: this should be down with the libfile
REM REM section, but by then I've lost track of where gunzip is!
REM ..\util\gunzip -c libsndfile-1.0.17.tar.gz > libsndfile-1.0.17.tar
REM ..\util\tar xvf libsndfile-1.0.17.tar



cd ..

REM CEBALERT: because of some path trouble with some of the installation
REM programs, we move to working in c:\create_python_topo.
xcopy /E /I create_python_topo c:\create_python_topo
xcopy /E /I util c:\create_python_topo\util
c:
cd \
cd create_python_topo


REM ** INSTALL PACKAGES

REM * python,tcl/tk
start /w msiexec /i python-2.4.4.msi ALLUSERS=0 TARGETDIR=c:\python24 ADDLOCAL=DefaultFeature,TclTk

REM * numpy
start /w numpy-1.0.1.win32-py2.4.exe

REM * matplotlib
start /w matplotlib-0.90.0.win32-py2.4.exe

REM * PIL
start /w PIL-1.1.5.win32-py2.4.exe

REM * scipy
start /w scipy-0.5.2.win32-py2.4.exe

REM * PMW
move Pmw c:\python24\Lib\site-packages

REM * gnosis
cd Gnosis_Utils-1.2.1\
c:\python24\python.exe setup.py install
cd ..

REM REM * ctypes
REM start /w ctypes-1.0.1.win32-py2.4.exe
REM 
REM REM * libsndfile
REM move libsndfile-1.0.17\* c:\python24\libs

REM REM * pyaudiolab
REM REM cd pyaudiolab-0.6.6
REM REM c:\python24\python.exe setup.py install
REM cd ..

REM CEBHACKALERT: add the jpeg package 


REM * weave
REM we just take it from scipy, since it's not available
REM separately as a binary (unless we ourselves build it).
xcopy /E /I c:\python24\Lib\site-packages\scipy\weave c:\python24\Lib\site-packages\weave


REM ** For fixedpoint, the patched version from unix is used.
REM ** CEBALERT: use the patch executable in utils to create the
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
