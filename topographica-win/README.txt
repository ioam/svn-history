********************************************
Files for setting up Topographica on Windows
********************************************

CEBHACKALERT: currently, Python cannot be built on Windows with a free
compiler. Until that changes, we have to use pre-built binaries. As
indicated in doc/Future_Work/current_work.html, we should eventually
be able to use pyMinGW.

This topographica-win module is therefore a little more complicated
than it would otherwise need to be. The way it works at the moment is
like this:


Creating python_topo/
====================

* This step need only be performed if we change Python version or
* update an external package (e.g. Numeric), and it is only performed
* by one developer: the result is committed to the repository.

A developer uses the script in create_python_topo/ to setup a copy of
Python plus all the extras (e.g. Numeric) needed for Topographica. The
binary version of Python that we get from python.org expects to be the
only copy of Python on the computer, and the extras will only install
into that one directory.

The result is a python_topo/ directory, containing all the files
necessary for Topographica. This is zipped up and put into the common/
subdirectory for use by the setup routines.


Setting up Topographica
=======================

Developers want a CVS-controlled copy of Topographica, whereas users
just require an installation program. Therefore, there are two further
subdirectories: create_installer/ and setup_cvs_copy/.

- Developers
After checking out topographica-win, Windows developers
run the setup script in setup_cvs_copy/. This makes their
copy of Topographica ready to run.

- Making an installation program
To make an installation program for distribution to users,
follow the instructions in create_installer/.





Files in the for_binaries/ subdirectory allow an installation package 
to be created for Topographica.

