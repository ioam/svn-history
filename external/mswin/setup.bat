REM invoke as:
REM setup "c:\chris\topographica\"

REM to get weave, rename python242_topo_weave.tar.gz to python242_topo.tar.gz
REM to run topographica with weave, you need gcc somewhere in your path and
REM you need to edit some files:
REM
REM topo/misc/inlinec.py
REM change: 
REM  import weave
REM to:
REM  from scipy import weave
REM
REM topo/misc/commandline.py
REM change:
REM  exec "import weave" in __main__.__dict__
REM to:
REM  exec "from scipy import weave" in __main__.__dict__ 



if "%1"=="" goto end

util\gunzip -c python242_topo.tar.gz > python242_topo.tar
util\tar xvf python242_topo.tar
del /F python242_topo.tar
move /Y python242_topo ..\..\

..\..\python242_topo\python.exe setup.py %1

REM xcopy /E /I /Y topographica.py ..\..\

xcopy /E /I /Y topographica.bat ..\..\


:end