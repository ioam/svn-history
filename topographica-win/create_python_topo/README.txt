$Id$

****************************************************
Create Topographica's python directory (python_topo)
****************************************************

This procedure sets up a copy of Python with all the external packages
necessary for Topographica.

Please note: this will trash any existing copy of python that you have
installed before (so not a python associated with topographica, but a
standalone one). It seems you can only have one copy of Python 2.5
installed at once.


(1) Run setup.bat. Accept all defaults (they're set programmatically)
    - changing any of the paths will break something. You only have to 
    click 'next' or 'finish' whenever prompted.

(2) As suggested by the script file, check that the new python_topo\
    directory works. 

(3) Ensure python25.dll is present in python_topo\. If it's not (which
    seems to happen sometimes if the python installer detects your 
    system copy is the same as the one about to be installed), copy
    it in (from c:\windows\system32\).

(4) If the new python_topo\ works, turn it into a tar.gz file and 
    commit to the repository
    (topographica-win\common\python_topo.tar.gz)


