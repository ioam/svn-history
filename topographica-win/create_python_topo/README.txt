$Id$

****************************************************
Create Topographica's python directory (python_topo)
****************************************************

Because we can't build Python with a free compiler, we use the binary
as distributed by python.org

This procedure sets up a copy of Python with all the external packages
necessary for Topographica. This copy of python is then archived for
distribution to Topographica users. Only if a package is upgraded or
added does someone need to go through this procedure.

Please note: it will trash any existing copy of python that you have
installed before (so not a python associated with topographica, but a
standalone one). It seems you can only have one copy of Python 2.4
installed at once.


(1) Run setup.bat. Accept all defaults (they're set programmatically)
    - changing any of the paths will break something. You only have to 
    click 'next' or 'finish' whenever prompted.

(2) As suggested by the script file, check that the new python_topo\
    directory works.

(3) If it does, turn it into a tar.gz file and commit to the repository
    (topographica-win\common\python_topo.tar.gz)


