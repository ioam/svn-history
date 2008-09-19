Making a Windows installation package
=====================================

(1) First you need to be using a copy that has been set up to
    work under SVN. This means you have topographica-win\ inside
    the topographica\ directory, you have run setup.bat in the
    setup_cvs_copy\ directory, and you've checked it all works!

(2) You also need to have msys. topographica-win\ includes a 
    ready-made msys setup and instructions in the msys\ directory.
    (In this file, commands after a $ prompt are to be typed at
    an msys prompt, whereas those after a > prompt are for 
    a windows cmd.exe prompt. 

(3) A linux release should previously have been made (i.e. things
    such as release numbers are assumed to be correct)

(4) $ make distdir
    Then wait a long time.

(5) Change to the newly created distribution directory (e.g.
    ../distributions/topographica-0.9.5). Then:
    $ make distclean

(6) Open a windows command prompt and change to the 
    distribution directory. Then change to topographica-win\create_installer
    > prepare_for_installer.bat
    (Note that the last output of this script will be 'The system
    cannot find the path specified'; this is because the last line 
    deletes the script itself.)

(4) Delete the doc/ subdirectory and replace it with one where the 
    documentation has been compiled (I copy it over from a linux
    version, but you could complile the php files on Windows, good
    luck with that).  The doc directory should be cleaned up before it
    is copied in (i.e. take it from a distribution-ready copy of Topographica
    on linux).

(6) I use 'Inno Setup 5', an open-source installation package creator
    (see http://www.jrsoftware.org/isinfo.php).
    Move topographica.iss to anywhere outside the topographica directory, 
    then open it from the new location, adjust the
    paths marked *** to match those on your system, and finally choose
    'compile' from the 'build' menu. You should get a setup.exe file
    in a newly created 'Output' directory at the same level as topographica.iss.
