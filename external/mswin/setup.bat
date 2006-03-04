REM invoke as:
REM setup "c:\chris\topographica\"

if "%1"=="" goto end

util\gunzip -c python242_topo.tar.gz > python242_topo.tar
util\tar xvf python242_topo.tar
del /F python242_topo.tar
move /Y python242_topo ..\..\

..\..\python242_topo\python.exe setup.py %1

REM xcopy /E /I /Y topographica.py ..\..\

xcopy /E /I /Y topographica.bat ..\..\


:end