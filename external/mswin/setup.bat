@echo off
echo
echo Topographica installation script
echo

REM must be given a path
if "%1"=="" goto bad_arg

REM unzip and untar, leaving original gz file alone
util\gunzip -c python_topo.tar.gz > python_topo.tar
util\tar xvf python_topo.tar
del /F python_topo.tar

REM move the python stuff to the topographica directory
move /Y python_topo ..\..\

REM create startup scripts for topographica
..\..\python_topo\python.exe setup.py %1
goto end


:bad_arg
echo
echo Invoke as:
echo  setup path\to\topographica
echo
echo E.g. If you downloaded Topographica to c:\topographica, type:
echo  setup c:\topographica
echo

:end
echo