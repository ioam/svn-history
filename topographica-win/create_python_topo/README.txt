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


(1) Run setup.bat. Accept all defaults (they're set programmatically)
    - changing any of the paths will break something.

(2) As suggested by the script file, check that the new python_topo\
    directory works.

(3) If it does, turn it into a tar.gz file and commit to the repository
    (topographica-win\common\python_topo.tar.gz

