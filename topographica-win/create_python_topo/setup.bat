@echo off
REM assumes we're going to c:\Python24

set startdir=%CD%

..\util\gunzip -c ..\..\external\Pmw.tgz > ..\..\external\Pmw.tar
..\util\tar xvf ..\..\external\Pmw.tar
copy ..\..\external\Pmw .

cd ..
xcopy /E /I create_python_topo c:\create_python_topo
REM CEBHACKALERT: because the msi won't run from this directory, at least
REM on my PC! Why? Is it a path problem?
c:
cd create_python_topo


start /w msiexec /i python-2.4.2.msi ALLUSERS=0 TARGETDIR=c:\python24 ADDLOCAL=DefaultFeature,TclTk
start /w Numeric-24.2.win32-py2.4.exe
start /w matplotlib-0.81.win32-py2.4.exe
start /w PIL-1.1.5.win32-py2.4.exe

xcopy /E /I Pmw c:\python24\Lib\site-packages\

REM ** For fixedpoint, the patched version from unix is used.
copy fixedpoint-0.1.2_patched.py c:\python24\Lib\site-packages\fixedpoint.py

cd ..
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
