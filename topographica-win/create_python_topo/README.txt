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
 
(2) Ensure python25.dll is present in python_topo\. If it's not (which
seems to happen sometimes if the python installer detects your system
copy is the same as the one about to be installed), copy it in (from
c:\windows\system32\ or wherever).

(3) Check that the new collection of binaries works. Rename
c:\Python25 to c:\python_topo and move it to your topographica/
directory, replacing one that is already there if necessary.  To be a
little more sure this copy works correctly, you should make sure any
other copy of Topographica is uninstalled first. 

(4) Now you've checked that it works, run as many tests as you can!
This is done most easily by installing the msys environment (see
topographica-win/msys/README.txt). Set a DISPLAY:
$ export DISPLAY=:0
Then you can run:
$ make tests; make slow-tests
You can also run 
$ make gui-tests
But you're likely to get an error from python after the tests have
run. You should see that the tests ran correctly before python tried
to quit, though.

(5) If the new python_topo\ does indeed work, turn it into a tar.gz
file and commit to the repository
(topographica-win\common\python_topo.tar.gz)


