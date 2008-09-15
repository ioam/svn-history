@echo off

REM Assumes we're going to c:\Python25; be careful to update everything if you decide to
REM change this. (Should have used a variable, but that can't cover the graphical installs)

set startdir=%CD%

REM ** GRAB PACKAGES IN COMMON WITH topographica\external

REM numpy.diff
copy ..\..\external\numpy.diff .

REM Gnosis_Utils
..\util\gunzip -c ..\..\external\Gnosis_Utils-1.2.1.tar.gz > ..\..\external\Gnosis_Utils-1.2.1.tar
..\util\tar xvf ..\..\external\Gnosis_Utils-1.2.1.tar
copy ..\..\external\Gnosis_Utils-1.2.1 .



cd ..

REM CEBALERT: because of some path trouble with some of the installation
REM programs, we move to working in c:\create_python_topo.
xcopy /E /I create_python_topo c:\create_python_topo
xcopy /E /I util c:\create_python_topo\util
c:
cd \
cd create_python_topo


REM ** INSTALL PACKAGES

REM osx_skip_tk python jpeg pil numpy matplotlib weave fixedpoint pychecker common pylint epydoc docutils gnosis ipython gmpy tilewrapper scrodget tooltip
REM binary:
REM python jpeg pil numpy matplotlib weave(scipy) 


REM * python,tcl/tk
start /w msiexec /i python-2.5.1.msi ALLUSERS=0 TARGETDIR=c:\python25 ADDLOCAL=DefaultFeature,TclTk

REM * numpy
start /w numpy-1.1.1-win32-superpack-python2.5.exe

REM patch numpy
set storecpt=%cd%
cd c:\python25\Lib\site-packages
%storecpt%\util\patch.exe -p0 < %storecpt%\numpy.diff
cd %storecpt%

REM * matplotlib
start /w matplotlib-0.91.4.win32-py2.5.exe

REM * scipy
start /w scipy-0.6.0.win32-py2.5.exe

REM * gnosis
cd Gnosis_Utils-1.2.1\
c:\python25\python.exe setup.py install
cd ..

REM * weave
REM we just take it from scipy, since it's not available
REM separately as a binary 
xcopy /E /I c:\python25\Lib\site-packages\scipy\weave c:\python25\Lib\site-packages\weave


REM ** For fixedpoint, the patched version from unix is used.
REM ** CEBALERT: use the patch executable in utils to create the
REM patch from the diff and fixedpoint.tgz file in external\
move fixedpoint-0.1.2_patched.py c:\python25\Lib\site-packages\fixedpoint.py


xcopy /E /I mingw c:\python25\mingw\
util\gunzip c:\python25\mingw\*.gz 
copy util\tar.exe c:\python25\mingw

cd \python25\mingw
tar xvf "c:\python25\mingw\gcc-core-3.4.2-20040916-1.tar" 
tar xvf "c:\python25\mingw\gcc-g++-3.4.2-20040916-1.tar" 
tar xvf "c:\python25\mingw\gcc-g77-3.4.2-20040916-1.tar" 
tar xvf "c:\python25\mingw\w32api-3.6.tar" 
tar xvf "c:\python25\mingw\mingw-runtime-3.9.tar" 
tar xvf "c:\python25\mingw\binutils-2.15.91-20040904-1.tar" 
del *.tar
del tar.exe

cd ..\..

rmdir /Q /S create_python_topo

echo.
echo.
echo Now test this has worked by renaming c:\Python25 to c:\python_topo 
echo and replacing your copy of Topographica's python_topo with this new one.
echo To be sure this copy works correctly, you should make sure any other
echo copy of Topographica is uninstalled first (or try on a computer that does
echo not have Python installed).
echo.
echo If successful, tar.gz this python_topo and add it to cvs at
echo topographica-win\common\python_topo.tar.gz.
echo.
echo.
echo.
echo ** Before testing, you should proabably delete any previously compiled
echo c++ code from python*_compiled and python*_intermediate in:
echo %TEMP%
echo or:
echo %TMP%
echo.
pause
