Making a Windows installation package
=====================================

(1) First you need to be using a copy that has been setup to
    work under CVS. This means you have run setup.bat in the
    Topographica root directory and can use Topographica.

(2) Run 'prepare_for_binaries.bat'
    - creates setup subdirectory in root topographica directory
    - deletes setup.bat from root topographica directory
    - copies this directory's setup.bat to setup/ subdirectory
    - cleans files that aren't needed for the binary version

(3) CEBHACKALERT: make sure release numbers are up to date in
    ..\setup.py and topographica.iss (the second is only for user's 
    information while installing).

(4) Copy topographica.iss to wherever you want to create the .exe
    file, then delete the external directory (which includes this file
    so remember the next step!).

(5) Delete the doc/ subdirectory and replace it with one where the 
    documentation has been compiled (I copy it over from a linux
    version, but you could complile the php files on Windows, good
    luck with that).

(6) I use 'Inno Setup 5', an open-source installation package creator.
    (See http://www.jrsoftware.org/isinfo.php)
    The script topographica.iss will create a .exe installation file;
    just choose 'compile' from the menu.