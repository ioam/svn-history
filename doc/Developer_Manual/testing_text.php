<H1>Test suite</H1>

<P>Every Python module should have a corresponding unit test in
<CODE>tests/</CODE>.  The tests should be nearly exhaustive, in the
sense that it should be unlikely that a good-faith re-implementation
of the module would pass the tests but have significant
bugs. Obviously, truly exhaustive tests capable of detecting arbitrary
(e.g. deliberate) errors would be impractical.

<P>The default set of unit tests that are run must complete very
quickly, with no extraneous output, no GUI windows popping up, etc.,
<!--CEBALERT: should either remove the no-GUI statement (we have
xvfb-run), or should remove the basic GUI class tests from 'make tests')-->
because these tests are (and should be) run automatically many times
each day during active development.  All the output from such tests
must be checked automatically, with any output generated for the user
representing something the user really does have to do something
about.

<P>Additional more expensive tests, GUI tests, or those requiring user
input or user examination of the output are also encouraged, but all
these must be kept separate from the main automated regression tests.

<P>Note that, due to previous oversights, one cannot assume that any
existing file has a corresponding test file already.  Moreover,
existing test files should <i>not</i> be assumed to be exhaustive or
even particularly useful; they vary a lot in how comprehensive they
are.  So please always check the test file when coding, especially
when debugging, because it probably needs work too.

<h2>Unittests and Doctests</h2>

<P>Topographica's test suite supports test cases that use Python's <a href="http://docs.python.org/lib/module-unittest.html">unittest</a> module or its <a href="http://docs.python.org/lib/module-doctest.html">doctest</a> module.  Unittest provides a framework for writing test cases as objects containing a set of test methods plus common initialization and clean-up code.  This framework is useful for constructing heavy-duty tests, but can be cumbersome when only a simple set of correctness tests are required.  All unittests in modules with names matching the pattern <CODE>topo/tests/test*.py</CODE> can be automatically discovered and run by the topographica command <CODE>topo.tests.run()</CODE>

<P>Python's doctest module allows tests to be specified as a sequence of Python expressions to be evaluated, each followed by the expected result of the command.  The entire sequence should be formatted like a trace of an interactive python session.  For example:
<pre>
>>> def f(x):
...    return x+1
... 
>>> f(3)
4
>>> f(2)
3
>>> f('foo')
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
  File "<stdin>", line 2, in f
TypeError: cannot concatenate 'str' and 'int' objects
>>> 
</pre>
As long as each command produces the expected output (including any errors), the test passes.  See the <a href="http://docs.python.org/lib/module-doctest.html">doctest documentation</a> for details.

As with unittest testsuites, all doctest files with names matching <code>topo/tests/test*.txt</code> can be found and run automatically with the function <code>topo.tests.run()</code>.

<P>Important notes:
<ul>
<li> To construct a doctest file from an interactive topographica trace, the entire <code>topographica_tXXX</code> prefix must be removed from every line.  Lines with the prefix will be ignored.

<li> The testrunner used by <code>topo.tests.run()</code> will happily run an empty doctest file and report no errors (since there were no tests).  Make sure to manually check new or modified doctest files with <code>doctest.testfile(filename,verbose=True)</code> to make sure that the tests are actually being run before running <code>make tests</code> or <code>topo.tests.run()</code>.

<li> Topographica does not currently run doctests embedded in code documentation.
</ul>

<H2>Automatic testing</H2>

<P>Currently, topographica is periodically checked out, built, and
tested on Linux, OS X, and Windows (automatically, using <a
href="http://buildbot.net/">buildbot</a>).  The results of these
builds and tests can be seen at <a
href="http://buildbot.topographica.org/">buildbot.topographica.org</a>.

