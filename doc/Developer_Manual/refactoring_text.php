<H1>Refactoring/testing tips</H1>

<P>This list of "soundbites" comes from Fowler 1999, <A
HREF="http://www.amazon.co.uk/exec/obidos/ASIN/0201485672/">Refactoring:
Improving the Design of Existing Code</A>, pp. 417-418).  It seems to
apply reasonably well to this project, particularly the parts about
testing.

<UL>
<LI>Page 7: When you find you have to add a feature to a program, and the
program's code is not structured in a convenient way to add the
feature, first refactor the program to make it easy to add the
feature, then add the feature.

<LI>Page 8: Before you start refactoring, check that you have a solid
suite of tests.  These tests must be self-checking.

<LI>Page 13: Refactoring changes the programs in small steps.  If you make
a mistake, it is easy to find the bug.

<LI>Page 15: Any fool can write code that a computer can understand. Good
programmers write code that humans can understand.

<LI>Page 53: Refactoring (noun): a change made to the internal structure of
software to make it easier to understand and cheaper to modify without
changing the observable behavior of the software.

<LI>Page 43: Refactor (verb): to restructure software by applying a series
of refactorings without changing the observable behavior of the
software.

<LI>Page 58: Three strikes and you refactor.

<LI>Page 65: Don't publish interfaces prematurely.  Modify your code
ownership policies to smooth refactoring.

<LI>Page 88: When you feel the need to write a comment, first try to
refactor the code so that any comment becomes superfluous.

<LI>Page 90: Make sure all tests are fully automatic and that they check
their own results.

<LI>Page 90: A suite of tests is a powerful bug detector that decapitates
the time it takes to find bugs.

<LI>Page 94: Run your tests frequently.  Localize tests whenever you
compile --- every test at least every day.

<LI>Page 97: When you get a bug report, start by writing a unit test that
exposes the bug.

<LI>Page 98: It is better to write and run incomplete tests than not to
run complete tests.

<LI>Page 99: Think of the boundary conditions under which things might go
wrong and concentrate your tests there.

<LI>Page 100: Don't forget to test that exceptions are raised when things
are expected to go wrong.

<LI>Page 101: Don't let the fear that testing can't catch all bugs stop
you from writing the tests that will catch most bugs.
</ul>


