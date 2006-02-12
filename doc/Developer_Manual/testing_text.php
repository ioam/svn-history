<H1>Test suite</H1>

<P>Every Python module should have a corresponding unit test in
<CODE>tests/</CODE>.  The tests should be nearly exhaustive, in the
sense that it should be unlikely that a good-faith re-implementation
of the module would pass the tests but have significant
bugs. Obviously, truly exhaustive tests capable of detecting arbitrary
(e.g. deliberate) errors would be impractical.

<P>The default set of unit tests that are run must complete very
quickly, with no extraneous output, no GUI windows popping up, etc.,
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
