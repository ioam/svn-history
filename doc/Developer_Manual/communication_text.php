<H1>Communication: code, documentation, and comments</H1>

<P>Writing Python code is similar to writing anything else: to do it
well, you need to keep your intended audience in mind.  There are
three different audiences for the different types of material in a
Python source file, and thus the guidelines for each category are
different:

<DL>
<DT>Program code: Communicating with the computer and the human reader</DT><DD>

     Program code tells the computer what to do, and needs to be
     written so that it is obvious to a human being what the computer
     is being told to do.  This means using class, variable, function,
     and function argument names that say exactly what they are, and
     favoring short, clear bits of code rather than long, convoluted
     logic.  For instance, any function longer than about a screenful
     should be broken up into more meaningful chunks that a human can
     understand.

<DT>Docstrings: Communicating with the user</DT><DD>

     Every file, class, function, and Parameter should have an
     appropriate docstring that says what that object does.  The first
     line of the docstring should be a brief summary that fits into 80
     columns.  If there are additional lines, there should be an
     intervening blank line, followed by this more detailed
     discussion.  For functions, the summary line should use the
     imperative voice, as in <CODE>"""Return the sum of all
     arguments."""</CODE>.  Such documentation is collected
     automatically for the online help and for the Reference manual,
     and must be written from the user's perspective.  I.e., the
     docstring must say how someone calling this function, class,
     etc. can use it, rather than having details about how it was
     implemented or its implementation history.

<DT>Comments: Communicating with the human reader</DT><DD>

     Comments (lines starting with #) are not processed by the
     computer, and are not visible to the user.  Thus comments should
     consist of things that you want to be visible to someone reading
     the file to really understand how something is implemented.
     Usually such a person will either be (a) trying to fix a bug, or
     (b) trying to add a new feature.  Thus the comments should be
     focused on what is needed for such readers.

     Please do not add redundant comments that simply describe what
     each statement does; the code itself documents that already.
     Redundant comments add more work for the reader, because they are
     usually out of date, and not necessarily accurate.  Instead,
     please use comments for things that are not obvious, such as the
     reason a particular approach was chosen, descriptions of things
     that would be nice to add but haven't been done yet, high-level
     explanations of a long section of low-level code, etc.  Do not
     include things relevant to the user; such things go into
     docstrings.
</DL>

<P>To summarize, please use code, docstrings, and comments
appropriately.  Any bit of information you add to a file should go
into the correct one of those three categories, and all files should
be written for all three of the different intended audiences.
