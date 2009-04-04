Making a Windows installation package
=====================================

(1) First you need to be using a copy that has been set up to
    work under SVN. This means you have already followed the
    instructions in topographica-win\setup_cvs_copy\README.txt

(2) You also need to have msys. topographica-win\ includes a 
    ready-made msys setup and instructions in the msys\ directory.
    (In this file, commands after a $ prompt are to be typed at
    an msys prompt, whereas those after a > prompt are for 
    a windows cmd.exe prompt. 

(3) A linux release should previously have been made (i.e. things
    such as release numbers are assumed to be correct)

(4) $ make distdir  # NOT 'make dist' as in linux!
    Then wait a long time.  

(5) Change to the newly created distribution directory (e.g.
    ../distributions/topographica-0.9.5). Then:
    $ make win-distclean

(6) Open a windows command prompt and change to the 
    distribution directory. Then change to topographica-win\create_installer
    > prepare_for_installer.bat
    (Note that the last output of this script will be 'The system
    cannot find the path specified'; this is because the last line 
    deletes the script itself.)

(4) Delete the doc/ subdirectory and replace it with one where the 
    documentation has been compiled (I copy doc/ over from the
    equivalent linux release, downloaded from sf.net, but you could
    complile the php files on Windows, good luck with that).

(6) I use 'Inno Setup 5', an open-source installation package creator
    (see http://www.jrsoftware.org/isinfo.php).
    Move topographica.iss to anywhere outside the topographica directory, 
    then open it from the new location, and follow the instructions at the top of the file.


