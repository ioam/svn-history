Topographica Unit Tests  Package

This packge contains unit test modules for topographica.  To run the
tests use the 'runtests' script in the main topographica directory.

To add new tests modules.

1. Add a module to this directory containing unit tests defined using
   Python's standard 'unittest' module.  Each test module should define
   a variable 'suite' containing the entire test suite for that module.

2. Edit the file __init__.py, adding an import line for your module.
   The package initialization code will take care of adding your
   module's test suite to the Topographica test suite.

Note that there need not be a 1-1 correspondence between test modules
and topographica modules.  For example, a special test module designed to
test the interaction between two topographica modules would be fine.