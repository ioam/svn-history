@echo off

REM Assumes we're going to c:\Python25; be careful to update
REM everything if you decide to change this. (Should have used a
REM variable, but that can't cover the graphical installs)

set startdir=%CD%

REM ******************************************************************
REM Copy in packages that are commmon with topographica\external

REM numpy.diff
copy ..\..\external\numpy.diff .

REM Gnosis_Utils
..\util\gunzip -c ..\..\external\Gnosis_Utils-1.3.0-alpha-7.tar.gz > ..\..\external\Gnosis_Utils-1.3.0-alpha-7.tar
..\util\tar xvf ..\..\external\Gnosis_Utils-1.3.0-alpha-7.tar

REM Tile
copy ..\..\external\Tile.py .

REM scrodget
..\util\gunzip -c ..\..\external\pyscrodget-0.0.1_2.1.tar.gz > ..\..\external\pyscrodget-0.0.1_2.1.tar
..\util\tar xvf ..\..\external\pyscrodget-0.0.1_2.1.tar

REM snit
..\util\gunzip -c ..\..\external\snit-2.2.1.tar.gz > ..\..\external\snit-2.2.1.tar
..\util\tar xvf ..\..\external\snit-2.2.1.tar

REM tooltip
..\util\gunzip -c ..\..\external\tooltip-1.4.tar.gz > ..\..\external\tooltip-1.4.tar
..\util\tar xvf ..\..\external\tooltip-1.4.tar

REM ******************************************************************


REM CEBALERT: because of some path trouble in some of the installation
REM programs, we move to working in c:\create_python_topo
cd ..
xcopy /E /I create_python_topo c:\create_python_topo
xcopy /E /I util c:\create_python_topo\util
c:
cd \
cd create_python_topo


REM ******************************************************************
REM INSTALL PACKAGES

REM python jpeg pil numpy matplotlib weave fixedpoint pychecker common pylint epydoc docutils gnosis ipython gmpy tilewrapper scrodget tooltip

REM * python
start /w msiexec /i python-2.5.1.msi ALLUSERS=0 TARGETDIR=c:\python25 ADDLOCAL=DefaultFeature,TclTk

REM * jpeg
REM CEBALERT: included in PIL binary?

REM * PIL
start /w PIL-1.1.5.win32-py2.5.exe

REM * numpy
start /w numpy-1.1.1-win32-superpack-python2.5.exe
REM patch numpy
set storecpt=%cd%
cd c:\python25\Lib\site-packages
%storecpt%\util\patch.exe -p0 < %storecpt%\numpy.diff
cd %storecpt%

REM * matplotlib
start /w matplotlib-0.91.4.win32-py2.5.exe

REM * weave
REM (we just take it from scipy, since it's not available separately
REM as a binary)
start /w scipy-0.6.0.win32-py2.5.exe
xcopy /E /I c:\python25\Lib\site-packages\scipy\weave c:\python25\Lib\site-packages\weave

REM * fixedpoint
REM CEBALERT: should use the patch executable in utils to create the
REM patch from the diff and fixedpoint.tgz file in external\
move fixedpoint-0.1.2_patched.py c:\python25\Lib\site-packages\fixedpoint.py

REM CEBALERT: skipped: pychecker common pylint epydoc docutils

REM * gnosis
cd Gnosis_Utils-1.3.0-alpha-7\
c:\python25\python.exe setup.py install
REM CEBALERT: need to patch gnosis
cd ..

REM * ipython
start /w ipython-0.8.4.win32-setup.exe
REM CEBALERT: readline?

REM * gmpy 
REM CEBALERT: newer version than on linux
start /w gmpy-1.03-gmp-4.2.1.win32-py2.5.exe

REM * tilewrapper
move Tile.py c:\python25\Lib\site-packages\Tile.py

REM * scrodget
REM depends on snit
move snit-2.2.1 c:\python25\tcl\
cd pyscrodget-0.0.1_2.1\
c:\python25\python.exe setup.py install
cd ..

REM * tooltip
move tooltip-1.4 c:\python25\tcl\

REM * tile 0.8.2 (ADDITIONAL, until python 2.6 which has tk 8.5)
..\util\gunzip -c tile0.8.2.tar.gz > tile0.8.2.tar
..\util\tar xvf tile0.8.2.tar
move tile0.8.2 c:\python25\tcl\


REM ******************************************************************


REM ******************************************************************
REM install c compiler
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
REM ******************************************************************


rmdir /Q /S create_python_topo

echo.
echo.
echo Now test this has worked by moving c:\Python25 to your Topographica
echo directory (replacing the one already there). To be sure this copy 
echo works correctly, you should make sure any other copy of Topographica 
echo is uninstalled first (or try on a computer that does not have Python 
echo installed).
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
